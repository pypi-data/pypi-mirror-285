import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta, timezone, time
import re
import functools
import calendar
from inspect import signature
from volstreet.config import holidays, logger
from volstreet import config


def word_to_num(s):
    word = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
    }
    multiplier = {
        "thousand": 1000,
        "hundred": 100,
        "million": 1000000,
        "billion": 1000000000,
    }

    words = s.lower().split()
    if words[0] == "a":
        words[0] = "one"
    total = 0
    current = 0
    for w in words:
        if w in word:
            current += word[w]
        if w in multiplier:
            current *= multiplier[w]
        if w == "and":
            continue
        if w == "thousand" or w == "million" or w == "billion":
            total += current
            current = 0
    total += current
    return total


def current_time():
    if config.backtest_mode:
        return config.backtest_state
    # Adjusting for timezones
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).replace(tzinfo=None)


def market_hours():
    if time(9, 15) <= current_time().time() <= time(15, 30):
        return True
    else:
        return False


def timed_executor(wait_time: int):
    def decorator(task):
        last_call_time = datetime.min

        def wrapper():
            nonlocal last_call_time
            if current_time() >= last_call_time + timedelta(seconds=wait_time):
                task()
                last_call_time = current_time()

        return wrapper

    return decorator


def last_market_close_time():
    if current_time().time() < time(9, 15):
        wip_time = current_time() - timedelta(days=1)
        wip_time = wip_time.replace(hour=15, minute=30, second=0, microsecond=0)
    elif current_time().time() > time(15, 30):
        wip_time = current_time().replace(hour=15, minute=30, second=0, microsecond=0)
    else:
        wip_time = current_time()

    if wip_time.weekday() not in [5, 6] and wip_time.date() not in holidays:
        return wip_time
    else:
        # Handling weekends and holidays
        while wip_time.weekday() in [5, 6] or wip_time.date() in holidays:
            wip_time = wip_time - timedelta(days=1)

    last_close_day_time = wip_time.replace(hour=15, minute=30, second=0, microsecond=0)
    return last_close_day_time


def find_strike(strike, base, offset=0, steps=0):
    if offset and steps:
        raise Exception("Both offset and steps cannot be used together")
    strike = strike * (1 + offset)  # Offset is a percentage
    number = base * round(strike / base)
    number = number + (steps * base)  # Shifting the strike by steps
    return int(number)


def get_range_of_strikes(ltp, base, range_of_strikes, offset=0):
    """Range of strikes means the number of strikes each side of the current strike. For example, if the current
    strike is 15000 and range_of_strikes is 1, the function will return [14950, 15000, 15050]
    """
    current_strike = find_strike(ltp, base, offset=offset)
    strike_range = np.arange(
        current_strike - (base * range_of_strikes),
        current_strike + (base * (range_of_strikes + 1)),
        base,
    )
    strike_range = [*map(int, strike_range)]
    return strike_range


def custom_round(x, base=0.05):
    """Used in place_order function to round off the price to the nearest 0.05"""
    if x == 0:
        return 0

    num = base * round(x / base)
    if num == 0:
        num = base
    return round(num, 2)


def _nearest_round(number, kind: str, significant_digits: int):
    if number == 0:
        return 0
    # Find the first non-zero digit
    first_non_zero = -math.floor(math.log10(abs(number)))
    # Calculate total digits to keep
    total_digits = first_non_zero + significant_digits
    # Scale up, floor, and scale back down
    scaled_number = getattr(math, kind)(number * 10**total_digits) / 10**total_digits
    return scaled_number


def dynamic_floor(number, significant_digits: int = 1):
    return _nearest_round(number, "floor", significant_digits)


def dynamic_ceil(number, significant_digits: int = 1):
    return _nearest_round(number, "ceil", significant_digits)


def round_to_nearest(x, digits=2):
    if x is None or x == 0 or np.isnan(x):
        return np.nan
    return round(x, digits)


def splice_orders(quantity_in_lots, freeze_qty):
    if quantity_in_lots > freeze_qty:
        loops = int(quantity_in_lots / freeze_qty)
        if loops > config.LARGE_ORDER_THRESHOLD:
            raise Exception(
                "Order too big. This error was raised to prevent accidental large order placement."
            )

        remainder = quantity_in_lots % freeze_qty
        if remainder == 0:
            spliced_orders = [freeze_qty] * loops
        else:
            spliced_orders = [freeze_qty] * loops + [remainder]
    else:
        spliced_orders = [quantity_in_lots]
    return spliced_orders


def time_to_expiry(
    expiry: str, effective_time: bool = False, in_days: bool = False
) -> float:
    """Return time left to expiry"""
    if in_days:
        multiplier = 365
    else:
        multiplier = 1

    expiry = datetime.strptime(expiry, "%d%b%y")
    time_left_to_expiry = (
        (expiry + pd.DateOffset(minutes=930)) - current_time()
    ) / timedelta(days=365)

    # Subtracting holidays and weekends
    if effective_time:
        date_range = pd.date_range(current_time().date(), expiry - timedelta(days=1))
        numer_of_weekdays = sum(date_range.dayofweek > 4)
        number_of_holidays = sum(date_range.isin(pd.DatetimeIndex(holidays)))
        time_left_to_expiry -= (numer_of_weekdays + number_of_holidays) / 365
    return round(time_left_to_expiry * multiplier, 5)


def strike_range_different(
    refreshed_strike_range: list[int | float], current_strike_range: list[int | float]
) -> bool:
    if set(refreshed_strike_range) == set(current_strike_range):
        return False
    new_strikes = set(refreshed_strike_range) - set(current_strike_range)
    if len(new_strikes) >= 0.4 * len(current_strike_range):  # Hardcoded 40%
        return True
    return False


def round_shares_to_lot_size(shares, lot_size):
    number = lot_size * round(shares / lot_size)
    return int(number)


def convert_exposure_to_lots(
    exposure: int | float, spot_price: float, lot_size: int, round_to: int = None
) -> int:
    shares = round_shares_to_lot_size(exposure / spot_price, lot_size)
    lots = shares / lot_size
    if round_to is not None:
        lots = custom_round(lots, round_to)
        # Return at least 1 lot
    return max(1, int(lots))


def check_for_weekend(expiry: str) -> bool:
    expiry = datetime.strptime(expiry, "%d%b%y")
    expiry = expiry + pd.DateOffset(minutes=930)
    date_range = pd.date_range(current_time().date(), expiry - timedelta(days=1))
    return date_range.weekday.isin([5, 6]).any()


def find_next_trading_day(date: datetime | str = None) -> datetime:
    if date is None:
        date = current_time().date()
    elif isinstance(date, str):
        date = pd.to_datetime(date)
        date = date.date()
    elif isinstance(date, datetime):
        date = date.date()
    date = date + timedelta(days=1)
    while date.weekday() in [5, 6] or date in holidays:
        date = date + timedelta(days=1)
    return date


def generate_cache_key_from_signature(func, *args, **kwargs):
    sig = signature(func)
    bound = sig.bind_partial(*args, **kwargs)
    bound.apply_defaults()

    sorted_kwargs_values = tuple(value for _, value in sorted(bound.kwargs.items()))
    combined_args = tuple(bound.args) + sorted_kwargs_values
    key = (func.__name__,) + combined_args  # Adding function name to the key
    return key


def custom_cacher(func):
    """
    A time based cache decorator for methods. It caches the result of the function call
    and returns the cached result if the function is called within the cache interval.
    Designed to be used as a decorator for *methods*. It caches the result of the function call
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "caching", False):
            logger.debug(
                f"Caching is enabled for {self.__class__.__name__}.{func.__name__}"
            )
            cache_key = generate_cache_key_from_signature(func, self, *args, **kwargs)
        else:
            cache_key = None
        if (
            getattr(self, "caching", False)
            and hasattr(self, "_cache")
            and cache_key in self._cache
            and current_time() - self._cache[cache_key]["last_fetch_time"]
            < timedelta(seconds=config.CACHE_INTERVAL)
        ):
            logger.debug(f"Using cache for {self.__class__.__name__}.{func.__name__}")
            return self._cache[cache_key]["result"]
        else:
            result = func(self, *args, **kwargs)
            if getattr(self, "caching", False):
                if not hasattr(self, "_cache"):
                    self._cache = {}
                self._cache[cache_key] = {
                    "result": result,
                    "last_fetch_time": current_time(),
                }
            return result

    return wrapper


def calculate_ema(new_price, prev_ema, alpha):
    """
    Calculate Exponential Moving Average (EMA)

    Parameters:
    - new_price (float): The new price data point
    - prev_ema (float or None): The previous EMA value, or None if not calculated yet
    - alpha (float): The smoothing factor

    Returns:
    float: The new EMA value
    """
    if prev_ema is None:
        return new_price
    return (new_price * alpha) + (prev_ema * (1 - alpha))


def spot_price_from_future(future_price, interest_rate, time_to_future):
    """
    Calculate the spot price from the future price, interest rate, and time.

    :param future_price: float, the future price of the asset
    :param interest_rate: float, the annual interest rate (as a decimal, e.g., 0.05 for 5%)
    :param time_to_future: float, the time to maturity (in years)
    :return: float, the spot price of the asset
    """
    spot_price = future_price / ((1 + interest_rate) ** time_to_future)
    return spot_price


def charges(buy_premium, contract_size, num_contracts, freeze_quantity=None):
    if freeze_quantity:
        number_of_orders = np.ceil(num_contracts / freeze_quantity)
    else:
        number_of_orders = 1

    buy_brokerage = 40 * number_of_orders
    sell_brokerage = 40 * number_of_orders
    transaction_charge_rate = 0.05 / 100
    stt_ctt_rate = 0.0625 / 100
    gst_rate = 18 / 100

    buy_transaction_charges = (
        buy_premium * contract_size * num_contracts * transaction_charge_rate
    )
    sell_transaction_charges = (
        buy_premium * contract_size * num_contracts * transaction_charge_rate
    )
    stt_ctt = buy_premium * contract_size * num_contracts * stt_ctt_rate

    buy_gst = (buy_brokerage + buy_transaction_charges) * gst_rate
    sell_gst = (sell_brokerage + sell_transaction_charges) * gst_rate

    total_charges = (
        buy_brokerage
        + sell_brokerage
        + buy_transaction_charges
        + sell_transaction_charges
        + stt_ctt
        + buy_gst
        + sell_gst
    )
    charges_per_share = total_charges / (num_contracts * contract_size)

    return round(charges_per_share, 1)


def _parse_bse_symbol(
    symbol, index: str
):  # todo check how months higher than 9 are handled and adapt it

    if len(symbol.lstrip(index)) != 12:
        logger.warning("BSE symbol is of unexpected length")
        return None

    pattern_one_digit_month = r"(\w+)(\d{2})(\d{1})(\d{2})(\d{5})(\w{2})"
    # pattern_two_digit_month = r"(\w+)(\d{2})(\d{2})(\d{2})(\d{5})(\w+)"

    # First try with the assumption that the month has one digit
    match = re.match(pattern_one_digit_month, symbol)
    if match:
        name, year, month, day, strike, option_type = match.groups()
        month = month.zfill(2)  # Zero-pad the month

        # Format the expiry date
        expiry_date = f"{day}{calendar.month_abbr[int(month)]}{year}"

        return name, expiry_date.upper(), strike, option_type
    else:
        return None

    # else:
    #     # Try with the assumption that the month has two digits
    #     match = re.match(pattern_two_digit_month, symbol)
    #     if match:
    #         name, year, month, day, strike, option_type = match.groups()
    #     else:
    #         return None  # Return None if both patterns fail


def parse_symbol(symbol):

    if symbol.startswith("SENSEX") or symbol.startswith("BANKEX"):
        return _parse_bse_symbol(symbol, re.search(r"([A-Za-z]+)", symbol).group(1))

    match = re.match(r"([A-Za-z]+)(\d{2}[A-Za-z]{3}\d{2})(\d+)(\w+)", symbol)
    if match:
        return match.groups()
    return None


def get_background_tasks(obj: object, task_name: str):
    """obj is the instance of the class where the tasks are defined"""
    parallel_tasks = [attr for attr in dir(obj) if attr.startswith(task_name)]
    parallel_tasks = [
        getattr(obj, attr) for attr in parallel_tasks if callable(getattr(obj, attr))
    ]
    return parallel_tasks


def filter_orderbook_by_time(
    orderbook: list[dict], start_time: datetime = None, end_time: datetime = None
) -> list[dict]:
    def check_eligibility(order):
        for field in ["updatetime", "exchtime", "exchorderupdatetime"]:
            try:
                return (
                    start_time
                    < datetime.strptime(order.get(field), "%d-%b-%Y %H:%M:%S")
                    < end_time
                )
            except Exception as e:
                logger.error(
                    f"Error in filter_orderbook_by_time for order {order}: {e}"
                )
                continue
        return False

    if start_time is None:
        start_time = datetime.now() - timedelta(days=1)
    elif isinstance(start_time, str):
        start_time = pd.to_datetime(start_time, infer_datetime_format=True)
    if end_time is None:
        end_time = datetime.now() + timedelta(days=1)
    elif isinstance(end_time, str):
        end_time = pd.to_datetime(end_time, infer_datetime_format=True)
    filtered_orders = [order for order in orderbook if check_eligibility(order)]
    return filtered_orders


def get_next_timestamp(
    interval_minutes: int | float,
    from_time: datetime = None,
    exit_time_tuple: tuple = None,
) -> datetime:
    # Let's handle cases when tuple is either (hour, minute) or (hour, minute, second)
    # Reading from JSON generates a list hence converting it to a tuple
    exit_time = tuple(exit_time_tuple) if exit_time_tuple else (23, 59, 59)
    exit_hour, exit_minute, exit_second = exit_time + (0,) * (3 - len(exit_time))

    from_time = from_time or current_time()

    # Determining the next timestamp
    if isinstance(interval_minutes, int):
        # Rounding the time_now to the nearest minute
        rounded_time_now = (from_time + timedelta(seconds=30)).replace(
            second=0, microsecond=0
        )
        next_timestamp = (
            rounded_time_now + timedelta(minutes=(interval_minutes - 1))
        ).replace(second=57, microsecond=500000)
        if next_timestamp <= from_time:
            next_timestamp += timedelta(minutes=1)
    elif isinstance(interval_minutes, float):
        next_timestamp = from_time + timedelta(minutes=interval_minutes)
    else:
        raise ValueError("Invalid interval_minutes value")

    next_timestamp = min(
        next_timestamp,
        current_time().replace(
            hour=exit_hour, minute=exit_minute, second=exit_second, microsecond=0
        ),
    )

    return next_timestamp
