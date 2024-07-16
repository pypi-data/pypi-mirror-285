import pandas as pd
from datetime import datetime
import numpy as np
from volstreet.config import logger
from volstreet.historical_info import historical_expiry_dates, historical_holidays


class UnderlyingInfo:
    def __init__(self, name):
        self.name = name.upper()
        self.base = self._get_base()
        self.expiry_dates = filter_expiry_dates_for_index(self.name)

    def _get_base(self):
        if self.name in ["NIFTY", "FINNIFTY"]:
            return 50
        elif self.name in ["BANKNIFTY", "SENSEX", "BANKEX"]:
            return 100
        elif self.name == "MIDCPNIFTY":
            return 25
        else:
            raise ValueError("Invalid index name")

    def get_dte_list(self, dte: int):
        expiry_dates = [date.date() for date in self.expiry_dates]
        dtes = list(map(lambda x: shift_date(x, dte), expiry_dates))
        return dtes


def filter_expiry_dates_for_index(underlying: str) -> pd.DatetimeIndex:
    index_expiry_dates = historical_expiry_dates[underlying.upper()]
    return pd.DatetimeIndex(sorted(index_expiry_dates))


def fetch_historical_expiry(
    underlying: str,
    date_time: str | datetime,
    threshold_days: int = 0,
    n_exp: int = 1,
) -> pd.DatetimeIndex | pd.Timestamp | None:
    """Not very robust because it modifies the date_time in-place. This can lead to unexpected results."""
    if isinstance(date_time, str):
        date_time = pd.to_datetime(date_time)

    filtered_dates = filter_expiry_dates_for_index(underlying)
    filtered_dates = filtered_dates.sort_values()
    delta_days = (filtered_dates - date_time.replace(hour=00, minute=00)).days
    filtered_dates = filtered_dates[delta_days >= threshold_days]
    nearest_exp_dates = [*sorted(filtered_dates)]
    if n_exp == 1:
        return nearest_exp_dates[0] if len(nearest_exp_dates) != 0 else None
    if len(nearest_exp_dates) < n_exp:
        logger.warning(f"Insufficient expiry dates for {underlying} on {date_time}")
        while len(nearest_exp_dates) < n_exp:
            nearest_exp_dates.append(np.nan)
    return pd.DatetimeIndex(nearest_exp_dates[:n_exp])


def historic_time_to_expiry(
    underlying: UnderlyingInfo,
    date_time: str | datetime,
    nth_expiry: int = 1,
    in_days: bool = True,
    effective: bool = True,
) -> float:
    """Careful when passing datetime obj as it will be modified in-place."""
    if isinstance(date_time, str):
        date_time = pd.to_datetime(date_time)

    expiry_dates = fetch_historical_expiry(underlying.name, date_time, n_exp=4)
    nth_expiry = expiry_dates[nth_expiry - 1]
    days_to_expiry = (nth_expiry - date_time).days
    if effective:  # calculate  the number of holidays between the two dates
        holidays = len(
            [
                date
                for date in pd.date_range(date_time, nth_expiry)
                if date in historical_holidays and date.weekday() < 5
            ]
        )
        days_to_expiry -= holidays
    return days_to_expiry if in_days else days_to_expiry / 365


def shift_date(date, days):
    while days > 0:
        date = date - pd.Timedelta(days=1)
        if date in historical_holidays:
            continue
        days -= 1
    return date
