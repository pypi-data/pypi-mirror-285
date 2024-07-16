from datetime import datetime, time
import pandas as pd
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from volstreet import config
from volstreet.utils import make_directory_if_needed, current_time, save_json_data
from volstreet.historical_info import market_days
from volstreet.backtests.underlying_info import UnderlyingInfo
from volstreet.backtests.proxy_functions import ProxyPriceFeed, ProxyFeeds


class Runner:
    def __init__(
        self,
        underlying: UnderlyingInfo,
        start_date: "datetime.date",
        end_date: "datetime.date",
        strategy: "BaseStrategy",
        parameters: dict,
        dte_list: list[int] = None,
        start_time: tuple[int, int] = (9, 16),
        end_time: tuple[int, int] = (15, 30),
        include_vix_data: bool = False,
        num_strikes_retrieved: int = 120,
        num_exp_retrieved: int = 1,
        end_directory: str = None,
    ):
        self.underlying = underlying
        self.start_date = start_date
        self.end_date = end_date
        self.dte_list = [0] if dte_list is None else dte_list
        self.strategy = strategy
        self.parameters = parameters
        self.start_time = start_time
        self.end_time = end_time
        self.include_vix_data = include_vix_data
        self.num_strikes_retrieved = num_strikes_retrieved
        self.num_exp_retrieved = num_exp_retrieved
        self.end_directory = end_directory

        # Post initialization
        self.price_feed = ProxyPriceFeed
        self.Index = __import__("volstreet.trade_interface").Index
        self.end_directory = self.make_result_directory(end_directory)

    def make_result_directory(self, end_directory):
        # Making a directory to store the results
        strategy = self.strategy.__name__
        index_strategy_directory = f"backtester\\{self.underlying.name}\\{strategy}\\"
        if end_directory is None:
            make_directory_if_needed(index_strategy_directory)
            folder_number = len(os.listdir(index_strategy_directory)) + 1
            end_directory = f"test_{folder_number}\\"

        end_directory = os.path.join(index_strategy_directory, f"{end_directory}\\")
        make_directory_if_needed(end_directory)
        return end_directory

    def run(self) -> pd.DataFrame:
        valid_range = pd.date_range(self.start_date, self.end_date)
        valid_range = [day.date() for day in valid_range if day.date() in market_days]

        target_days = []
        for dte in self.dte_list:
            target_days.extend([date for date in self.underlying.get_dte_list(dte)])
        target_days = list(sorted(target_days))
        target_days = [day for day in target_days if day in valid_range]

        # Dumping the parameters in the directory
        with open(os.path.join(self.end_directory, "parameters.json"), "w") as f:
            json.dump(self.parameters, f)

        with ThreadPoolExecutor(max_workers=3) as executor:
            daily_prices = [
                executor.submit(
                    self.price_feed.request_grouped_prices_for_day,
                    self.underlying,
                    day,
                    include_vix_data=self.include_vix_data,
                    num_strikes=self.num_strikes_retrieved,
                    num_exp=self.num_exp_retrieved,
                )
                for day in target_days
            ]

            error_list = []
            for daily_prices in as_completed(daily_prices):
                try:
                    date = daily_prices.result().timestamp.first().iloc[0].date()
                    self.price_feed._current_group = (
                        daily_prices.result()
                    )  # Updating prices
                    config.backtest_state = datetime.combine(
                        date, time(*self.start_time)
                    )  # State changes to the next day
                    self.price_feed.update_prices()  # data_bank gets updated
                    updated_index_instance = self.Index(
                        self.underlying.name
                    )  # Index instance gets updated
                    ProxyFeeds.order_feed = []  # Order feed gets reset
                    parameters = self.parameters.copy()
                    parameters["underlying"] = updated_index_instance
                    position_statuses = self.strategy.run_strategy(
                        parameters=parameters
                    )
                    # Storing the order data
                    day_result = ProxyFeeds.order_feed
                    result = pd.DataFrame(day_result)
                    filename = os.path.join(
                        self.end_directory, f"{current_time().strftime('%d-%m-%Y')}.csv"
                    )
                    result.to_csv(filename)

                    # Storing the position data if it exists
                    if position_statuses:
                        date = current_time().strftime("%d-%m-%Y")
                        filename = os.path.join(self.end_directory, f"{date}.json")
                        save_json_data(position_statuses, filename)

                except Exception as e:
                    config.logger.error(
                        f"Error in running the strategy {self.strategy.__name__} for {date}: {e}",
                        exc_info=True,
                    )
                    error_list.append(date)

            config.logger.info(
                f"Finished running the strategy {self.strategy.__name__} from {self.start_date} to {self.end_date}. "
                f"Total errors: {len(error_list)}. Error days: {error_list}"
            )
            return result


def get_parallel_runners(
    start_date: datetime,
    end_date: datetime,
    **kwargs,
):
    entire_date_range = pd.date_range(start_date, end_date, freq="B")
    if len(entire_date_range) < 6:
        return [
            Runner(
                start_date=start_date,
                end_date=end_date,
                **kwargs,
            )
        ]
    date_ranges = np.array_split(entire_date_range, 6)  # 6 processes
    runners = []
    for date_range in date_ranges:
        runner = Runner(
            start_date=date_range[0],
            end_date=date_range[-1],
            **kwargs,
        )
        runners.append(runner)
    return runners
