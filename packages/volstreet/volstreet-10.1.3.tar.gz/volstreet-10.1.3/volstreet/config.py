import urllib
import pandas as pd
import os
import json
import sys
from pathlib import Path
from threading import local
from twilio.rest import Client as TwilioClient
from io import StringIO
import logging
from importlib.resources import files
from collections import defaultdict
from volstreet.vslogging import setup_logging


def change_mode(mode: str):
    mode_file = files("volstreet").joinpath("volstreet_mode.json")
    with open(mode_file, "w") as f:
        json.dump({"mode": mode}, f)
    sys.exit()


def get_ticker_file():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    data = urllib.request.urlopen(url).read().decode()

    # Use StringIO to mimic a file using the string data
    df = pd.read_json(StringIO(data))
    return df


def fetch_holidays():
    try:
        url = "https://marketholidays.s3.ap-south-1.amazonaws.com/holidays.csv"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        holidays = pd.DatetimeIndex(df["date"])
        holidays = [d.date() for d in holidays]
    except Exception as e:
        logger.error(f"Error while fetching holidays: {e}")
        backup_file = Path("holidays.csv")
        if os.path.exists(backup_file):
            df = pd.read_csv(backup_file)
            df["Date"] = pd.to_datetime(df["Date"])
            holidays = df["Date"].values.astype("datetime64[D]")
        else:
            # Handle the case where the backup file doesn't exist
            logger.info(f"Backup file {backup_file} not found. Holidays set to empty.")
            holidays = pd.to_datetime([])
    return holidays


def get_symbol_df():
    try:
        url = "https://symbolinfo.s3.ap-south-1.amazonaws.com/symbol_info.csv"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        df["SYMBOL"] = df["SYMBOL"].str.strip()
        return df
    except Exception as e:
        logger.error(f"Error while fetching symbols: {e}")
        return pd.DataFrame()


class Twilio:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    content_sid = os.getenv("TWILIO_CONTENT_SID")
    service_sid = os.getenv("TWILIO_SERVICE_SID")
    if account_sid is not None and auth_token is not None:
        client = TwilioClient(account_sid, auth_token)
    else:
        client = None


# Set the default values for critical variables
NOTIFIER_LEVEL = "INFO"
LARGE_ORDER_THRESHOLD = 30
ERROR_NOTIFICATION_SETTINGS = {"url": None}
LIMIT_PRICE_BUFFER = 0.01
MAX_PRICE_MODIFICATION = 0.3
MODIFICATION_STEP_SIZE = 0.05
MODIFICATION_SLEEP_INTERVAL = 0.5
CACHING = True
CACHE_INTERVAL = 2  # in seconds
EXPIRY_FREQUENCIES: dict = {
    "MIDCPNIFTY": 0,
    "FINNIFTY": 1,
    "BANKNIFTY": 2,
    "NIFTY": 3,
    "SENSEX": 4,
    "BANKEX": 0,
}

# Backtest settings
try:
    vs_mode_file = files("volstreet").joinpath("volstreet_mode.json")
    with open(vs_mode_file, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}
_mode = data.get("mode", "live")
backtest_mode = "backtest" in _mode
backtest_state = None


# Create loggers
setup_logging()
logger = logging.getLogger("volstreet")
logger = logging.LoggerAdapter(logger, {})

if backtest_mode:
    scrips = pd.DataFrame()
    token_symbol_dict = {}
    token_exchange_dict = defaultdict(lambda: "BACKTESTER")
    holidays = []
    symbol_df = pd.DataFrame()
else:
    # Get the list of scrips
    scrips = get_ticker_file()
    scrips["expiry_dt"] = pd.to_datetime(
        scrips[scrips.expiry != ""]["expiry"], format="%d%b%Y"
    )
    scrips["expiry_formatted"] = scrips["expiry_dt"].dt.strftime("%d%b%y")
    scrips["expiry_formatted"] = scrips["expiry_formatted"].str.upper()

    # Create a dictionary of token and symbol
    token_symbol_dict = dict(zip(scrips["token"], scrips["symbol"]))

    # Create a dictionary of token and exchange segment
    token_exchange_dict = dict(zip(scrips["token"], scrips["exch_seg"]))

    # Get the list of holidays
    try:
        holidays = fetch_holidays()
    except Exception as e:
        logger.error(f"Error while fetching holidays: {e}")
        holidays = pd.to_datetime([])

    # Get the list of symbols
    symbol_df = get_symbol_df()


implemented_indices = [
    "NIFTY",
    "BANKNIFTY",
    "FINNIFTY",
    "MIDCPNIFTY",
    "SENSEX",
    "BANKEX",
    "INDIA VIX",
]

# Create a thread local object
thread_local = local()

modification_fields = [
    "orderid",
    "variety",
    "symboltoken",
    "price",
    "ordertype",
    "transactiontype",
    "producttype",
    "exchange",
    "tradingsymbol",
    "quantity",
    "duration",
    "status",
]
