import json
import pandas as pd
import re
from volstreet.config import logger


def parse_jsonl_file(file_path: str) -> pd.DataFrame:
    with open(file_path, "r") as f:
        lines = f.readlines()
    lines = [line.rstrip("\n") for line in lines]
    logs = []
    for i, line in enumerate(lines):
        try:
            j = json.loads(line)
            logs.append(j)
        except json.JSONDecodeError:
            logger.error(
                f"Error in line number {i} of file {file_path}." " Skipping this line."
            )
    log_df = pd.DataFrame(logs)
    return log_df


def add_order_tracking_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["uniqueorderid"] = (
        df["message"]
        .apply(lambda x: re.search(r"'uniqueorderid': '(.*?)'", x))
        .apply(lambda x: x.group(1) if x else None)
    )
    df["orderid"] = (
        df["message"]
        .apply(lambda x: re.search(r"'orderid': '(.*?)'", x))
        .apply(lambda x: x.group(1) if x else None)
    )
    df["status"] = (
        df["message"]
        .apply(lambda x: re.search(r"'status': '(.*?)'", x))
        .apply(lambda x: x.group(1) if x else None)
    )
    df["orderstatus"] = (
        df["message"]
        .apply(lambda x: re.search(r"'orderstatus': '(.*?)'", x))
        .apply(lambda x: x.group(1) if x else None)
    )
    return df
