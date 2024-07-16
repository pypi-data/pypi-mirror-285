import os
import json
import numpy as np
from scipy.optimize import minimize
import pandas as pd
from volstreet import config
from volstreet.backtests.tools import nav_drawdown_analyser


def consolidate_backtest(path: str) -> pd.DataFrame:
    df = pd.DataFrame()
    for file in os.listdir(path):
        if file.endswith(".csv"):
            day_df = pd.read_csv(os.path.join(path, file))
            df = pd.concat([df, day_df])
    df["quantity"] = np.where(
        df["action"] == "BUY", 1 * df["quantity"], -1 * df["quantity"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)
    df = df.iloc[:, 1:]
    return df


def describe_backtest(dataframe: pd.DataFrame) -> pd.DataFrame:
    # -1 because we are selling the strangle
    all_days = dataframe.groupby(dataframe.index.date).agg(
        {"quantity": "sum", "value": ["sum", lambda x: x.abs().sum()]}
    )
    config.logger.info(f"Total number of days: {len(all_days)}")
    all_days.columns = ["quantity", "profit", "turnover"]
    all_days["exposure"] = 10000000
    all_days["profit"] *= -1
    all_days["profit_percentage"] = (all_days["profit"] / all_days["exposure"]) * 100
    invalid_days = all_days.query("quantity != 0").index
    all_days = all_days[all_days["quantity"] == 0].drop(columns="quantity")
    config.logger.info(
        f"Number of valid days: {len(all_days)}. Invalid days: {invalid_days}"
    )
    config.logger.info(
        f"Profit Margin: {(all_days.profit.sum() / all_days.turnover.sum()) * 100: 0.2f}%"
    )
    all_days = nav_drawdown_analyser(
        all_days, column_to_convert="profit_percentage", profit_in_pct=True
    )
    return all_days


def flatten_position_json(y):
    """Used to flatten the position details stored in the json format"""
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def load_position_details(path_to_folder: str) -> pd.DataFrame:
    json_data = []
    for file in os.listdir(path_to_folder):
        if file.endswith(".json") and "parameters" not in file:
            with open(f"{path_to_folder}\\{file}", "r") as f:
                data = json.load(f)
                json_data.extend(data)
    position_data = [flatten_position_json(x) for x in json_data]
    position_df = pd.DataFrame(position_data)
    position_df["timestamp"] = pd.to_datetime(position_df["timestamp"])
    return position_df


def reconcile_position_pnl_with_summary(
    position_dataframe: pd.DataFrame, summary_dataframe: pd.DataFrame
):
    eod_profit = position_dataframe.pivot_table(
        index=position_dataframe.index.date, values=["mtm"], aggfunc="last"
    )
    combined = eod_profit.merge(
        summary_dataframe[["profit"]], left_index=True, right_index=True
    )
    combined = combined.round(2)
    combined["difference"] = combined["mtm"] - combined["profit"]

    return combined["difference"].sum() == 0, combined


def get_optimized_weights(returns: pd.DataFrame):
    """Returns are the profit percentages for different strategies. The objective is to find the optimal weights"""

    def objective(x):
        nav_start = 100
        combined_profit_pcts = x.dot(returns.T)
        strat_nav = ((combined_profit_pcts + 100) / 100).cumprod() * nav_start
        cum_max = pd.Series(strat_nav).cummax().to_numpy()
        drawdown = ((strat_nav / cum_max) - 1) * 100
        cagr = ((strat_nav[-1] / 100) ** (1 / 1.5) - 1) * 100
        return abs(drawdown.min()) - np.log(cagr)

    solved = minimize(
        objective,
        x0=np.array([1 / returns.shape[1]] * returns.shape[1]),
        bounds=[(0, 1)] * returns.shape[1],
        constraints={"type": "eq", "fun": lambda x: x.sum() - 1},
    )

    optimal_weights = solved.x

    return optimal_weights


def get_optimized_returns(returns: pd.DataFrame, optimal_weights: np.array):
    optimal_returns = optimal_weights.dot(returns.T)
    optimal_returns = pd.Series(
        optimal_returns, index=returns.index, name="profit_percentage"
    ).to_frame()
    optimal_returns = nav_drawdown_analyser(
        optimal_returns, column_to_convert="profit_percentage", profit_in_pct=True
    )
    return optimal_returns
