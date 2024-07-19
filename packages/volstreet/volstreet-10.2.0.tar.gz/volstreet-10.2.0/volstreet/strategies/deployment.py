import json
import inspect
from threading import Thread
from time import sleep
from typing import Optional
import os
from multiprocessing import Manager
import numpy as np
import boto3
from volstreet.config import logger
from volstreet.utils.core import current_time
from volstreet.utils.change_config import (
    set_notifier_level,
    set_error_notification_settings,
)
from volstreet import config
from volstreet.angel_interface.login import login, wait_for_login
from volstreet.angel_interface.interface import (
    LiveFeeds,
    fetch_book,
    lookup_and_return,
    modify_order,
    update_order_params,
    fetch_quotes,
    DataException,
)
from volstreet.angel_interface.active_session import ActiveSession

# noinspection PyUnresolvedReferences
from volstreet.strategies.strategy_classes import (
    BaseStrategy,
    OvernightStraddle,
    TrendV2,
    BiweeklyStraddle,
    BuyHedge,
    IntradayStrangle,
    DeltaHedgedStrangle,
    ReentryStraddle,
    QuickStrangle,
)


class Client:

    def __init__(
        self,
        user: str,
        pin: str,
        apikey: str,
        authkey: str,
        name: str = None,
        whatsapp: str = None,
        error_url: str = None,
        config_mode: str = "s3",
        webhook_url: str = None,
    ):
        self.user = user
        self.pin = pin
        self.apikey = apikey
        self.authkey = authkey
        self.webhook_url = webhook_url
        self.name = name
        self.strategies = []
        self.session_terminated: bool = False
        self.whatsapp = whatsapp
        self.error_url = error_url
        self.config_mode = config_mode

    @classmethod
    def from_name(cls, client: str, **kwargs) -> "Client":
        try:
            user = __import__("os").environ[f"{client}_USER"]
            pin = __import__("os").environ[f"{client}_PIN"]
            apikey = __import__("os").environ[f"{client}_API_KEY"]
            authkey = __import__("os").environ[f"{client}_AUTHKEY"]
        except KeyError:
            raise KeyError(
                f"Environment variables for {client} not found. Please check if the environment variables are set."
            )

        error_url = os.getenv(f"{client}_ERROR_URL", os.getenv("ERROR_URL", None))
        whatsapp = os.getenv(f"{client}_WHATSAPP", None)
        webhook_url = os.getenv(f"{client}_WEBHOOK_URL", None)
        return cls(
            user=user,
            pin=pin,
            apikey=apikey,
            authkey=authkey,
            name=client,
            whatsapp=whatsapp,
            error_url=error_url,
            webhook_url=webhook_url,
            **kwargs,
        )

    def login(self) -> None:
        login(self.user, self.pin, self.apikey, self.authkey, self.webhook_url)
        set_error_notification_settings("url", self.error_url)
        set_error_notification_settings("whatsapp", self.whatsapp)

    def terminate(self) -> None:
        self.session_terminated = True
        LiveFeeds.close()
        ActiveSession.obj.terminateSession(self.user)

    def load_config_from_s3(self) -> list[dict]:
        try:
            s3 = boto3.client("s3", region_name="ap-south-1")
            client_info = json.loads(
                s3.get_object(
                    Bucket="userstrategies", Key=f"{self.name.lower()}/strategies.json"
                )["Body"]
                .read()
                .decode("utf-8")
            )
            return client_info
        except Exception as e:
            logger.error(f"Error in loading strategies for client {self.name}: {e}")
            raise e

    def load_strats(self) -> None:
        if self.config_mode == "s3":
            client_info = self.load_config_from_s3()
        else:
            with open("client_config.json", "r") as f:
                config_data = json.load(f)
            client_info = config_data[self.name]

        for strategy_data in client_info:

            strategy_class = eval(strategy := strategy_data["type"])
            webhook_url = os.getenv(
                f"{self.name}_WEBHOOK_URL_{strategy.upper()}", self.webhook_url
            )
            strategy = strategy_class(
                **strategy_data["init_params"], webhook_url=webhook_url
            )
            self.strategies.append(strategy)

    @wait_for_login
    def continuously_handle_open_orders(self):
        while not self.session_terminated:
            try:
                order_book = fetch_book("orderbook", from_api=True)
                if not order_book:
                    continue
                open_orders = get_open_orders(order_book, statuses=["open"])

                if open_orders.size > 0:
                    order_descriptions = [
                        {
                            "id": order["orderid"],
                            "symbol": order["tradingsymbol"],
                            "price": order["price"],
                        }
                        for order in open_orders
                    ]
                    logger.info(
                        f"Modifying open orders {order_descriptions} "
                        f"at {current_time()}"
                    )
                    modify_orders(open_orders)
            except Exception as e:
                logger.error(f"Error in continuously handling open orders: {e}")
            # In Python, the "finally" block is guaranteed to be executed regardless of how the try block is exited.
            # This includes situations where the try block is exited due to a return, break, or continue statement,
            # or even if an exception is raised. Hence, the lock gets released in the "finally" block.
            finally:
                sleep(3)


def run_client(
    client: Client,
    websockets: bool = True,
    price_socket_manager: Manager = None,
    order_socket_manager: Manager = None,
    notifier_level="INFO",
) -> None:
    # Setting notification settings
    set_notifier_level(notifier_level)
    client.login()

    # Load strategies
    client.load_strats()
    logger.info(
        f"Client {client.name} logged in successfully. Starting strategies with the following settings:\n"
        f"Notifier level: {config.NOTIFIER_LEVEL}\n"
        f"Error notification settings: {config.ERROR_NOTIFICATION_SETTINGS}"
    )

    # Wait for market to open
    start_time = current_time().replace(hour=9, minute=14, second=1)
    seconds_to_start = (start_time - current_time()).total_seconds()
    sleep(max(seconds_to_start, 0))

    # Starting order modification thread
    logger.info(
        f"Starting open orders handler in client {client.name} at {current_time()}..."
    )
    Thread(target=client.continuously_handle_open_orders).start()

    if websockets:
        # Starting live feeds
        logger.info(
            f"Starting live feeds in client {client.name} at {current_time()}..."
        )
        LiveFeeds.start_price_feed(price_socket_manager)
        LiveFeeds.start_order_feed(order_socket_manager)

    # Starting strategies
    strategy_threads = [
        Thread(target=strategy.run_all) for strategy in client.strategies
    ]
    logger.info(f"Starting strategies in client {client.name} at {current_time()}")
    for strategy in strategy_threads:
        strategy.start()

    for strategy in strategy_threads:
        strategy.join()


def get_open_orders(
    order_book: list,
    order_ids: list[str] | tuple[str] | np.ndarray[str] = None,
    statuses: list[str] | tuple[str] | np.ndarray[str] = None,
):
    """Returns a list of open order ids. If order_ids is provided,
    it will return open orders only for those order ids. Otherwise,
    it will return all open orders where the ordertag is not empty.
    """
    if order_ids is None:
        order_ids = [
            order["orderid"] for order in order_book if order["ordertag"] != ""
        ]
    if statuses is None:
        statuses = ["open", "open pending", "modified", "modify pending"]
    open_orders_with_params: np.ndarray[dict] = lookup_and_return(
        order_book,
        ["orderid", "status"],
        [order_ids, statuses],
        config.modification_fields,
    )
    return open_orders_with_params


def modify_orders(open_orders_params: list[dict] | np.ndarray[dict]):
    quotes = fetch_quotes(
        [order["symboltoken"] for order in open_orders_params],
        structure="dict",
        from_source=True,
    )

    for order in open_orders_params:
        quote_data = quotes[order["symboltoken"]]
        modified_params = update_order_params(order, quote_data)

        try:
            modify_order(modified_params)
        except Exception as e:
            if isinstance(e, DataException):
                logger.error(f"Error in modifying order: {e}")
                sleep(1)


def add_env_vars_for_client(
    name: str,
    user: str,
    pin: str,
    api_key: str,
    auth_key: str,
    webhook_url: Optional[str] = None,
):
    # Specify the variable name and value
    var_dict = {
        f"{name}_USER": user,
        f"{name}_PIN": pin,
        f"{name}_API_KEY": api_key,
        f"{name}_AUTHKEY": auth_key,
    }

    if webhook_url is not None:
        var_dict[f"{name}_WEBHOOK_URL"] = webhook_url

    # Use the os.system method to set the system-wide environment variable
    for var_name, var_value in var_dict.items():
        os.system(f"setx {var_name} {var_value}")


def prepare_default_strategy_params(
    strategy_name: str,
    as_string: bool = False,
):
    init_params = get_default_params(BaseStrategy)
    strategy_params = get_default_params(eval(strategy_name))
    strategy_params.pop("strategy_tag", None)
    init_params["parameters"] = strategy_params
    if as_string:
        return json.dumps(init_params)
    return init_params


def modify_strategy_params(
    client_config_data, client_name, strategy_name, init_params=None
):
    """
    Update the init_params of a specific strategy for a specific client in the given JSON data.
    Adds the client and/or strategy if they don't exist.

    Parameters:
    - json_data (dict): The original JSON data as a Python dictionary.
    - client_name (str): The name of the client to update.
    - strategy_name (str): The name of the strategy to update.
    - new_init_params (dict): The new init_params to set.

    Returns:
    - bool: True if the update/addition was successful, False otherwise.
    """

    if init_params is None:
        init_params = get_default_params(eval(strategy_name))

    # Search for the strategy for the client
    for strategy in client_config_data:
        if strategy["type"] == strategy_name:
            # Update the init_params
            strategy["init_params"].update(init_params)
            logger.info(f"Updated {strategy_name} for {client_name}.")
            return True

    # If strategy not found, add it
    logger.info(
        f"Strategy {strategy_name} not found for client {client_name}. Adding new strategy."
    )
    new_strategy = {"type": strategy_name, "init_params": init_params}
    client_config_data[client_name]["strategies"].append(new_strategy)

    return True


def get_default_params(obj, as_string=False):
    """
    Given a function, it returns a dictionary containing all the default
    keyword arguments and their values.
    """
    signature = inspect.signature(obj)
    params = {
        k: v.default if v.default is not inspect.Parameter.empty else None
        for k, v in signature.parameters.items()
    }
    # Remove the 'underlying' parameter if it exists
    params.pop("underlying", None)
    if as_string:
        return json.dumps(params)
    return params
