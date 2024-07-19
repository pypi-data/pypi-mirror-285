from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os
from volstreet.config import logger
from volstreet.utils.data_io import make_directory_if_needed
from volstreet.backtests.framework import (
    BackTester,
    UnderlyingInfo,
    add_greeks_to_dataframe,
    calculate_moving_interest_rate,
    calculate_average_atm_info,
)


def build_option_chain_for_vol_surface(
    backtester: BackTester,
    underlying_info: UnderlyingInfo,
    timestamp: str | datetime,
):
    option_chain = backtester.build_option_chain(
        underlying_info,
        timestamp,
        timestamp,
        num_strikes=30,
        num_exp=3,
        threshold_days_expiry=0,
        add_greeks=True,
    )
    option_chain = option_chain.dropna().copy()
    option_chain["underlying"] = underlying_info.name
    option_chain["iv"] = np.mean(option_chain[["call_iv", "put_iv"]], axis=1)

    # Calculating the ATM IV for each expiry
    atm_iv_of_expiries = option_chain.groupby(option_chain["expiry"]).apply(
        lambda x: x.loc[abs(x["strike"] - x["atm_strike"]).idxmin(), "iv"],
        include_groups=False,
    )
    atm_iv_of_expiries = atm_iv_of_expiries.rename("atm_iv").reset_index()

    # Merging with the original option chain
    option_chain = option_chain.merge(atm_iv_of_expiries, on="expiry")

    # Removing call and put columns
    option_chain = option_chain.filter(regex="^(?!call_|put_).*$")

    return option_chain


def store_option_chain(
    backtester: BackTester,
    underlying_info: UnderlyingInfo,
    timestamp: str | datetime,
):
    logger.info(f"Fetching option chain for {timestamp}")
    try:
        option_chain = build_option_chain_for_vol_surface(
            backtester, underlying_info, timestamp
        )
        option_chain.to_csv(
            f"data/option_chains/{underlying_info.name}_{timestamp.strftime('%d%m%Y_%H%M%S')}.csv",
            index=False,
        )
        return "Stored successfully!"
    except Exception as e:
        logger.error(f"Error fetching option chain for {timestamp}: {e}")
        return "Error!"


def build_atm_ivs(
    backtester: BackTester,
    underlying: UnderlyingInfo,
    from_timestamp: str | datetime,
    to_timestamp: str | datetime,
    **kwargs,
) -> pd.DataFrame:

    option_chain = backtester.build_option_chain(
        underlying, from_timestamp, to_timestamp, **kwargs
    )
    option_chain["r"] = calculate_moving_interest_rate(option_chain)
    df = add_greeks_to_dataframe(option_chain, r_col="r")
    averages = df.groupby(["timestamp", "expiry"]).apply(calculate_average_atm_info)
    averages["atm_iv"] = averages["atm_iv"].ffill().bfill()
    averages["underlying"] = underlying.name
    averages = averages.reset_index()
    return averages


def store_atm_ivs(*args, **kwargs):
    ivs = build_atm_ivs(*args, **kwargs)
    underlying = ivs.underlying[0]
    from_timestamp = ivs.timestamp.min()
    to_timestamp = ivs.timestamp.max()
    directory = f"data\\atm_ivs_new\\{underlying}"
    file_name = f"{underlying}_atm_ivs_{from_timestamp.strftime('%Y-%m-%d')}_{to_timestamp.strftime('%Y-%m-%d')}.csv"
    full_path = f"{directory}\\{file_name}"
    make_directory_if_needed(full_path)
    ivs.to_csv(full_path)


# Function to train and evaluate a single model
def evaluate_model(params, x_train, x_val, y_train, y_val):
    model = RandomForestRegressor(**params)
    x_train = x_train.copy()
    x_val = x_val.copy()
    y_train = y_train.copy()
    y_val = y_val.copy()
    model.fit(x_train, y_train)
    predictions = model.predict(x_val)
    mse = mean_squared_error(y_val, predictions)

    # Serialize model
    joblib.dump(model, "model.joblib")
    model_size = os.path.getsize("model.joblib")

    # Clean up the model file
    os.remove("model.joblib")

    return params, mse, model_size
