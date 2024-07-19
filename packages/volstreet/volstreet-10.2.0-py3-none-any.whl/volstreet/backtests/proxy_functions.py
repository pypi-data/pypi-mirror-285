from datetime import datetime, timedelta, time
import pandas as pd
import re
from volstreet import config
from volstreet.utils import current_time, get_range_of_strikes
from volstreet.backtests.underlying_info import UnderlyingInfo, fetch_historical_expiry
from volstreet.backtests.framework import BackTester


class ProxyPriceFeed:
    data_bank = {}
    backtester = BackTester()
    _current_group = None

    @classmethod
    def request_grouped_prices_for_day(
        cls, underlying: UnderlyingInfo, day: datetime, include_vix_data=False, **kwargs
    ):
        day_prices = cls.backtester.get_price_stream_for_day(underlying, day, **kwargs)
        if include_vix_data:
            vix_data = cls.backtester.fetch_index_prices(
                "India Vix",
                from_timestamp=f"{day} 09:16",
                to_timestamp=f"{day} 15:30",
            )
            vix_data = vix_data.rename(
                columns={
                    "timestamp": "timestamp",
                    "open": "price",
                    "underlying": "symboltoken",
                }
            )
            vix_data = vix_data[["timestamp", "price", "symboltoken"]]
            # To ensure that vix prices are available for all timestamps
            new_index = pd.date_range(
                start=f"{day} 09:16", end=f"{day} 15:30", freq="1min"
            )
            new_index.name = "timestamp"
            vix_data = (
                vix_data.set_index("timestamp")
                .reindex(new_index, method="nearest")
                .reset_index()
            )
            day_prices = pd.concat([day_prices, vix_data])
            day_prices = day_prices.sort_values("timestamp")

        day_prices_grouped = day_prices.groupby(day_prices.timestamp.dt.time)
        return day_prices_grouped

    @classmethod
    def update_prices(cls):
        prices_at_time = cls._current_group.get_group(config.backtest_state.time())
        price_dict = prices_at_time.to_dict(orient="records")
        cls.data_bank = {
            x["symboltoken"]: {
                "token": x["symboltoken"],
                "ltp": x["price"],
                "best_bid": x["price"],
                "best_ask": x["price"],
                "best_bid_qty": 0,
                "best_ask_qty": 0,
                "last_traded_datetime": x["timestamp"],
            }
            for x in price_dict
        }


class ProxyFeeds:
    price_feed = ProxyPriceFeed
    order_feed = []
    back_up_tokens = set()

    @classmethod
    def price_feed_connected(cls):
        return bool(cls.price_feed.data_bank)


def get_symbol_token(name=None, expiry=None, strike=None, option_type=None):
    if expiry is None and strike is None and option_type is None:
        return name.upper(), name.upper()
    else:
        symbol = f"{name.upper()}{expiry.upper()}{int(strike)}{option_type.upper()}"
        return symbol, symbol


def get_expiry_dates(underlying: str):
    expiries = fetch_historical_expiry(
        underlying, current_time(), threshold_days=0, n_exp=3
    )
    return expiries


def get_available_strikes(name: str, *args, **kwargs) -> dict:
    price = ProxyFeeds.price_feed.data_bank[name]["ltp"]
    # 60 strikes because that is current implementation in price_stream_v2
    strike_range = get_range_of_strikes(price, UnderlyingInfo(name).base, 60)
    return {"CE": strike_range, "PE": strike_range}


def get_base(name, expiry):
    return UnderlyingInfo(name).base


def get_lot_size(*args, **kwargs):
    return 1


def identify_average_prices(instruments, avg_prices: dict[str, float]) -> dict:

    average_price_dict = {}  # The new dict to be returned
    for instr in instruments:
        if hasattr(instr, "call_option") and hasattr(instr, "put_option"):
            call_instr, put_instr = instr.call_option, instr.put_option
            average_price_dict[instr] = (
                avg_prices[call_instr.symbol],
                avg_prices[put_instr.symbol],
            )
        else:
            average_price_dict[instr] = avg_prices[instr.symbol]

    return average_price_dict


def parse_symbol(symbol):
    match = re.match(r"([A-Za-z]+)(\d{2}[A-Za-z]{3}\d{2})(\d+)(\w+)", symbol)
    return match.groups()


def simulate_execution(order: dict):

    price = order["price"]
    index, expiry, strike, option_type = parse_symbol(order["symboltoken"])
    value = order["quantity"] * price * (1 if order["transactiontype"] == "BUY" else -1)
    order_details = {
        "timestamp": current_time(),
        "index": index,
        "expiry": expiry,
        "strike": strike,
        "option_type": option_type,
        "action": order["transactiontype"],
        "price": price,
        "quantity": order["quantity"],
        "value": value,
        "token": order["symboltoken"],
    }
    return order_details


def execute_instructions(instructions: dict, *args, **kwargs):
    orders = []
    for instrument, params in instructions.items():
        filtered_params = {
            k: v for k, v in params.items() if k in ["action", "quantity_in_lots"]
        }
        if hasattr(instrument, "call_token") and hasattr(instrument, "put_token"):
            call_price = ProxyFeeds.price_feed.data_bank[instrument.call_token]["ltp"]
            put_price = ProxyFeeds.price_feed.data_bank[instrument.put_token]["ltp"]
            orders.extend(
                instrument.generate_order_params(
                    **filtered_params, price=(call_price, put_price)
                )
            )
        else:
            price = ProxyFeeds.price_feed.data_bank[instrument.token]["ltp"]
            orders.extend(
                instrument.generate_order_params(**filtered_params, price=price)
            )
    orders = [simulate_execution(order) for order in orders]
    ProxyFeeds.order_feed.extend(orders)
    average_prices = {order["token"]: order["price"] for order in orders}
    return identify_average_prices(instructions, average_prices)


def sleep_until_next_action(
    interval_minutes: int | float, exit_time: tuple[int, int], *args, **kwargs
):
    interval_minutes = max(1, interval_minutes)
    target_time = config.backtest_state + timedelta(minutes=interval_minutes)
    target_time = min(
        target_time,
        datetime.combine(config.backtest_state.date(), time(*exit_time)),
    )
    tasks_to_perform = kwargs.get("tasks_to_perform", [])
    interruption_condition = kwargs.get("interruption_condition", lambda: False)
    while config.backtest_state < target_time:
        if interruption_condition():
            config.logger.info("Interruption condition met. Exiting loop.")
            break
        for task in tasks_to_perform:
            task()
        config.backtest_state += timedelta(minutes=1)
        ProxyPriceFeed.update_prices()


def retry_angel_api(*args, **kwargs):
    def decorator(func):
        return func

    return decorator


def access_rate_handler(*args, **kwargs):
    def decorator(func):
        return func

    return decorator


def timeit(*args, **kwargs):
    def decorator(func):
        return func

    return decorator


class SmartConnect:
    pass


class DataException(Exception):
    pass
