import io
import pandas as pd
import polars as pl
import os
import ftplib
import warnings
from datetime import datetime, timedelta
import re
from sqlalchemy import create_engine
import zipfile
from volstreet.config import logger


class FTPConnection:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None

    def __enter__(self):
        self.ftp = ftplib.FTP(self.host)
        self.ftp.login(self.username, self.password)
        return self.ftp

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ftp.quit()


def find_zip_files(ftp, current_directory, zip_files=None):
    if zip_files is None:
        zip_files = []

    original_directory = ftp.pwd()
    try:
        ftp.cwd(current_directory)
        items = ftp.nlst()

        for item in items:
            if item.lower().endswith(".zip"):
                if "BACKADJUSTED" in item:  # Filter for only backadjusted files
                    absolute_path = f"{ftp.pwd()}/{item}"
                    zip_files.append(absolute_path)
            else:
                try:
                    ftp.cwd(item)
                    find_zip_files(ftp, "", zip_files)
                    ftp.cwd("..")
                except ftplib.error_perm:
                    continue
    finally:
        ftp.cwd(original_directory)

    return zip_files


# Cleaning the csv files
def parse_option_string_with_digits(option_string: str) -> dict:
    """
    Parse the given option string to identify the underlying asset, expiry date, strike price, and option type.
    This version accommodates underlying symbols that may contain digits.

    Parameters:
        option_string (str): The option string to be parsed.

    Returns:
        dict[str, str]: A dictionary containing the parsed information.
    """
    # Using a non-greedy match for the underlying and a greedy match for the strike
    pattern = r"(.+?)(\d{2}[a-zA-Z]{3}\d{2})(\d+)([a-zA-Z]+)"
    match = re.match(pattern, option_string)

    if match:
        groups = match.groups()
        return {
            "underlying": groups[0],
            "expiry": groups[1],
            "strike": groups[2],
            "option_type": groups[3].upper(),
        }
    else:
        logger.error(f"Error in parsing option string: {option_string}")
        return {
            "underlying": None,
            "expiry": None,
            "strike": None,
            "option_type": None,
        }


def round_to_next_minute(time_str):
    """
    Round a time string (HH:MM:SS) to the next minute.
    """
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    # Add enough seconds to round to the next minute
    rounded_time_obj = time_obj + timedelta(seconds=(60 - time_obj.second))
    rounded_time_str = rounded_time_obj.strftime("%H:%M:%S")
    return rounded_time_str


def process_daily_prices(df):
    # Suppress the specific UserWarning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        # Filtering for only indices

        # Identify the exchange from the tickers
        if any(".BFO" in ticker for ticker in df.Ticker):
            # Filtering out tickers that end in either -I.BFO -II.BFO -III.BFO -FUT.BFO
            df = df[~df.Ticker.str.contains(r"(I|II|III|FUT).BFO$")]
            df = df[df.Ticker.str.contains(r"^(SENSEX|BANKEX)")]
        else:
            # Filtering out tickers that end in either -I.NFO or -II.NFO
            df = df[~df.Ticker.str.contains(r"(I|II|III|FUT).NFO$")]
            df = df[df.Ticker.str.contains(r"^(.*?)NIFTY")]

    df[["underlying", "expiry", "strike", "option_type"]] = (
        df.Ticker.apply(parse_option_string_with_digits).apply(pd.Series).values
    )
    logger.info(f"Length of df before dropping NA rows: {len(df)}")
    df.dropna(subset=["underlying", "expiry", "strike", "option_type"], inplace=True)
    logger.info(f"Length of df after dropping NA rows: {len(df)}")
    df.strike = df.strike.apply(int)
    df["Time"] = df["Time"].apply(round_to_next_minute)
    df["Date"] = pd.to_datetime(df.Date, dayfirst=True)
    df["Time"] = pd.to_timedelta(df.Time)
    df["timestamp"] = df["Date"] + df["Time"]
    df = df.drop(columns=["Ticker", "Date", "Time"])
    df = df[
        [
            "timestamp",
            "underlying",
            "expiry",
            "strike",
            "option_type",
            "Open",
            "High",
            "Low",
            "Close",
        ]
    ]

    df.columns = [name.lower() for name in df.columns]

    df["expiry"] = pd.to_datetime(df["expiry"], format="%d%b%y")
    df["expiry"] = df["expiry"] + timedelta(hours=15, minutes=30)

    return df


def process_daily_prices_v2(df):

    pattern = r"(?<underlying>.+?)(?<expiry>\d{2}[a-zA-Z]{3}\d{2})(?<strike>\d+)(?<option_type>[a-zA-Z]+)"

    q = (
        df.filter(
            ~pl.col("Ticker").str.contains(r"(I|II|III|FUT).(B|N)FO"),
            pl.col("Ticker").str.contains(r"^(SENSEX|BANKEX|\w*NIFTY)"),
        )
        .with_columns(pl.col("Ticker").str.extract_groups(pattern))
        .unnest("Ticker")
        .with_columns(
            pl.col("Date")
            .str.to_date()
            .dt.combine(pl.col("Time").str.to_time("%H:%M:%S"))
        )
        .with_columns(
            (
                pl.col("Date") + pl.duration(seconds=60 - pl.col("Date").dt.second())
            ).alias("timestamp")
        )
        .drop("Date", "Time")
        .select(pl.all().name.to_lowercase())
        .with_columns(
            pl.col("expiry").str.to_datetime("%d%b%y")
            + pl.duration(hours=15, minutes=30)
        )
        .with_columns(pl.col("strike").str.to_integer())
    )
    df = q.collect()
    return df


def extract_zipped_files(directory, remove: bool = False):
    for filename in os.listdir(directory):
        if filename.endswith(".zip"):
            # Construct the full path to the ZIP file
            zip_path = os.path.join(directory, filename)

            # Open the ZIP file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(directory)

            if remove:
                # Remove the ZIP file
                os.remove(zip_path)


def process_file(file_path):
    exchange = os.path.basename(file_path).split("_")[0]
    file_name = f"{exchange}_{os.path.basename(file_path).split('_')[2]}"
    existing_files = os.listdir(os.path.join("option_prices", "all"))
    if f"{file_name}" in map(
        lambda x: os.path.basename(x), existing_files
    ):  # If the file already exists, skip it
        return
    destination = os.path.join("option_prices", "all", file_name)
    logger.info(f"Processing {file_path}")
    df = pd.read_csv(file_path)
    df = process_daily_prices(df)
    df.to_csv(destination, index=False)


def process_folder(folder_path):
    for day in os.listdir(folder_path):
        day_file = os.path.join(folder_path, day)
        process_file(day_file)


def process_year(year_path):
    for month in os.listdir(year_path):
        month_folder = os.path.join(year_path, month)
        process_folder(month_folder)


def prepare_option_prices(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True)
    df.sort_values(["timestamp", "underlying", "strike", "option_type"], inplace=True)
    return df


def write_to_csv(data: pd.DataFrame, root_path: str) -> None:
    file_name = pd.to_datetime(data["Date"].iloc[0]).strftime("%Y-%m-%d")
    full_path = os.path.join(root_path, f"{file_name}.csv")
    data.to_csv(full_path, index=False)


def insert_csv_to_db(csv_file: str, engine_url: str) -> None:
    engine = create_engine(engine_url)

    # Read the CSV file
    df = pd.read_csv(csv_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["expiry"] = pd.to_datetime(df["expiry"])

    df.to_sql("index_options", con=engine, if_exists="append", index=False)

    logger.info(f"Inserted {csv_file} into the database")


def get_present_dates(
    database_connection, for_index: str = "NIFTY"
) -> list["datetime"]:

    dates_present = database_connection.execute_query(
        f"SELECT DISTINCT DATE(timestamp) FROM index_options WHERE underlying = '{for_index}'"
    )  # Nifty as a proxy to get the max date of NSE data (DB contains NSE and BSE data)
    dates_present = [date[0] for date in dates_present]

    return dates_present


def get_ftp_credentials() -> tuple[str, str, str]:
    host = os.getenv("GDFL_FTP_HOST")
    username = os.getenv("GDFL_FTP_USER")
    password = os.getenv("GDFL_FTP_PASS")
    return host, username, password


def get_new_daily_data(*remote_directories, dates_to_skip=None, write_to: str = None):

    host, username, password = get_ftp_credentials()

    if dates_to_skip is None:
        dates_to_skip = []

    dataframes = []  # List to keep track of new dataframes
    for attempt in range(3):
        try:
            with FTPConnection(host, username, password) as ftp:
                zip_files = []
                for remote_directory in remote_directories:
                    zip_files.extend(find_zip_files(ftp, remote_directory))
                dates_of_files = [
                    file.split("_")[4].rstrip(".zip") for file in zip_files
                ]
                dates_of_files = [
                    datetime.strptime(date, "%d%m%Y").date() for date in dates_of_files
                ]
                for file, date in zip(zip_files, dates_of_files):
                    zip_name = file.split("/")[-1]
                    if date not in dates_to_skip:
                        logger.info(f"Downloading {zip_name}")
                        zip_data = io.BytesIO()
                        ftp.retrbinary("RETR " + file, zip_data.write)
                        zip_data.seek(0)  # Go to the start of the BytesIO object
                        csv_name = zip_name.split(".")[0] + ".csv"
                        with zipfile.ZipFile(zip_data, "r") as zip_ref:
                            with zip_ref.open(csv_name) as csv_file:
                                df = pd.read_csv(csv_file)
                                if write_to:
                                    path_ = os.path.join(write_to, csv_name)
                                    df.to_csv(path_, index=False)
                                else:
                                    dataframes.append(
                                        df
                                    )  # Add the new dataframe to the list
            return dataframes
        except ftplib.error_temp as e:
            logger.warning(f"Error in downloading data from GDFL: {e}")
    logger.error("Failed to download data from GDFL")


def upload_option_data(processed_data, database_connection):
    with create_engine(database_connection._alchemy_engine_url).connect() as conn:
        processed_data.to_sql("index_options", conn, if_exists="append", index=False)


def unzip_file(zip_path, csv_filename):
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        with zip_file.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file)
    return df


def process_and_upload_data(data: pd.DataFrame, database_connection):
    processed_data = process_daily_prices(data)
    upload_option_data(processed_data, database_connection)
