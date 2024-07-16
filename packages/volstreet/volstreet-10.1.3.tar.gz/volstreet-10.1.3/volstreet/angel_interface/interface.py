import numpy as np
from collections import defaultdict
from time import sleep
import functools
from datetime import datetime
import pandas as pd
from typing import Callable
from volstreet.exceptions import APIFetchError
from volstreet import config
from volstreet.config import logger, token_exchange_dict
from volstreet.decorators import (
    timeit,
)
from volstreet.utils import (
    custom_round,
    generate_cache_key_from_signature,
    current_time,
)
from volstreet.angel_interface.active_session import ActiveSession
from volstreet.angel_interface.smart_connect import DataException
from volstreet.angel_interface.access_rate_handler import (
    access_rate_handler,
    limiter_1,
    limiter_10,
    limiter_20,
    quote_limiter,
)
from volstreet.angel_interface.live_feeds import LiveFeeds
from volstreet.angel_interface.tools import format_quote_response


order_param_fields = [
    "tradingsymbol",
    "symboltoken",
    "transactiontype",
    "variety",
    "exchange",
    "producttype",
    "duration",
    "quantity",
    "ordertag",
    "ordertype",
    "price",
]


def timed_cacher(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not config.CACHING:
            return func(*args, **kwargs)
        key = generate_cache_key_from_signature(func, *args, **kwargs)
        if (
            key not in cache
            or (current_time() - cache[key]["time"]).seconds > config.CACHE_INTERVAL
        ):
            result = func(*args, **kwargs)
            time = current_time()
            cache[key] = {"result": result, "time": time}
            return result
        else:
            return cache[key]["result"]

    return wrapper


def retry_angel_api(
    data_type: str | Callable = None,
    max_attempts: int = 10,
    wait_increase_factor: float = 1.1,
):
    def handle_retry_logic(
        attempt: int,
        exception: Exception,
        msg: str,
        additional_msg: str,
    ) -> None:
        if ActiveSession.obj is None:
            raise Exception("Not logged in.")
        if (
            isinstance(exception, ValueError) and "Invalid book type" in str(exception)
        ) or (attempt == max_attempts):
            logger.error(f"{msg}. Additional info: {additional_msg}")
            if not isinstance(exception, DataException) and not isinstance(
                exception, ValueError
            ):
                raise APIFetchError(msg)
            else:
                raise exception

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sleep_duration = 1
            data = {}
            for attempt in range(1, max_attempts + 1):
                try:
                    data = func(*args, **kwargs)
                    if callable(data_type):
                        return data_type(data)
                    if data_type == "ltp":
                        return data["data"]["ltp"]
                    return data["data"]

                except Exception as e:
                    function = func.__name__
                    msg = f"Attempt {attempt}: Error in function {function}: {e}"
                    additional_msg = (
                        data.get("message", "No additional message available")
                        if isinstance(data, dict)
                        else ""
                    )
                    handle_retry_logic(
                        attempt,
                        e,
                        msg,
                        additional_msg,
                    )
                    sleep_duration *= wait_increase_factor
                    logger.info(
                        f"{msg}. Additional info: {additional_msg}. Retrying in {sleep_duration} seconds."
                    )
                    sleep(sleep_duration)

        return wrapper

    return decorator


if config.backtest_mode:
    from volstreet.backtests.proxy_functions import ProxyFeeds as LiveFeeds
    from volstreet.backtests.proxy_functions import retry_angel_api, access_rate_handler


def generate_order_params(
    symbol: str,
    token: str,
    qty: int,
    action: str,
    price: float | int | str,
    order_tag: str = "",
    stop_loss_order: bool = False,
) -> dict:
    """Price can be a str or a float because "market" is an acceptable value for price."""
    action = action.upper()
    order_tag = (
        "Automated Order" if (order_tag == "" or order_tag is None) else order_tag
    )
    exchange = token_exchange_dict[token]
    params = {
        "tradingsymbol": symbol,
        "symboltoken": token,
        "transactiontype": action,
        "exchange": exchange,
        "producttype": "CARRYFORWARD",
        "duration": "DAY",
        "quantity": int(qty),
        "ordertag": order_tag,
    }

    if stop_loss_order:
        execution_price = (
            price * 1.1
        )  # Hardcoded 10% buffer for execution price in sl orders
        params.update(
            {
                "variety": "STOPLOSS",
                "ordertype": "STOPLOSS_LIMIT",
                "triggerprice": round(price, 1),
                "price": round(execution_price, 1),
            }
        )
    else:
        order_type, execution_price = (
            ("MARKET", 0) if price == "MARKET" else ("LIMIT", price)
        )
        if order_type == "LIMIT":
            execution_price = max(custom_round(execution_price), 0.05)
        params.update(
            {
                "variety": "NORMAL",
                "ordertype": order_type,
                "price": execution_price,
            }
        )

    return params


def update_order_params(
    current_params: dict, quote_data: dict, additional_buffer: float = 0
) -> dict:
    """Additional buffer is a percentage value that can further modify the price of the order.
    Additional buffer can be used when iteratively modifying orders to speed up the execution of persistently
    open orders."""

    action = current_params["transactiontype"]
    target_price = "best_bid" if action == "SELL" else "best_ask"
    market_price = quote_data[target_price]
    modifier = (
        (1 + config.LIMIT_PRICE_BUFFER + additional_buffer)
        if action == "BUY"
        else (1 - config.LIMIT_PRICE_BUFFER - additional_buffer)
    )

    new_price = market_price * modifier
    new_price = max(0.05, new_price)
    new_price = custom_round(new_price)

    modified_params = current_params.copy()
    modified_params["price"] = new_price
    current_params["price"] = new_price
    modified_params.pop("status")

    return modified_params


@retry_angel_api(data_type=lambda x: x)
@access_rate_handler(limiter_20, "place_order", False)
@timeit()
def _place_order_params(params: dict) -> str:
    return ActiveSession.obj.placeOrder(params)


def place_order(
    symbol: str,
    token: str,
    qty: int,
    action: str,
    price: str | float | int,
    order_tag: str = "",
    stop_loss_order: bool = False,
) -> str:
    params = generate_order_params(
        symbol, token, qty, action, price, order_tag, stop_loss_order
    )
    return _place_order_params(params)


@retry_angel_api(data_type=lambda x: None)
@access_rate_handler(limiter_20, "modify_order", False)
@timeit()
def modify_order(params: dict) -> None:
    return ActiveSession.obj.modifyOrder(params)


@retry_angel_api(data_type=lambda x: x["data"]["fetched"])
@access_rate_handler(quote_limiter, "get_quotes", False)
@timeit()
def _fetch_quotes_slice(tokens: list, mode: str = "FULL") -> list[dict]:
    payload = defaultdict(list)
    for token in tokens:
        exchange = token_exchange_dict.get(token)
        if exchange:
            payload[exchange].append(token)
    payload = dict(payload)
    return ActiveSession.obj.getMarketData(mode, payload)


def _fetch_quotes(tokens: list, mode: str = "FULL") -> list[dict]:
    max_tokens_per_request = 50
    if len(tokens) <= max_tokens_per_request:
        return _fetch_quotes_slice(tokens, mode)
    else:
        quote_data = []
        for i in range(0, len(tokens), max_tokens_per_request):
            quote_data.extend(
                _fetch_quotes_slice(tokens[i : i + max_tokens_per_request], mode)
            )
        return quote_data


def fetch_quotes(
    tokens: list | set,
    mode: str = "FULL",
    structure: str = "list",
    from_source: bool = False,
):
    if (
        not from_source
        and LiveFeeds.price_feed_connected()
        and all([token in LiveFeeds.price_feed.data_bank for token in tokens])
    ):
        quote_data = [LiveFeeds.price_feed.data_bank[token] for token in tokens]
    else:
        quote_data = _fetch_quotes(tokens, mode)
        quote_data = format_quote_response(quote_data)

    if structure.lower() == "dict":
        return {entry["token"]: entry for entry in quote_data}
    elif structure.lower() == "list":
        return quote_data
    else:
        raise ValueError(f"Invalid structure '{structure}'.")


@timed_cacher
@retry_angel_api(data_type="ltp")
@access_rate_handler(limiter_10, "get_ltp", False)
@timeit()
def _fetch_ltp(exchange_seg, symbol, token):
    price_data = ActiveSession.obj.ltpData(exchange_seg, symbol, token)
    return price_data


def fetch_ltp(exchange_seg, symbol, token, field="ltp"):
    if LiveFeeds.price_feed_connected() and token in LiveFeeds.price_feed.data_bank:
        data_bank = LiveFeeds.price_feed.data_bank
    elif LiveFeeds.back_up_feed and token in LiveFeeds.back_up_feed:
        data_bank = LiveFeeds.back_up_feed
    else:
        return _fetch_ltp(exchange_seg, symbol, token)
    return data_bank[token][field]


@retry_angel_api(max_attempts=10)
@access_rate_handler(limiter_1, "get_orderbook", False)
@timeit()
def _fetch_book(fetch_func):
    data = fetch_func()
    return data


def fetch_book(book: str, from_api: bool = False) -> list:
    if book == "orderbook":
        if LiveFeeds.order_feed_connected() and not from_api:
            return LiveFeeds.order_book
        return _fetch_book(ActiveSession.obj.orderBook)
    elif book in {"positions", "position"}:
        return _fetch_book(ActiveSession.obj.position)
    else:
        raise ValueError(f"Invalid book type '{book}'.")


def lookup_and_return(
    book, field_to_lookup, value_to_lookup, field_to_return=None
) -> np.ndarray | dict:
    def filter_and_return(data: list):
        if not isinstance(field_to_lookup, (list, tuple, np.ndarray)):
            field_to_lookup_ = [field_to_lookup]
            value_to_lookup_ = [value_to_lookup]
        else:
            field_to_lookup_ = field_to_lookup
            value_to_lookup_ = value_to_lookup

        if field_to_return is None:  # Return the entire entry
            return np.array(
                [
                    entry
                    for entry in data
                    if all(
                        (
                            entry[field] == value
                            if not isinstance(value, (list, tuple, np.ndarray))
                            else entry[field] in value
                        )
                        for field, value in zip(field_to_lookup_, value_to_lookup_)
                    )
                    and all(entry[field] != "" for field in field_to_lookup_)
                ]
            )

        elif isinstance(
            field_to_return, (list, tuple, np.ndarray)
        ):  # multiple fields are requested
            bucket = []
            for entry in data:
                if all(
                    (
                        entry[field] == value
                        if not isinstance(value, (list, tuple, np.ndarray))
                        else entry[field] in value
                    )
                    for field, value in zip(field_to_lookup_, value_to_lookup_)
                ) and all(entry[field] != "" for field in field_to_lookup_):
                    bucket.append({field: entry[field] for field in field_to_return})
            if len(bucket) == 0:
                return np.array([])
            else:
                return np.array(bucket)
        else:  # Return a numpy array as only one field is requested
            # Check if 'orderid' is in field_to_lookup_
            if "orderid" in field_to_lookup_:
                sort_by_orderid = True
                orderid_index = field_to_lookup_.index("orderid")
            else:
                sort_by_orderid = False
                orderid_index = None

            bucket = [
                (
                    (entry["orderid"], entry[field_to_return])
                    if sort_by_orderid
                    else entry[field_to_return]
                )
                for entry in data
                if all(
                    (
                        entry[field] == value
                        if not isinstance(value, (list, tuple, np.ndarray))
                        else entry[field] in value
                    )
                    for field, value in zip(field_to_lookup_, value_to_lookup_)
                )
                and all(entry[field] != "" for field in field_to_lookup_)
            ]

            if len(bucket) == 0:
                return np.array([])
            else:
                if sort_by_orderid:
                    # Create a dict mapping order ids to their index in value_to_lookup
                    orderid_to_index = {
                        value: index
                        for index, value in enumerate(value_to_lookup_[orderid_index])
                    }
                    # Sort the bucket based on the order of 'orderid' in value_to_lookup
                    bucket.sort(key=lambda x: orderid_to_index[x[0]])
                    # Return only the field_to_return values
                    return np.array([x[1] for x in bucket])
                else:
                    return np.array(bucket)

    if not (
        isinstance(field_to_lookup, (str, list, tuple, np.ndarray))
        and isinstance(value_to_lookup, (str, list, tuple, np.ndarray))
    ):
        raise ValueError(
            "Both 'field_to_lookup' and 'value_to_lookup' must be strings or lists."
        )

    if isinstance(field_to_lookup, list) and isinstance(value_to_lookup, str):
        raise ValueError(
            "Unsupported input: 'field_to_lookup' is a list and 'value_to_lookup' is a string."
        )

    if isinstance(book, list):
        return filter_and_return(book)
    elif isinstance(book, str) and book in {"orderbook", "positions"}:
        book_data = fetch_book(book)
        return filter_and_return(book_data)
    else:
        logger.error(f"Invalid book type '{book}'.")
        raise ValueError("Invalid book type.")


@retry_angel_api()
@access_rate_handler(limiter_1, "get_historical_data", False)
def fetch_historical_prices(
    token: str, interval: str, from_date: datetime, to_date: datetime
):
    from_date = pd.to_datetime(from_date) if isinstance(from_date, str) else from_date
    to_date = pd.to_datetime(to_date) if isinstance(to_date, str) else to_date
    exchange = token_exchange_dict[token]
    historic_param = {
        "exchange": exchange,
        "symboltoken": token,
        "interval": interval,
        "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
        "todate": to_date.strftime("%Y-%m-%d %H:%M"),
    }
    return ActiveSession.obj.getCandleData(historic_param)
