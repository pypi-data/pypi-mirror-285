from itertools import groupby
import asyncio
import threading
import numpy as np
import itertools
from time import sleep
from volstreet import config
from volstreet.decorators import timeit
from volstreet.utils.core import time_to_expiry
from volstreet.utils.communication import log_error, notifier
from volstreet.config import logger
from volstreet.angel_interface.active_session import ActiveSession
from volstreet.angel_interface.interface import (
    update_order_params,
    lookup_and_return,
    fetch_quotes,
    fetch_book,
)
from volstreet.angel_interface.async_interface import (
    get_quotes_async,
    get_ltp_async,
    place_order_async,
    modify_order_async,
    unique_order_status_async,
)
from volstreet.trade_interface.instruments import (
    Option,
    Strangle,
    Straddle,
    SyntheticFuture,
    Action,
)


@log_error()
def cancel_pending_orders(order_ids, variety="STOPLOSS"):
    if isinstance(order_ids, (list, np.ndarray)):
        for order_id in order_ids:
            ActiveSession.obj.cancelOrder(order_id, variety)
    else:
        ActiveSession.obj.cancelOrder(order_ids, variety)


async def place_orders(list_of_orders: list[dict], session=None) -> list[str]:
    """Designed to be used for a specific action type.
    For example, all orders are BUY orders.
    """
    order_coros = [
        place_order_async(order, session=session) for order in list_of_orders
    ]
    results = await asyncio.gather(*order_coros)
    unique_ids = [result["uniqueorderid"] for result in results]
    return unique_ids


async def fetch_statuses(list_of_unique_ids: list[str], session=None) -> list[dict]:
    status_coros = [
        unique_order_status_async(unique_id, session=session)
        for unique_id in list_of_unique_ids
    ]
    # noinspection PyTypeChecker
    return await asyncio.gather(*status_coros)


async def modify_open_orders(
    open_orders: list[dict], quotes: dict, additional_buffer: float = 0, session=None
):
    modified_params = [
        update_order_params(order, quotes[order["symboltoken"]], additional_buffer)
        for order in open_orders
    ]
    modify_coros = [modify_order_async(params, session) for params in modified_params]
    await asyncio.gather(*modify_coros)


def check_for_rejection(statuses: list[dict]):
    if any(status["status"] == "rejected" for status in statuses):
        notifier(
            f"One or more orders were rejected in batch: {statuses}",
            config.ERROR_NOTIFICATION_SETTINGS["url"],
            "ERROR",
            send_whatsapp=True,
        )
        raise Exception("One or more orders were rejected in batch.")


def filter_for_open_orders(statuses: list[dict]) -> list[dict]:
    open_order_statuses = ["open", "open pending", "modified", "modify pending", ""]
    open_orders = [
        status for status in statuses if status["status"] in open_order_statuses
    ]
    if not open_orders:
        return []
    open_orders_formatted = [
        {field: status[field] for field in config.modification_fields}
        for status in open_orders
    ]
    return open_orders_formatted


def calculate_average_price(orders: list, ids: list[str]) -> float:
    avg_prices = lookup_and_return(
        orders, ["uniqueorderid", "status"], [ids, "complete"], "averageprice"
    )
    return avg_prices.astype(float).mean() if avg_prices.size > 0 else np.nan


async def execute_orders_per_symbol(
    orders: list[dict], symbol: str, session=None
) -> float:
    """
    Used to execute orders for a particular action type and symbol token.
    Executes orders in a loop until all orders are executed.
    Or max iterations are reached.
    Returns the average price of all executed orders.
    """
    if session is None:
        async with ActiveSession.obj.async_session() as session:
            return await execute_orders_per_symbol(orders, symbol, session)

    order_ids = await place_orders(orders, session)
    await asyncio.sleep(0.25)
    statuses = await fetch_statuses(order_ids, session)
    check_for_rejection(statuses)
    open_orders = filter_for_open_orders(statuses)

    iteration = 1
    while open_orders:
        if iteration == 3:
            notifier(
                f"Max modification iterations reached for symbol {symbol}.",
                config.ERROR_NOTIFICATION_SETTINGS["url"],
                "ERROR",
            )
            token = orders[0]["symboltoken"]  # All orders have the same symbol token
            return await get_ltp_async(token, session)
        additional_buffer = iteration / 100
        quotes = await get_quotes_async(
            [order["symboltoken"] for order in open_orders], session=session
        )
        await modify_open_orders(open_orders, quotes, additional_buffer, session)
        await asyncio.sleep(0.25)
        statuses = await fetch_statuses(order_ids, session)
        check_for_rejection(statuses)
        open_orders = filter_for_open_orders(statuses)
        iteration += 1

    logger.info(f"Orders successfully executed for symbol {symbol}.")

    avg_price = calculate_average_price(statuses, order_ids)
    return avg_price


async def execute_orders(orders: list[dict]) -> dict:
    """The difference between this function and execute_order_per_symbol is that this function
    can take in orders of different action types and symbols. It groups the orders
    into transaction types and symbol tokens and executes them in parallel, prioritizing
    buy orders to be executed first.
    """
    master_dict = {}
    orders.sort(key=lambda x: x["transactiontype"])
    orders_grouped_by_action = groupby(orders, key=lambda x: x["transactiontype"])

    async with ActiveSession.obj.async_session() as session:
        for action, orders_per_action in orders_grouped_by_action:
            orders_per_action = list(orders_per_action)
            orders_per_action.sort(key=lambda x: x["tradingsymbol"])
            orders_grouped_by_symbol = groupby(
                orders_per_action, key=lambda x: x["tradingsymbol"]
            )
            orders_grouped_by_symbol = {
                symbol: list(orders_per_symbol)
                for symbol, orders_per_symbol in orders_grouped_by_symbol
            }  # Just converting it to a dict
            order_tasks = [
                execute_orders_per_symbol([*orders], symbol, session)
                for symbol, orders in orders_grouped_by_symbol.items()
            ]
            avg_prices = await asyncio.gather(*order_tasks)

            for symbol, avg_price in zip(orders_grouped_by_symbol.keys(), avg_prices):
                # IMPORTANT: If orders contained buy and sell both for a single token
                # then this will overwrite the avg_price for that token with the sell avg_price
                # This is a limitation of the current implementation. It will be fixed in the future.
                master_dict[symbol] = avg_price

    return master_dict


def generate_bulk_params(
    instructions: dict[Option | Strangle | Straddle | SyntheticFuture, dict]
) -> list[dict]:

    def fetch_market_depth(instruments):
        option_tokens = {
            instrument.token
            for instrument in instruments
            if isinstance(instrument, Option)
        }
        strangle_tokens = {
            token
            for instrument in instruments
            if isinstance(instrument, (Strangle, Straddle, SyntheticFuture))
            for token in (instrument.call_token, instrument.put_token)
        }
        tokens = option_tokens | strangle_tokens
        return fetch_quotes(tokens, structure="dict", from_source=False)

    order_params = []

    # If price is present in all the instructions, then we can directly use that

    if all("price" in params for params in instructions.values()):
        logger.info(f"Prices are present in all instructions. Using them directly.")
        for instr, params in instructions.items():
            order_params.extend(instr.generate_order_params(**params))
        return order_params

    logger.info(f"Fetching quotes to generate order params.")
    quotes = fetch_market_depth([instr for instr in instructions.keys()])

    for instr, params in instructions.items():
        action = params["action"]

        if isinstance(instr, Option):
            target_price = "best_bid" if action == Action.SELL else "best_ask"
            quote_for_symbol = quotes[instr.token]
            price = params.pop("price", quote_for_symbol[target_price])
            modifier = (
                (1 + config.LIMIT_PRICE_BUFFER)
                if action == Action.BUY
                else (1 - config.LIMIT_PRICE_BUFFER)
            )
            price *= modifier
            order_params.extend(instr.generate_order_params(**params, price=price))

        elif isinstance(instr, (Strangle, Straddle, SyntheticFuture)):
            call_target_key = "best_bid" if action == Action.SELL else "best_ask"
            is_synthetic = isinstance(instr, SyntheticFuture)
            if is_synthetic:
                put_target_key = "best_bid" if action == Action.BUY else "best_ask"
            else:
                put_target_key = call_target_key

            quote_for_call, quote_for_put = (
                quotes[instr.call_token],
                quotes[instr.put_token],
            )
            call_price, put_price = params.pop(
                "price",
                (quote_for_call[call_target_key], quote_for_put[put_target_key]),
            )
            if isinstance(instr, SyntheticFuture):
                call_modifier, put_modifier = (
                    (1 + config.LIMIT_PRICE_BUFFER, 1 - config.LIMIT_PRICE_BUFFER)
                    if action == Action.BUY
                    else (1 - config.LIMIT_PRICE_BUFFER, 1 + config.LIMIT_PRICE_BUFFER)
                )
            else:
                call_modifier = put_modifier = (
                    (1 + config.LIMIT_PRICE_BUFFER)
                    if action == Action.BUY
                    else (1 - config.LIMIT_PRICE_BUFFER)
                )

            call_price, put_price = call_price * call_modifier, put_price * put_modifier
            order_params.extend(
                instr.generate_order_params(**params, price=(call_price, put_price))
            )

    return order_params


@timeit()
def execute_instructions(
    instructions: dict[Option | Strangle | Straddle | SyntheticFuture, dict],
    at_market: bool = False,
) -> dict[Option | Strangle | Straddle | SyntheticFuture, float]:
    """Executes orders for a given set of instructions.
    Instructions is a dictionary where the keys are Instrument objects and
    the values are dictionaries containing the order parameters.
    The order parameters MUST contain the following keys:
    - action: Action.BUY or Action.SELL
    - quantity_in_lots: int
    - order_tag: str (optional)
    """

    def identify_average_prices(instruments, avg_prices: dict[str, float]) -> dict:

        average_price_dict = {}  # The new dict to be returned
        for instr in instruments:
            if isinstance(instr, Option):
                average_price_dict[instr] = avg_prices[instr.symbol]
            else:
                call_instr, put_instr = instr.call_option, instr.put_option
                average_price_dict[instr] = (
                    avg_prices[call_instr.symbol],
                    avg_prices[put_instr.symbol],
                )

        return average_price_dict

    # Filtering out close to expiry options (defined by less than 5 minutes)
    # if their instructions contain square_off_order=True
    # But we need to store the original instructions so that we can add closing prices
    # as average prices
    og_instructions = instructions.copy()
    instructions = {
        instr: params
        for instr, params in instructions.items()
        if not (
            params.pop("square_off_order", False)
            and time_to_expiry(instr.expiry, in_days=True) < (5 / (24 * 60))
        )
    }

    average_prices = {}

    # If instructions has at-least one option, we need to execute the orders
    # Or else skip to the next step
    if instructions:
        logger.info(f"{threading.current_thread().name} is executing orders.")
        if at_market:
            instructions = {
                instr: {**params, "price": "MARKET"}
                for instr, params in instructions.items()
            }
        order_params = generate_bulk_params(instructions)
        executed_prices = asyncio.run(execute_orders(order_params))
        executed_prices = identify_average_prices(instructions.keys(), executed_prices)
        average_prices.update(executed_prices)

    average_prices.update(
        {
            instr: instr.fetch_ltp()
            for instr in og_instructions
            if instr not in instructions
        }
    )
    return average_prices


@timeit()
def place_option_order_and_notify(
    instrument: Option | Strangle | Straddle | SyntheticFuture,
    action: Action | str,
    qty_in_lots: int,
    prices: str | int | float | tuple | list | np.ndarray = "LIMIT",
    order_tag: str = "",
    webhook_url=None,
    stop_loss_order: bool = False,
    target_status: str = "complete",
    return_avg_price: bool = True,
    square_off_order: bool = False,
    **kwargs,
) -> list | tuple | float | None:
    """Returns either a list of order ids or a tuple of avg prices or a float of avg price"""

    def return_avg_price_from_orderbook(
        orderbook: list, ids: list | tuple | np.ndarray
    ):
        avg_prices = lookup_and_return(
            orderbook, ["orderid", "status"], [ids, "complete"], "averageprice"
        )
        return avg_prices.astype(float).mean() if avg_prices.size > 0 else None

    action = action.value if isinstance(action, Action) else action

    # If square_off_order is True, check if the expiry is within 3 minutes
    if square_off_order and time_to_expiry(instrument.expiry, in_days=True) < (
        3 / (24 * 60)
    ):
        logger.info(
            f"Square off order not placed for {instrument} as expiry is within 5 minutes"
        )
        return instrument.fetch_ltp() if return_avg_price else None

    notify_dict = {
        "order_tag": order_tag,
        "Underlying": instrument.underlying,
        "Action": action,
        "Expiry": instrument.expiry,
        "Qty": qty_in_lots,
    }

    order_params = {
        "transaction_type": action,
        "quantity_in_lots": qty_in_lots,
        "stop_loss_order": stop_loss_order,
        "order_tag": order_tag,
    }

    if isinstance(instrument, (Strangle, Straddle, SyntheticFuture)):
        notify_dict.update({"Strikes": [instrument.call_strike, instrument.put_strike]})
        order_params.update({"prices": prices})
    elif isinstance(instrument, Option):
        notify_dict.update(
            {"Strike": instrument.strike, "OptionType": instrument.option_type.value}
        )
        order_params.update({"price": prices})
    else:
        raise ValueError("Invalid instrument type")

    notify_dict.update(kwargs)

    if stop_loss_order:
        assert isinstance(
            prices, (int, float, tuple, list, np.ndarray)
        ), "Stop loss order requires a price"
        target_status = "trigger pending"

    # Placing the order
    order_ids = instrument.place_order(**order_params)

    if isinstance(order_ids, tuple):  # Strangle/Straddle/SyntheticFuture
        call_order_ids, put_order_ids = order_ids[0], order_ids[1]
        order_ids = list(itertools.chain(call_order_ids, put_order_ids))
    else:  # Option
        call_order_ids, put_order_ids = False, False

    # Waiting for the orders to reflect
    sleep(0.5)

    order_book = fetch_book("orderbook")
    order_statuses_ = lookup_and_return(order_book, "orderid", order_ids, "status")
    if isinstance(order_statuses_, np.ndarray) and order_statuses_.size > 0:
        check_and_notify_order_placement_statuses(
            statuses=order_statuses_,
            target_status=target_status,
            webhook_url=webhook_url,
            **notify_dict,
        )
    else:
        notifier(
            f"Unable to check statuses. Order statuses is {order_statuses_} for orderid(s) {order_ids}. "
            f"Please confirm execution.",
            webhook_url,
            "ERROR",
        )

    if return_avg_price:
        if call_order_ids and put_order_ids:  # Strangle/Straddle/SyntheticFuture
            call_avg_price = (
                return_avg_price_from_orderbook(order_book, call_order_ids)
                or instrument.call_option.fetch_ltp()
            )
            put_avg_price = (
                return_avg_price_from_orderbook(order_book, put_order_ids)
                or instrument.put_option.fetch_ltp()
            )
            result = call_avg_price, put_avg_price
        else:  # Option
            avg_price = (
                return_avg_price_from_orderbook(order_book, order_ids)
                or instrument.fetch_ltp()
            )
            result = avg_price
        return result

    return order_ids


def check_and_notify_order_placement_statuses(
    statuses, target_status="complete", webhook_url=None, **kwargs
):
    order_prefix = (
        f"{kwargs['order_tag']}: "
        if ("order_tag" in kwargs and kwargs["order_tag"])
        else ""
    )
    order_message = [f"{k}-{v}" for k, v in kwargs.items() if k != "order_tag"]
    order_message = ", ".join(order_message)

    if all(statuses == target_status):
        logger.info(f"{order_prefix}Order(s) placed successfully for {order_message}")
    elif any(statuses == "rejected"):
        if all(statuses == "rejected"):
            notifier(
                f"{order_prefix}All orders rejected for {order_message}",
                [config.ERROR_NOTIFICATION_SETTINGS["url"], webhook_url],
                "ERROR",
            )
            raise Exception("Orders rejected")
        notifier(
            f"{order_prefix}Some orders rejected for {order_message}. Please repair.",
            [config.ERROR_NOTIFICATION_SETTINGS["url"], webhook_url],
            "CRUCIAL",
        )
    elif any(["open" in status or "modi" in status for status in statuses]):
        logger.info(
            f"{order_prefix}Orders open for {order_message}. Awaiting modification."
        )
    elif any(statuses == target_status):
        notifier(
            f"{order_prefix}Some orders successful for {order_message}. Please repair the remaining orders.",
            [config.ERROR_NOTIFICATION_SETTINGS["url"], webhook_url],
            "CRUCIAL",
        )
    else:
        notifier(
            f"{order_prefix}No orders successful. Please intervene.",
            [config.ERROR_NOTIFICATION_SETTINGS["url"], webhook_url],
            "ERROR",
        )
        raise Exception("No orders successful")
