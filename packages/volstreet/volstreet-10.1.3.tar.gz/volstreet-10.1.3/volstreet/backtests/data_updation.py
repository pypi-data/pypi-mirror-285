import pickle
from importlib.resources import files
from pathlib import Path
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from volstreet.config import logger
from volstreet.historical_info import market_days
from volstreet.backtests.database import DataBaseConnection
from volstreet.backtests.framework import BackTester
from volstreet.backtests.underlying_info import UnderlyingInfo


def extend_expiry_dates() -> None:
    """Extend the expiry dates which are stored in the index_expiries.pkl file."""

    dbc = DataBaseConnection()

    directory = files("volstreet").joinpath("historical_info")
    # noinspection PyTypeChecker
    file_path = Path(directory.joinpath("index_expiries.pkl"))

    with open(file_path, "rb") as file:
        all_expiry_dates = pickle.load(file)

    for underlying in [
        "NIFTY",
        "BANKNIFTY",
        "FINNIFTY",
        "MIDCPNIFTY",
        "SENSEX",
        "BANKEX",
    ]:
        index_expiry_dates = all_expiry_dates.get(underlying, [])
        new_list = dbc.fetch_historical_expiries(underlying)
        combined_list = [*set(index_expiry_dates + new_list)]
        all_expiry_dates[underlying] = combined_list
        logger.info(f"Extended expiry dates for {underlying}")

    with open(file_path, "wb") as file:
        pickle.dump(all_expiry_dates, file)


def update_market_days() -> None:
    """Update the market days which are stored in the market_days.pkl file."""

    dbc = DataBaseConnection()

    directory = files("volstreet").joinpath("historical_info")
    # noinspection PyTypeChecker
    file_path = Path(directory.joinpath("market_days.pkl"))

    new_market_days = dbc.execute_query(
        "SELECT DISTINCT(DATE(timestamp)) FROM index_options"
    )
    new_market_days = [date[0] for date in new_market_days]

    with open(file_path, "wb") as file:
        pickle.dump(new_market_days, file)
        logger.info(
            f"Updated market days. New number of market days: {len(new_market_days)}"
        )


def update_price_stream_for_index(
    index: str, earliest_allowed_date: "datetime.date" = None, days_to_expiry: int = 2
) -> None:
    backtester = BackTester()
    index = UnderlyingInfo(index)
    engine = create_engine(backtester._alchemy_engine_url)
    market_dts = [datetime.combine(day, datetime.min.time()) for day in market_days]
    target_days = [
        day.date()
        for day in market_dts
        if backtester.historic_time_to_expiry(index.name, day, in_days=True)
        <= days_to_expiry
    ]  # For now only two nearest expiry dates
    latest_date = backtester.execute_query(
        f"""
        SELECT MAX(DATE(timestamp)) FROM price_stream WHERE symboltoken LIKE '{index.name}%'
        """
    )[0][0]
    filter_date = latest_date or earliest_allowed_date
    assert (
        filter_date
    ), "Atleast one of latest_date or earliest_allowed_date must be provided"
    dates_to_update = [
        day for day in target_days if day > filter_date
    ]  # Only update the days which are not already present in the database
    if not dates_to_update:
        logger.info(f"No days to update for {index.name}")
        return
    logger.info(f"Updating price stream for {index.name} for days: {dates_to_update}")
    for day in dates_to_update:
        df = backtester.get_prices_for_day(
            underlying_info=index,
            day=day,
            num_strikes=120,
            num_exp=1,
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df[["timestamp", "symboltoken", "price"]]
        df["price"] = df["price"].round(3)
        df = df.sort_values(["timestamp", "symboltoken"])
        logger.info(
            f"Updating price stream for {index.name} on {day} with len {len(df)}"
        )
        df.to_sql("price_stream_v2", con=engine, if_exists="append", index=False)
        logger.info(f"Updated price stream for {index.name} on {day}")
    logger.info(f"Finished updating price stream for {index.name}")
