from abc import ABC, abstractmethod
import numpy as np
from time import sleep
from typing import Optional
from volstreet import config
from threading import Thread
from datetime import datetime, timedelta, time
from functools import partial
from types import MethodType
import traceback
from volstreet.config import logger
from volstreet.utils.core import (
    current_time,
    find_strike,
    time_to_expiry,
    check_for_weekend,
    calculate_ema,
    timed_executor,
    convert_exposure_to_lots,
)
from volstreet.utils.communication import notifier, log_error
from volstreet.utils.data_io import save_json_data
from volstreet.exceptions import IntrinsicValueError
from volstreet.blackscholes import simulate_price, calculate_strangle_iv
from volstreet.angel_interface.interface import (
    fetch_book,
    lookup_and_return,
    fetch_historical_prices,
)
from volstreet.angel_interface.active_session import ActiveSession
from volstreet.trade_interface import (
    Strangle,
    Straddle,
    Action,
    Index,
    Stock,
    IndiaVix,
    place_option_order_and_notify,
    execute_instructions,
    cancel_pending_orders,
)
from volstreet.strategies.helpers import (
    sleep_until_next_action,
    round_shares_to_lot_size,
    get_above_below_strangles_with_prices,
    disparity_calculator,
    identify_strangle,
    ActiveOption,
    DeltaPosition,
    TrendPosition,
    ReentryPosition,
    PositionMonitor,
    record_position_status,
    load_current_strangle,
    approve_execution,
    process_stop_loss_order_statuses,
)
from volstreet.strategies.monitoring import exit_positions, notify_pnl

if config.backtest_mode:
    from volstreet.backtests.proxy_functions import (
        execute_instructions,
        sleep_until_next_action,
    )


class BaseStrategy(ABC):
    def __init__(
        self,
        parameters: dict,
        indices: list[str],
        dtes: list[int],
        exposure: int | float = 0,  # This is not a compulsory parameter
        special_parameters: Optional[dict] = None,
        start_time: tuple = (9, 16),
        strategy_tag: Optional[str] = None,
        webhook_url: Optional[str] = None,
    ):
        self.exposure = exposure
        self.start_time = start_time
        self.dtes = dtes
        self.indices = indices
        self.parameters = parameters
        self.special_parameters = special_parameters or {}
        self.strategy_tag = strategy_tag or self.__class__.__name__
        self.webhook_url = webhook_url

        # Initialize attributes that will be set in `run`

        self.indices_to_trade = None
        self.combined_parameters = None
        self.strategy_threads = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"parameters="
            f"{self._truncate_or_str(self.parameters if self.parameters is not None else self.parameters)}, "
            f"indices={None if self.indices_to_trade is None else [index.name for index in self.indices_to_trade]}, "
            f"tags={self.strategy_tag}, "
        )

    @staticmethod
    def _truncate_or_str(obj, max_len=50):
        s = str(obj)
        return s if len(s) <= max_len else s[:max_len] + "..."

    @abstractmethod
    def logic(self, **kwargs):
        pass

    @classmethod
    def run_strategy(cls, parameters: dict, **kwargs) -> list[str]:
        """This is intended to run the strategy as a standalone instance.
        Hence, it requires the parameters dict to contain at least the essential parameters for the strategy.
        """
        strategy = cls(parameters=parameters, indices=[], dtes=[], **kwargs)
        if config.backtest_mode:
            return strategy.logic(**parameters)
        else:
            return strategy.run(**parameters)

    def no_trade(self):
        notifier(f"No {self.strategy_tag} trade today", self.webhook_url)

    def setup_thread(self, index: Index) -> Thread:
        index_parameters = self.combined_parameters[index.name]
        tag_formatted = self.strategy_tag.replace(" ", "_")
        return Thread(
            target=self.run,
            kwargs=index_parameters,
            name=f"{index.name}_{tag_formatted}".lower(),
        )

    def setup_threads(self, indices: list[Index]) -> list[Thread]:
        if len(indices) == 0:
            return [Thread(target=self.no_trade)]
        strategy_threads = [self.setup_thread(index) for index in indices]
        return strategy_threads

    def initialize_parameters(self, parameters, special_parameters) -> dict:
        """Returns a dictionary of parameters for each index and strategy tag."""

        # Since this function is called after set_parameters, parameters is a list of dictionaries
        # It is also called after initialize_indices, so indices_to_trade is already set
        # We will use both of this information to set quantities if exposure is given
        if self.exposure:
            exposure = self.exposure / len(self.indices_to_trade)
            parameters["exposure"] = exposure

        # Initialize final output dictionary
        combined_params = {}

        # Iterate through each index to populate final_parameters
        for index in self.indices_to_trade:
            index_params = parameters.copy()
            index_params["underlying"] = index
            index_params.update(special_parameters.get(index.name, {}))
            combined_params[index.name] = index_params
        logger.info(
            f"Initializing {self.__class__.__name__} with parameters: {combined_params}"
        )
        return combined_params

    def run(self, **kwargs):
        """The difference between this function and the logic function is that this function will handle all the
        error handling and notification sending. The logic function will only contain the logic of the strategy.
        """
        execution_time = current_time()
        underlying = kwargs.get("underlying").name
        exposure = kwargs.get("exposure")
        try:
            return self.logic(**kwargs)
        except Exception as e:
            user_prefix = config.ERROR_NOTIFICATION_SETTINGS.get("user")
            user_prefix = f"{user_prefix} - " if user_prefix else ""
            sleep(5)  # Sleep for 5 seconds to allow the orders to be filled
            notifier(
                f"{user_prefix}"
                f"Error in strategy {self.strategy_tag}: {e}\nTraceback:{traceback.format_exc()}\n\n"
                f"Exiting existing positions...",
                webhook_url=config.ERROR_NOTIFICATION_SETTINGS["url"],
                level="ERROR",
                send_whatsapp=True,
            )
            exit_positions(underlying, self.strategy_tag, execution_time)
        finally:
            sleep(10)  # Sleep for 10 seconds to allow the orders to be filled
            notify_pnl(
                underlying,
                self.strategy_tag,
                execution_time,
                exposure,
                self.webhook_url,
            )

    def run_all(self):
        """This function will run the strategy threads for each index, param combination.
        IMPORTANT: it will block until all threads are finished."""

        # Moved initialization methods here
        self.indices_to_trade = initialize_indices(self, self.indices, self.dtes)
        self.combined_parameters = self.initialize_parameters(
            self.parameters,
            self.special_parameters,
        )
        self.strategy_threads = self.setup_threads(self.indices_to_trade)

        logger.info(
            f"Waiting for {self.__class__.__name__} to start at {self.start_time}"
        )

        while current_time().time() < time(*self.start_time):
            sleep(1)

        # Start all threads
        for thread in self.strategy_threads:
            thread.start()

        # Join all threads
        for thread in self.strategy_threads:
            thread.join()


class QuickStrangle(BaseStrategy):

    def logic(
        self,
        underlying: Index | Stock,
        action: str,
        iv_threshold: float,
        take_profit: float,
        scan_exit_time: tuple[int, int],
        exposure: int | float = 0,
        investment: int | float = 0,
        stop_loss: Optional[float] = None,
        trade_exit_time: tuple[int, int] = (10, 10),
        at_market: bool = False,
    ):

        if not exposure and not investment:
            raise ValueError("Exposure or investment must be provided")

        DISPARITY_THRESHOLD = 0.2

        # Entering the main function
        if time(*scan_exit_time) < current_time().time():
            notifier(
                f"{underlying.name} {self.strategy_tag} not being deployed after exit time",
                self.webhook_url,
                "INFO",
            )
            return

        def fetch_spot_and_basis(underlying: Index, expiry: str) -> tuple[float, float]:
            spot_price = underlying.fetch_ltp()
            current_basis = underlying.get_basis_for_expiry(
                expiry=expiry, underlying_price=spot_price
            )
            return spot_price, current_basis

        def calculate_ivs(strangle, spot_price, r, prices):
            ivs = strangle.fetch_ivs(spot=spot_price, r=r, prices=prices)
            return np.mean(ivs)

        def disparity_check(call_ltp, put_ltp):
            disparity = disparity_calculator(call_ltp, put_ltp)
            return disparity < DISPARITY_THRESHOLD

        last_log_time = current_time()

        def log_iv_status():
            nonlocal ivs, last_log_time
            if current_time() - last_log_time > timedelta(seconds=0.1):
                logger.info(f"{underlying.name} {self.strategy_tag} IVs: {ivs}")
                last_log_time = current_time()

        def condition_triggered() -> bool | tuple[Strangle, float, float]:
            nonlocal ivs, action, iv_threshold, position
            if action == Action.BUY:
                strangle = min(ivs, key=ivs.get)
            else:
                strangle = max(ivs, key=ivs.get)
            iv = ivs[strangle]
            # noinspection PyTypeChecker
            total_price = np.sum(strangle.fetch_ltp(for_type=action.value))
            condition = (
                iv <= iv_threshold if action == Action.BUY else iv >= iv_threshold
            )

            if condition:
                position.position_active = True
                position.instrument = strangle
                position.initiating_price = total_price
                return True
            else:
                return False

        def profit_condition() -> bool:
            nonlocal action, total_current_price, position
            if action == Action.BUY:
                return total_current_price >= position.profit_threshold
            else:
                return total_current_price <= position.profit_threshold

        def stop_loss_condition() -> bool:
            nonlocal action, total_current_price, position

            if action == Action.BUY:
                return total_current_price <= position.stop_loss_threshold
            else:
                return total_current_price >= position.stop_loss_threshold

        strategy_tag = f"{self.strategy_tag} {action.upper()}"
        action = Action(action)
        expiry = underlying.current_expiry

        if stop_loss is None:
            stop_loss = np.nan

        position = PositionMonitor(underlying)

        while current_time().time() < time(*scan_exit_time):
            spot, basis = fetch_spot_and_basis(underlying, expiry)
            above_info, below_info = get_above_below_strangles_with_prices(
                underlying, spot, expiry, action.value
            )
            above_strangle, above_prices = above_info
            below_strangle, below_prices = below_info
            ivs = {}
            if disparity_check(*above_prices):
                ivs[above_strangle] = calculate_ivs(
                    above_strangle, spot, basis, above_prices
                )
            if disparity_check(*below_prices):
                ivs[below_strangle] = calculate_ivs(
                    below_strangle, spot, basis, below_prices
                )

            if not ivs:
                sleep(0.1)
                continue

            log_iv_status()

            if condition_triggered():
                if exposure != 0:
                    quantity_in_lots = convert_exposure_to_lots(
                        exposure, underlying.fetch_ltp(), underlying.lot_size
                    )
                elif investment != 0:
                    # Calculation of quantity
                    shares_to_buy = investment / position.initiating_price
                    shares_to_buy = round_shares_to_lot_size(
                        shares_to_buy, underlying.lot_size
                    )
                    quantity_in_lots = shares_to_buy / underlying.lot_size
                else:
                    raise ValueError("Exposure or investment must be provided")

                execution_details = execute_instructions(
                    {
                        position.instrument: {
                            "action": action,
                            "quantity_in_lots": quantity_in_lots,
                            "order_tag": strategy_tag,
                        }
                    },
                    at_market=at_market,
                )
                call_avg_price, put_avg_price = execution_details[position.instrument]

                notifier(
                    f"Entered {underlying.name} {strategy_tag} on {position.instrument} "
                    f"with avg price {call_avg_price + put_avg_price}",
                    self.webhook_url,
                    "INFO",
                )
                position.initiating_price = call_avg_price + put_avg_price
                break

            sleep(0.1)

        if not position.position_active:
            notifier(
                f"{underlying.name} {strategy_tag} not triggered. Exiting.",
                self.webhook_url,
            )
            return

        if position.position_active:
            position.profit_threshold = position.initiating_price * (
                1 + (take_profit * action.num_value)
            )
            position.stop_loss_threshold = position.initiating_price * (
                1 - (stop_loss * action.num_value)
            )
            while current_time().time() < time(*trade_exit_time):
                current_call_price, current_put_price = position.instrument.fetch_ltp(
                    for_type=(~action).value
                )
                total_current_price = current_call_price + current_put_price
                logger.info(
                    f"{underlying.name} {strategy_tag} Current price: {total_current_price} "
                    f"Target price: {position.profit_threshold} Stop loss price: {position.stop_loss_threshold}"
                )
                if profit_condition():
                    notifier(
                        f"{underlying.name} {strategy_tag} profit triggered. Exiting.",
                        self.webhook_url,
                    )
                    break
                if stop_loss_condition():
                    notifier(
                        f"{underlying.name} {strategy_tag} stop loss triggered. Exiting.",
                        self.webhook_url,
                    )
                    break

                sleep(0.1)

            # noinspection PyUnboundLocalVariable
            execution_details = execute_instructions(
                {
                    position.instrument: {
                        "action": ~action,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": strategy_tag,
                    }
                },
                at_market=at_market,
            )
            call_exit_price, put_exit_price = execution_details[position.instrument]
            exit_price = call_exit_price + put_exit_price
            profit_points = (exit_price - position.initiating_price) * action.num_value
            notifier(
                f"Exited {underlying.name} {strategy_tag} with profit points {profit_points}",
                self.webhook_url,
            )


class IntradayStrangle(BaseStrategy):

    def logic(
        self,
        underlying: Index | Stock,
        exposure: int | float,
        call_strike_offset: Optional[float] = 0,
        put_strike_offset: Optional[float] = 0,
        strike_selection: Optional[str] = "equal",
        stop_loss: Optional[float | str] = "dynamic",
        call_stop_loss: Optional[float] = None,
        put_stop_loss: Optional[float] = None,
        combined_stop_loss: Optional[float] = None,
        exit_time: tuple[int, int] = (15, 29),
        sleep_time: Optional[int] = 5,
        seconds_to_avg: Optional[int] = 30,
        simulation_safe_guard: Optional[float] = 1.15,
        catch_trend: Optional[bool] = False,
        trend_qty_ratio: Optional[float] = 1,
        place_trend_sl_orders: Optional[bool] = False,
        disparity_threshold: Optional[float] = 1000,
        place_sl_orders: Optional[bool] = False,
        move_sl_to_cost: Optional[bool] = False,
        place_orders_on_sl: Optional[bool] = False,
        convert_to_butterfly: Optional[bool] = False,
        conversion_method: Optional[str] = "pct",
        conversion_threshold_pct: Optional[float] = 0.175,
        take_profit: Optional[float] = 0,
    ):
        """Intraday strangle strategy. Trades strangle with stop loss. All offsets are in percentage terms.
        Parameters
        ----------
        underlying : Index | Stock
            Underlying object
        exposure : int | float
            Exposure in rupees
        strike_selection : str, optional {'equal', 'resilient', 'atm'}
            Mode for finding the strangle, by default 'equal'
        call_strike_offset : float, optional
            Call strike offset in percentage terms, by default 0
        put_strike_offset : float, optional
            Put strike offset in percentage terms, by default 0
        stop_loss : float or string, optional
            Stop loss percentage, by default 'dynamic'
        call_stop_loss : float, optional
            Call stop loss percentage, by default None. If None then stop loss is same as stop_loss.
        put_stop_loss : float, optional
            Put stop loss percentage, by default None. If None then stop loss is same as stop_loss.
        combined_stop_loss : float, optional
            Combined stop loss percentage, by default None. If None then individual stop losses are used.
        exit_time : tuple, optional
            Exit time, by default (15, 29)
        sleep_time : int, optional
            Sleep time in seconds for updating prices, by default 5
        seconds_to_avg : int, optional
            Seconds to average prices over, by default 30
        simulation_safe_guard : float, optional
            The multiple over the simulated price that will reject stop loss, by default 1.15
        catch_trend : bool, optional
            Catch trend or not, by default False
        trend_qty_ratio : int, optional
            Ratio of trend quantity to strangle quantity, by default 1
        place_trend_sl_orders : bool, optional
            Place stop loss order for trend or not, by default False
        disparity_threshold : float, optional
            Disparity threshold for equality of strikes, by default np.inf
        place_sl_orders : bool, optional
            Place stop loss orders or not, by default False
        move_sl_to_cost : bool, optional
            Move other stop loss to cost or not, by default False
        place_orders_on_sl : bool, optional
            Place orders on stop loss or not, by default False
        convert_to_butterfly : bool, optional
            Convert to butterfly or not, by default False
        conversion_method : str, optional
            Conversion method for butterfly, by default 'breakeven'
        conversion_threshold_pct : float, optional
            Conversion threshold for butterfly if conversion method is 'pct', by default 0.175
        take_profit : float, optional
            Take profit percentage, by default 0
        """

        @log_error(notify=True, raise_error=True)
        def position_monitor(info_dict):
            c_avg_price = info_dict["call_avg_price"]
            p_avg_price = info_dict["put_avg_price"]
            traded_strangle = info_dict["traded_strangle"]

            # EMA parameters
            periods = max(int(seconds_to_avg / sleep_time), 1) if sleep_time >= 1 else 1
            alpha = 2 / (periods + 1)
            ema_values = {
                "call": None,
                "put": None,
                "underlying": None,
            }

            # Conversion to butterfly settings
            ctb_notification_sent = False
            ctb_message = ""
            ctb_hedge = None
            conversion_threshold_break_even = None

            def process_ctb(
                h_strangle: Strangle,
                method: str,
                threshold_break_even: float,
                threshold_pct: float,
                total_price: float,
            ) -> bool:
                hedge_total_ltp = h_strangle.fetch_total_ltp()

                if method == "breakeven":
                    hedge_profit = total_price - hedge_total_ltp - underlying.base
                    return hedge_profit >= threshold_break_even

                elif method == "pct":
                    if (
                        total_price - (hedge_total_ltp + underlying.base)
                        < threshold_break_even
                    ):
                        return (
                            False  # Ensuring that this is better than break even method
                        )
                    return hedge_total_ltp <= total_price * threshold_pct

                else:
                    raise ValueError(
                        f"Invalid conversion method: {method}. Valid methods are 'breakeven' and 'pct'."
                    )

            if convert_to_butterfly:
                ctb_call_strike = traded_strangle.call_strike + underlying.base
                ctb_put_strike = traded_strangle.put_strike - underlying.base
                ctb_hedge = Strangle(
                    ctb_call_strike, ctb_put_strike, underlying.name, expiry
                )
                c_sl = call_stop_loss if call_stop_loss is not None else stop_loss
                p_sl = put_stop_loss if put_stop_loss is not None else stop_loss
                profit_if_call_sl = p_avg_price - (c_avg_price * (c_sl - 1))
                profit_if_put_sl = c_avg_price - (p_avg_price * (p_sl - 1))

                conversion_threshold_break_even = max(
                    profit_if_call_sl, profit_if_put_sl
                )

            threshold_points = (
                (take_profit * (c_avg_price + p_avg_price))
                if take_profit > 0
                else np.inf
            )

            last_print_time = current_time()
            last_log_time = current_time()
            last_notify_time = current_time()
            print_interval = timedelta(seconds=10)
            log_interval = timedelta(minutes=25)
            notify_interval = timedelta(minutes=180)

            while not info_dict["trade_complete"]:
                # Fetching prices
                spot_price = underlying.fetch_ltp()
                c_ltp, p_ltp = traded_strangle.fetch_ltp()
                info_dict["underlying_ltp"] = spot_price
                info_dict["call_ltp"] = c_ltp
                info_dict["put_ltp"] = p_ltp

                # Calculate EMA for each series
                for series, price in zip(
                    ["call", "put", "underlying"], [c_ltp, p_ltp, spot_price]
                ):
                    ema_values[series] = calculate_ema(price, ema_values[series], alpha)

                c_ltp_avg = ema_values["call"]
                p_ltp_avg = ema_values["put"]
                spot_price_avg = ema_values["underlying"]

                info_dict["call_ltp_avg"] = c_ltp_avg
                info_dict["put_ltp_avg"] = p_ltp_avg
                info_dict["underlying_ltp_avg"] = spot_price_avg

                # Combined stop loss detection
                if combined_stop_loss is not None and not np.isnan(combined_stop_loss):
                    if (c_ltp_avg + p_ltp_avg) > info_dict["combined_stop_loss_price"]:
                        info_dict["exit_triggers"].update({"combined_stop_loss": True})
                        notifier(
                            f"{underlying.name} Combined stop loss triggered with "
                            f"combined price of {c_ltp_avg + p_ltp_avg}",
                            self.webhook_url,
                            "INFO",
                        )

                # Calculate IV
                call_iv, put_iv, avg_iv = calculate_strangle_iv(
                    call_price=c_ltp,
                    put_price=p_ltp,
                    call_strike=traded_strangle.call_strike,
                    put_strike=traded_strangle.put_strike,
                    spot=spot_price,
                    time_left=time_to_expiry(expiry),
                )
                info_dict["call_iv"] = call_iv
                info_dict["put_iv"] = put_iv
                info_dict["avg_iv"] = avg_iv

                # Calculate mtm price
                call_exit_price = info_dict.get("call_exit_price", c_ltp)
                put_exit_price = info_dict.get("put_exit_price", p_ltp)
                mtm_price = call_exit_price + put_exit_price

                # Calculate profit
                profit_in_pts = (c_avg_price + p_avg_price) - mtm_price
                profit_in_rs = profit_in_pts * underlying.lot_size * quantity_in_lots
                info_dict["profit_in_pts"] = profit_in_pts
                info_dict["profit_in_rs"] = profit_in_rs

                if take_profit > 0:
                    if profit_in_pts >= threshold_points:
                        info_dict["exit_triggers"].update({"take_profit": True})
                        notifier(
                            f"{underlying.name} Take profit triggered with profit of {profit_in_pts} points",
                            self.webhook_url,
                            "INFO",
                        )

                # Conversion to butterfly working
                if (
                    not (info_dict["call_sl"] or info_dict["put_sl"])
                    and info_dict["time_left_day_start"] * 365 < 1
                    and convert_to_butterfly
                    and not ctb_notification_sent
                    and current_time().time() < time(14, 15)
                ):
                    try:
                        ctb_trigger = process_ctb(
                            ctb_hedge,
                            conversion_method,
                            conversion_threshold_break_even,
                            conversion_threshold_pct,
                            info_dict["total_avg_price"],
                        )
                        if ctb_trigger:
                            notifier(
                                f"{underlying.name} Convert to butterfly triggered\n",
                                self.webhook_url,
                                "INFO",
                            )
                            info_dict["exit_triggers"].update(
                                {"convert_to_butterfly": True}
                            )
                            ctb_message = f"Hedged with: {ctb_hedge}\n"
                            info_dict["ctb_hedge"] = ctb_hedge
                            ctb_notification_sent = True
                    except Exception as _e:
                        logger.error(f"Error in process_ctb: {_e}")

                message = (
                    f"\nUnderlying: {underlying.name}\n"
                    f"Time: {current_time(): %d-%m-%Y %H:%M:%S}\n"
                    f"Underlying LTP: {spot_price}\n"
                    f"Call Strike: {traded_strangle.call_strike}\n"
                    f"Put Strike: {traded_strangle.put_strike}\n"
                    f"Call Price: {c_ltp}\n"
                    f"Put Price: {p_ltp}\n"
                    f"MTM Price: {mtm_price}\n"
                    f"Call last n avg: {c_ltp_avg}\n"
                    f"Put last n avg: {p_ltp_avg}\n"
                    f"IVs: {call_iv}, {put_iv}, {avg_iv}\n"
                    f"Call SL: {info_dict['call_sl']}\n"
                    f"Put SL: {info_dict['put_sl']}\n"
                    f"Profit Pts: {info_dict['profit_in_pts']:.2f}\n"
                    f"Profit: {info_dict['profit_in_rs']:.2f}\n" + ctb_message
                )
                if current_time() - last_print_time > print_interval:
                    print(message)
                    last_print_time = current_time()
                if current_time() - last_log_time > log_interval:
                    logger.info(message)
                    last_log_time = current_time()
                if current_time() - last_notify_time > notify_interval:
                    notifier(message, self.webhook_url, "INFO")
                    last_notify_time = current_time()
                sleep(sleep_time)

        @log_error(raise_error=True, notify=True)
        def trend_catcher(info_dict, sl_type, qty_ratio):

            def check_trade_eligibility(option, price):
                if option.fetch_ltp() > price * 0.70:
                    return True

            traded_strangle = info_dict["traded_strangle"]
            og_price = (
                info_dict["call_avg_price"]
                if sl_type == "put"
                else info_dict["put_avg_price"]
            )
            trend_option = (
                traded_strangle.call_option
                if sl_type == "put"
                else traded_strangle.put_option
            )

            qty_in_lots = max(int(quantity_in_lots * qty_ratio), 1)

            while not check_trade_eligibility(
                trend_option, og_price
            ) and current_time().time() < time(*exit_time):
                sleep(sleep_time)

            # Placing the trend option order
            exec_details = execute_instructions(
                {
                    trend_option: {
                        "action": Action.SELL,
                        "quantity_in_lots": qty_in_lots,
                        "order_tag": f"{self.strategy_tag} Trend Catcher",
                    }
                }
            )
            sell_avg_price = exec_details[trend_option]

            # Setting up the stop loss on the trend option
            if place_trend_sl_orders:
                trend_sl_order_ids = place_option_order_and_notify(
                    instrument=trend_option,
                    action="BUY",
                    qty_in_lots=qty_in_lots,
                    prices=og_price,
                    order_tag=f"{self.strategy_tag} Trend Catcher",
                    webhook_url=self.webhook_url,
                    stop_loss_order=True,
                    target_status="trigger pending",
                    return_avg_price=False,
                )

            trend_sl_hit = False
            notifier(
                f"{underlying.name} strangle {sl_type} trend catcher starting. "
                f"Placed {qty_in_lots} lots of {trend_option} at {sell_avg_price}. "
                f"Stoploss prices: {og_price}",
                self.webhook_url,
                "INFO",
            )

            last_print_time = current_time()
            print_interval = timedelta(seconds=10)
            while all(
                [
                    current_time().time() < time(*exit_time),
                    not info_dict["trade_complete"],
                ]
            ):
                if place_trend_sl_orders:
                    orderbook = fetch_book("orderbook")
                    # noinspection PyUnboundLocalVariable
                    trend_sl_hit, _ = process_stop_loss_order_statuses(
                        orderbook,
                        trend_sl_order_ids,
                        context="Trend Sl",
                        notify_url=self.webhook_url,
                    )
                else:
                    option_price = trend_option.fetch_ltp()
                    trend_sl_hit = option_price >= og_price
                if trend_sl_hit:
                    break
                if current_time() - last_print_time > print_interval:
                    last_print_time = current_time()
                    logger.info(
                        f"{underlying.name} {sl_type} trend catcher running\n"
                        f"Stoploss price: {og_price}\n"
                    )
                sleep(sleep_time)

            # A boolean to check if the position is squared up
            # It is only true if the trend stop loss is hit and the orders were placed
            position_squared_up = trend_sl_hit and place_trend_sl_orders

            if position_squared_up:
                square_up_avg_price = (
                    lookup_and_return(
                        fetch_book("orderbook"),
                        "orderid",
                        trend_sl_order_ids,
                        "averageprice",
                    )
                    .astype(float)
                    .mean()
                )
            else:
                exec_details = execute_instructions(
                    {
                        trend_option: {
                            "action": Action.BUY,
                            "quantity_in_lots": qty_in_lots,
                            "order_tag": f"{self.strategy_tag} Trend Catcher",
                            "square_off_order": True,
                        }
                    }
                )
                square_up_avg_price = exec_details[trend_option]
                if place_trend_sl_orders:
                    cancel_pending_orders(trend_sl_order_ids, "STOPLOSS")

            points_captured = sell_avg_price - square_up_avg_price
            info_dict["trend_catcher_points_captured"] = points_captured

        def justify_stop_loss(info_dict, side):
            entry_spot = info_dict.get("spot_at_entry")
            current_spot = info_dict.get("underlying_ltp")
            stop_loss_price = info_dict.get(f"{side}_stop_loss_price")

            time_left_day_start = info_dict.get("time_left_day_start")
            time_left_now = time_to_expiry(expiry)
            time_delta_minutes = (time_left_day_start - time_left_now) * 525600
            time_delta_minutes = int(time_delta_minutes)
            time_delta_minutes = min(
                time_delta_minutes, 300
            )  # Hard coded number. At most 300 minutes and not more.
            try:
                simulated_option_price = simulate_price(
                    strike=(
                        info_dict.get("traded_strangle").call_strike
                        if side == "call"
                        else info_dict.get("traded_strangle").put_strike
                    ),
                    flag=side,
                    original_atm_iv=info_dict.get("atm_iv_at_entry"),
                    original_spot=entry_spot,
                    original_time_to_expiry=time_left_day_start,
                    new_spot=current_spot,
                    time_delta_minutes=time_delta_minutes,
                )
            except (Exception, IntrinsicValueError) as ex:
                error_message = (
                    f"Error in justify_stop_loss for {underlying.name} {side} strangle: {ex}\n"
                    f"Setting stop loss to True"
                )
                logger.error(error_message)
                notifier(error_message, self.webhook_url, "ERROR")
                return True

            actual_price = info_dict.get(f"{side}_ltp_avg")
            unjust_increase = (
                actual_price / simulated_option_price > simulation_safe_guard
                and simulated_option_price < stop_loss_price
            )
            if unjust_increase:
                if not info_dict.get(f"{side}_sl_check_notification_sent"):
                    message = (
                        f"{underlying.name} strangle {side} stop loss appears to be unjustified. "
                        f"Actual price: {actual_price}, Simulated price: {simulated_option_price}"
                    )
                    notifier(message, self.webhook_url, "CRUCIAL")
                    info_dict[f"{side}_sl_check_notification_sent"] = True

                # Additional check for unjustified stop loss (forcing stoploss to trigger even if unjustified only if
                # the price has increased by more than 2 times AND spot has moved by more than 0.5%)
                spot_change = (current_spot / entry_spot) - 1
                spot_moved = (
                    spot_change > 0.012 if side == "call" else spot_change < -0.0035
                )  # Hard coded number
                if (
                    spot_moved and (actual_price / stop_loss_price) > 1.6
                ):  # Hard coded number
                    message = (
                        f"{underlying.name} strangle {side} stop loss forced to trigger due to price increase. "
                        f"Price increase from stop loss price: {actual_price / simulated_option_price}"
                    )
                    notifier(message, self.webhook_url, "CRUCIAL")
                    return True
                else:
                    return False
            else:
                message = (
                    f"{underlying.name} strangle {side} stop loss triggered. "
                    f"Actual price: {actual_price}, Simulated price: {simulated_option_price}"
                )
                notifier(message, self.webhook_url, "CRUCIAL")
                return True

        def check_for_stop_loss(info_dict, side):
            """Check for stop loss."""

            stop_loss_order_ids = info_dict.get(f"{side}_stop_loss_order_ids")

            if stop_loss_order_ids is None:  # If stop loss order ids are not provided
                ltp_avg = info_dict.get(f"{side}_ltp_avg", info_dict.get(f"{side}_ltp"))
                stop_loss_price = info_dict.get(f"{side}_stop_loss_price")
                stop_loss_triggered = ltp_avg > stop_loss_price
                if stop_loss_triggered:
                    stop_loss_justified = justify_stop_loss(info_dict, side)
                    if stop_loss_justified:
                        info_dict[f"{side}_sl"] = True

            else:  # If stop loss order ids are provided
                orderbook = fetch_book("orderbook")
                orders_triggered, orders_complete = process_stop_loss_order_statuses(
                    orderbook,
                    stop_loss_order_ids,
                    context=side,
                    notify_url=self.webhook_url,
                )
                if orders_triggered:
                    justify_stop_loss(info_dict, side)
                    info_dict[f"{side}_sl"] = True
                    if not orders_complete:
                        info_dict[f"{side}_stop_loss_order_ids"] = None

        def process_stop_loss(info_dict, sl_type):
            if (
                info_dict["call_sl"] and info_dict["put_sl"]
            ):  # Check to avoid double processing
                return

            traded_strangle = info_dict["traded_strangle"]
            other_side: str = "call" if sl_type == "put" else "put"

            # Buying the stop loss option back if it is not already bought
            if info_dict[f"{sl_type}_stop_loss_order_ids"] is None:
                option_to_buy = (
                    traded_strangle.call_option
                    if sl_type == "call"
                    else traded_strangle.put_option
                )
                exec_details = execute_instructions(
                    {
                        option_to_buy: {
                            "action": Action.BUY,
                            "quantity_in_lots": quantity_in_lots,
                            "order_tag": self.strategy_tag,
                        }
                    }
                )
                exit_price = exec_details[option_to_buy]

            else:
                orderbook = fetch_book("orderbook")
                exit_price = (
                    lookup_and_return(
                        orderbook,
                        "orderid",
                        info_dict[f"{sl_type}_stop_loss_order_ids"],
                        "averageprice",
                    )
                    .astype(float)
                    .mean()
                )
            info_dict[f"{sl_type}_exit_price"] = exit_price

            if move_sl_to_cost:
                info_dict[f"{other_side}_stop_loss_price"] = info_dict[
                    f"{other_side}_avg_price"
                ]
                if (
                    info_dict[f"{other_side}_stop_loss_order_ids"] is not None
                    or place_orders_on_sl
                ):
                    if info_dict[f"{other_side}_stop_loss_order_ids"] is not None:
                        cancel_pending_orders(
                            info_dict[f"{other_side}_stop_loss_order_ids"], "STOPLOSS"
                        )
                    option_to_repair = (
                        traded_strangle.call_option
                        if other_side == "call"
                        else traded_strangle.put_option
                    )
                    info_dict[f"{other_side}_stop_loss_order_ids"] = (
                        place_option_order_and_notify(
                            instrument=option_to_repair,
                            action="BUY",
                            qty_in_lots=quantity_in_lots,
                            prices=info_dict[f"{other_side}_stop_loss_price"],
                            order_tag=f"{other_side.capitalize()} stop loss {self.strategy_tag}",
                            webhook_url=self.webhook_url,
                            stop_loss_order=True,
                            target_status="trigger pending",
                            return_avg_price=False,
                        )
                    )

            # Starting the trend catcher
            if catch_trend:
                trend_thread = Thread(
                    target=trend_catcher,
                    args=(
                        info_dict,
                        sl_type,
                        trend_qty_ratio,
                    ),
                    name=f"{underlying.name} {sl_type} trend catcher",
                )
                trend_thread.start()
                info_dict["active_threads"].append(trend_thread)

            sleep(
                5
            )  # To ensure that the stop loss orders are reflected in the orderbook

            # Wait for exit or other stop loss to hit
            while all(
                [
                    current_time().time() < time(*exit_time),
                    not info_dict["exit_triggers"]["take_profit"],
                ]
            ):
                check_for_stop_loss(info_dict, other_side)
                if info_dict[f"{other_side}_sl"]:
                    if info_dict[f"{other_side}_stop_loss_order_ids"] is None:
                        other_sl_option = (
                            traded_strangle.call_option
                            if other_side == "call"
                            else traded_strangle.put_option
                        )
                        notifier(
                            f"{underlying.name} strangle {other_side} stop loss hit.",
                            self.webhook_url,
                            "CRUCIAL",
                        )
                        exec_details = execute_instructions(
                            {
                                other_sl_option: {
                                    "action": Action.BUY,
                                    "quantity_in_lots": quantity_in_lots,
                                    "order_tag": self.strategy_tag,
                                }
                            }
                        )
                        other_exit_price = exec_details[other_sl_option]
                    else:
                        orderbook = fetch_book("orderbook")
                        other_exit_price = (
                            lookup_and_return(
                                orderbook,
                                "orderid",
                                info_dict[f"{other_side}_stop_loss_order_ids"],
                                "averageprice",
                            )
                            .astype(float)
                            .mean()
                        )
                    info_dict[f"{other_side}_exit_price"] = other_exit_price
                    break
                sleep(1)

        # Entering the main function
        if time(*exit_time) < current_time().time():
            notifier(
                f"{underlying.name} intraday strangle not being deployed after exit time",
                self.webhook_url,
                "INFO",
            )
            return
        expiry = underlying.current_expiry
        quantity_in_lots = convert_exposure_to_lots(
            exposure, underlying.fetch_ltp(), underlying.lot_size
        )

        if combined_stop_loss is None:
            # If combined stop loss is not provided, then it is set to np.nan, and
            # individual stop losses are calculated
            combined_stop_loss = np.nan
            # Setting stop loss
            stop_loss_dict = {
                "fixed": {"BANKNIFTY": 1.7, "NIFTY": 1.5},
                "dynamic": {"BANKNIFTY": 1.7, "NIFTY": 1.5},
            }

            if isinstance(stop_loss, str):
                if stop_loss == "dynamic" and time_to_expiry(expiry, in_days=True) < 1:
                    stop_loss = 1.7
                else:
                    stop_loss = stop_loss_dict[stop_loss].get(underlying.name, 1.6)
            else:
                stop_loss = stop_loss
        else:
            # If combined stop loss is provided, then individual stop losses are set to np.nan
            stop_loss = np.nan

        if strike_selection == "equal":
            strangle = identify_strangle(
                underlying=underlying,
                equality_constraint=True,
                call_strike_offset=call_strike_offset,
                put_strike_offset=put_strike_offset,
                disparity_threshold=disparity_threshold,
                range_of_strikes=1,
                exit_time=exit_time,
                expiry=expiry,
                notification_url=self.webhook_url,
            )
            if strangle is None:
                notifier(
                    f"{underlying.name} no strangle found within disparity threshold {disparity_threshold}",
                    self.webhook_url,
                    "INFO",
                )
                return
        elif strike_selection == "resilient":
            strangle = underlying.most_resilient_strangle(
                stop_loss=stop_loss, expiry=expiry
            )
        elif strike_selection == "atm":
            atm_strike = find_strike(underlying.fetch_ltp(), underlying.base)
            strangle = Strangle(atm_strike, atm_strike, underlying.name, expiry)
        else:
            raise ValueError(f"Invalid find mode: {strike_selection}")

        call_ltp, put_ltp = strangle.fetch_ltp()

        # Placing the main order
        execution_details = execute_instructions(
            {
                strangle: {
                    "action": Action.SELL,
                    "quantity_in_lots": quantity_in_lots,
                    "order_tag": self.strategy_tag,
                }
            }
        )
        call_avg_price, put_avg_price = execution_details[strangle]
        total_avg_price = call_avg_price + put_avg_price

        # Calculating stop loss prices
        call_stop_loss_price = (
            call_avg_price * call_stop_loss
            if call_stop_loss
            else call_avg_price * stop_loss
        )
        put_stop_loss_price = (
            put_avg_price * put_stop_loss
            if put_stop_loss
            else put_avg_price * stop_loss
        )
        combined_stop_loss_price = total_avg_price * combined_stop_loss

        underlying_ltp = underlying.fetch_ltp()

        # Logging information and sending notification
        trade_log = {
            "Time": current_time().strftime("%d-%m-%Y %H:%M:%S"),
            "Index": underlying.name,
            "Underlying price": underlying_ltp,
            "Call strike": strangle.call_strike,
            "Put strike": strangle.put_strike,
            "Expiry": expiry,
            "Action": "SELL",
            "Call price": call_avg_price,
            "Put price": put_avg_price,
            "Total price": total_avg_price,
            "Order tag": self.strategy_tag,
        }

        summary_message = "\n".join(f"{k}: {v}" for k, v in trade_log.items())

        # Setting the IV information at entry

        traded_call_iv, traded_put_iv, traded_avg_iv = calculate_strangle_iv(
            call_price=call_avg_price,
            put_price=put_avg_price,
            call_strike=strangle.call_strike,
            put_strike=strangle.put_strike,
            spot=underlying_ltp,
            time_left=time_to_expiry(expiry),
        )
        try:
            atm_iv_at_entry = underlying.fetch_atm_info()["avg_iv"]
        except Exception as e:
            logger.error(f"Error in fetching ATM IV: {e}")
            atm_iv_at_entry = np.nan
        time_left_at_trade = time_to_expiry(expiry)

        # Sending the summary message
        summary_message += (
            f"\nTraded IVs: {traded_call_iv}, {traded_put_iv}, {traded_avg_iv}\n"
            f"ATM IV at entry: {atm_iv_at_entry}\n"
            f"Call SL: {call_stop_loss_price}, Put SL: {put_stop_loss_price}\n"
            f"Combined SL: {combined_stop_loss_price}\n"
        )
        notifier(summary_message, self.webhook_url, "INFO")

        if place_sl_orders:
            call_stop_loss_order_ids = place_option_order_and_notify(
                instrument=strangle.call_option,
                action="BUY",
                qty_in_lots=quantity_in_lots,
                prices=call_stop_loss_price,
                order_tag=self.strategy_tag,
                webhook_url=self.webhook_url,
                stop_loss_order=True,
                target_status="trigger pending",
                return_avg_price=False,
            )
            put_stop_loss_order_ids = place_option_order_and_notify(
                instrument=strangle.put_option,
                action="BUY",
                qty_in_lots=quantity_in_lots,
                prices=put_stop_loss_price,
                order_tag=self.strategy_tag,
                webhook_url=self.webhook_url,
                stop_loss_order=True,
                target_status="trigger pending",
                return_avg_price=False,
            )
        else:
            call_stop_loss_order_ids = None
            put_stop_loss_order_ids = None

        # Setting up shared info dict
        shared_info_dict = {
            "traded_strangle": strangle,
            "spot_at_entry": underlying_ltp,
            "call_avg_price": call_avg_price,
            "put_avg_price": put_avg_price,
            "total_avg_price": total_avg_price,
            "atm_iv_at_entry": atm_iv_at_entry,
            "call_stop_loss_price": call_stop_loss_price,
            "put_stop_loss_price": put_stop_loss_price,
            "combined_stop_loss_price": combined_stop_loss_price,
            "call_stop_loss_order_ids": call_stop_loss_order_ids,
            "put_stop_loss_order_ids": put_stop_loss_order_ids,
            "time_left_day_start": time_left_at_trade,
            "call_ltp": call_ltp,
            "put_ltp": put_ltp,
            "underlying_ltp": underlying_ltp,
            "call_iv": traded_call_iv,
            "put_iv": traded_put_iv,
            "avg_iv": traded_avg_iv,
            "call_sl": False,
            "put_sl": False,
            "exit_triggers": {
                "convert_to_butterfly": False,
                "take_profit": False,
                "combined_stop_loss": False,
            },
            "trade_complete": False,
            "call_sl_check_notification_sent": False,
            "put_sl_check_notification_sent": False,
            "active_threads": [],
            "trend_catcher_points_captured": 0,
        }

        position_monitor_thread = Thread(
            target=position_monitor,
            args=(shared_info_dict,),
            name="Intraday Strangle Position Monitor",
        )
        position_monitor_thread.start()
        shared_info_dict["active_threads"].append(position_monitor_thread)
        sleep(
            5
        )  # To ensure that the position monitor thread has started and orders are reflected in the orderbook

        # Wait for exit time or both stop losses to hit (Main Loop)
        while all(
            [
                current_time().time() < time(*exit_time),
                not any(shared_info_dict["exit_triggers"].values()),
            ]
        ):
            if combined_stop_loss is not None and not np.isnan(combined_stop_loss):
                pass
            else:
                check_for_stop_loss(shared_info_dict, "call")
                if shared_info_dict["call_sl"]:
                    process_stop_loss(shared_info_dict, "call")
                    break
                check_for_stop_loss(shared_info_dict, "put")
                if shared_info_dict["put_sl"]:
                    process_stop_loss(shared_info_dict, "put")
                    break
            sleep(1)

        # Out of the while loop, so exit time reached or both stop losses hit, or we are hedged

        # If we are hedged then wait till exit time
        # noinspection PyTypeChecker
        if shared_info_dict["exit_triggers"]["convert_to_butterfly"]:
            hedge_strangle = shared_info_dict["ctb_hedge"]
            execute_instructions(
                {
                    hedge_strangle: {
                        "action": Action.BUY,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": self.strategy_tag,
                    }
                }
            )
            if place_sl_orders:
                cancel_pending_orders(
                    shared_info_dict["call_stop_loss_order_ids"]
                    + shared_info_dict["put_stop_loss_order_ids"]
                )
            notifier(
                f"{underlying.name}: Converted to butterfly", self.webhook_url, "INFO"
            )
            while current_time().time() < time(*exit_time):
                sleep(3)

        call_sl = shared_info_dict["call_sl"]
        put_sl = shared_info_dict["put_sl"]

        if not call_sl and not put_sl:  # Both stop losses not hit
            execution_details = execute_instructions(
                {
                    strangle: {
                        "action": Action.BUY,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": self.strategy_tag,
                    }
                }
            )
            call_exit_avg_price, put_exit_avg_price = execution_details[strangle]

            # noinspection PyTypeChecker
            if (
                place_sl_orders
                and not shared_info_dict["exit_triggers"]["convert_to_butterfly"]
            ):
                cancel_pending_orders(
                    shared_info_dict["call_stop_loss_order_ids"]
                    + shared_info_dict["put_stop_loss_order_ids"]
                )
            shared_info_dict["call_exit_price"] = call_exit_avg_price
            shared_info_dict["put_exit_price"] = put_exit_avg_price

        elif (call_sl or put_sl) and not (call_sl and put_sl):  # Only one stop loss hit
            exit_option_type: str = "put" if call_sl else "call"
            exit_option = strangle.put_option if call_sl else strangle.call_option
            execution_details = execute_instructions(
                {
                    exit_option: {
                        "action": Action.BUY,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": self.strategy_tag,
                    }
                }
            )
            non_sl_exit_price = execution_details[exit_option]
            if place_sl_orders or place_orders_on_sl:
                cancel_pending_orders(
                    shared_info_dict[f"{exit_option_type}_stop_loss_order_ids"]
                )
            shared_info_dict[f"{exit_option_type}_exit_price"] = non_sl_exit_price

        else:  # Both stop losses hit
            pass

        shared_info_dict["trade_complete"] = True
        for thread in shared_info_dict["active_threads"]:
            thread.join()

        # Calculate profit
        total_exit_price = (
            shared_info_dict["call_exit_price"] + shared_info_dict["put_exit_price"]
        )
        # Exit message
        exit_message = (
            f"{underlying.name} strangle exited.\n"
            f"Time: {current_time(): %d-%m-%Y %H:%M:%S}\n"
            f"Underlying LTP: {shared_info_dict['underlying_ltp']}\n"
            f"Call Price: {shared_info_dict['call_ltp']}\n"
            f"Put Price: {shared_info_dict['put_ltp']}\n"
            f"Call SL: {shared_info_dict['call_sl']}\n"
            f"Put SL: {shared_info_dict['put_sl']}\n"
            f"Call Exit Price: {shared_info_dict['call_exit_price']}\n"
            f"Put Exit Price: {shared_info_dict['put_exit_price']}\n"
            f"Total Exit Price: {total_exit_price}\n"
            f"Total Entry Price: {total_avg_price}\n"
            f"Profit Points: {total_avg_price - total_exit_price}\n"
            f"Chase Points: {shared_info_dict['trend_catcher_points_captured']}\n"
        )
        # Exit dict
        exit_dict = {
            "Call exit price": shared_info_dict["call_exit_price"],
            "Put exit price": shared_info_dict["put_exit_price"],
            "Total exit price": total_exit_price,
            "Points captured": total_avg_price - total_exit_price,
            "Call stop loss": shared_info_dict["call_sl"],
            "Put stop loss": shared_info_dict["put_sl"],
            "Trend catcher points": shared_info_dict["trend_catcher_points_captured"],
        }

        notifier(exit_message, self.webhook_url, "CRUCIAL")
        trade_log.update(exit_dict)

        return shared_info_dict


class TrendV2(BaseStrategy):

    def logic(
        self,
        underlying: Index | Stock,
        exposure: int | float,
        exit_time: tuple[int, int] = (15, 27),
        threshold_movement: Optional[float] = None,
        beta: Optional[float] = 0.8,
        stop_loss: Optional[float] = 0.003,
        hedge_offset: Optional[float | bool] = 0.004,
        optimized: bool = False,
        target_delta: float = 0.65,
        theta_time_jump_hours: int = 6,  # In hours
        max_entries: Optional[int] = 3,
        at_market: bool = False,
    ) -> list[dict]:
        # Entering the main function
        if time(*exit_time) < current_time().time():
            notifier(
                f"{underlying.name} {self.strategy_tag} not being deployed after exit time",
                self.webhook_url,
                "INFO",
            )
            return []

        # Quantity
        spot_price = underlying.fetch_ltp()
        quantity_in_shares = round_shares_to_lot_size(
            exposure / spot_price, underlying.lot_size
        )

        # Fetching open price
        if current_time().time() > time(9, 18):
            try:
                open_time = current_time().replace(hour=9, minute=16, second=0)
                open_price_data = fetch_historical_prices(
                    underlying.token, "ONE_MINUTE", open_time, open_time
                )
                open_price = open_price_data[0][1]
            except Exception as e:
                notifier(
                    f"Error in fetching historical prices: {e}",
                    self.webhook_url,
                    "INFO",
                )
                open_price = underlying.fetch_ltp()
        else:
            while current_time().time() < time(9, 16):
                sleep(1)
            open_price = underlying.fetch_ltp()

        # Threshold movement and price boundaries
        threshold_movement = (
            threshold_movement or (IndiaVix.fetch_ltp() * (beta or 1)) / 48
        )
        price_boundaries = [
            open_price * (1 + ((-1) ** i) * threshold_movement / 100) for i in range(2)
        ]

        # Exit time
        exit_time_object = time(*exit_time)
        scan_end_time = (
            datetime.combine(current_time().date(), exit_time_object)
            - timedelta(minutes=10)
        ).time()

        # Initializing the trend position manager
        greek_settings = {"theta_time_jump": theta_time_jump_hours / (365 * 24)}
        trend_position = TrendPosition(
            underlying=underlying,
            base_exposure_qty=quantity_in_shares,
            greek_settings=greek_settings,
            notifier_url=self.webhook_url,
            order_tag=self.strategy_tag,
        )
        trend_position.set_options()

        # The file name for recording the position status
        date = current_time().strftime("%d-%m-%Y")
        file_name = (
            f"{ActiveSession.obj.userId}\\"
            f"{underlying.name.lower()}_{self.strategy_tag.lower().strip().replace(' ', '_')}\\"
            f"{date}.json"
        )

        notifier(
            f"{underlying.name} trend following starting with {threshold_movement:0.2f} threshold movement\n"
            f"Current Price: {open_price}\nUpper limit: {price_boundaries[0]:0.2f}\n"
            f"Lower limit: {price_boundaries[1]:0.2f}.",
            self.webhook_url,
            "INFO",
        )
        recording_task = partial(record_position_status, trend_position, file_name)
        recording_task = timed_executor(55)(recording_task)
        entries = 0
        movement = 0
        while entries < max_entries and current_time().time() < exit_time_object:

            # Scan for entry condition
            notifier(
                f"{underlying.name} trender {entries + 1} scanning for entry condition.",
                self.webhook_url,
                "INFO",
            )
            while current_time().time() < scan_end_time:
                ltp = underlying.fetch_ltp()
                movement = (ltp - open_price) / open_price * 100
                if abs(movement) > threshold_movement:
                    break
                sleep_until_next_action(1, exit_time)

            if current_time().time() >= scan_end_time:
                notifier(
                    f"{underlying.name} trender {entries + 1} exiting due to time.",
                    self.webhook_url,
                    "CRUCIAL",
                )
                break

            # Entry condition met taking position
            price = underlying.fetch_ltp()
            action: Action = Action.BUY if movement > 0 else Action.SELL
            stop_loss_price = price * (
                (1 - stop_loss) if action == Action.BUY else (1 + stop_loss)
            )
            notifier(
                f"{underlying.name} {action} trender triggered with {movement:0.2f} movement. "
                f"{underlying.name} at {price}. "
                f"Stop loss at {stop_loss_price}.",
                self.webhook_url,
                "INFO",
            )

            # Set quantities and enter the position
            trend_position.set_recommended_qty(
                optimized=optimized,
                target_delta=target_delta,
                trend_direction=action,
                hedge_offset=hedge_offset,
            )
            trend_position.enter_positions(at_market=at_market)

            notifier(
                f"{underlying.name} {action} trender {entries + 1} entered.",
                self.webhook_url,
                "INFO",
            )

            # Monitoring begins
            stop_loss_hit = False
            early_exit = False

            # 15% of the quantity will be the delta threshold
            exit_threshold = 0.15 * quantity_in_shares

            while current_time().time() < exit_time_object:
                sleep_until_next_action(
                    1,
                    exit_time,
                    tasks_to_perform=[recording_task],
                )
                ltp = underlying.fetch_ltp()
                movement = (ltp - open_price) / open_price * 100
                stop_loss_hit = (
                    (ltp < stop_loss_price)
                    if action == Action.BUY
                    else (ltp > stop_loss_price)
                )
                if stop_loss_hit:
                    break
                if abs(trend_position.aggregate_greeks().delta) < exit_threshold:
                    notifier(
                        f"{underlying.name} trender {entries + 1} delta threshold hit.",
                        self.webhook_url,
                        "INFO",
                    )
                    early_exit = True
                    break

            # Exit condition met exiting position (stop loss or time)
            stop_loss_message = f"Trender stop loss hit. " if stop_loss_hit else ""
            notifier(
                f"{stop_loss_message}{underlying.name} trender {entries + 1} exiting.",
                self.webhook_url,
                "CRUCIAL",
            )
            trend_position.exit_positions(at_market=at_market)
            notifier(
                f"{underlying.name} {action} trender {entries + 1} exited.",
                self.webhook_url,
                "INFO",
            )
            entries += 1
            if early_exit:
                break

        return trend_position.position_statuses


class DeltaHedgedStrangle(BaseStrategy):

    def logic(
        self,
        underlying: Index | Stock,
        exposure: int | float,
        delta_threshold_pct: float = 0.04,
        target_delta: float = 0.1,
        delta_cutoff: float = 0.65,
        optimized: bool = True,
        optimize_gamma: bool = False,
        theta_time_jump_hours: float = 1,  # In hours
        delta_interval_minutes: int | float = 1,
        interrupt: bool = False,
        handle_spikes: bool = False,
        exit_time: Optional[tuple] = (15, 29),
        use_cache: Optional[bool] = True,
        at_market: bool = False,
    ) -> list[dict]:
        """Theta time jump is defined in hours. Delta interval is in minutes. Delta threshold is in percentage terms
        eg: 0.02 for 2%
        """

        base_exposure = exposure

        # Entering the main function
        if time(*exit_time) < current_time().time():
            notifier(
                f"{underlying.name} {self.strategy_tag} not being deployed after exit time",
                self.webhook_url,
                "INFO",
            )
            return []

        # Setting the exit time
        if time_to_expiry(underlying.current_expiry, in_days=True) < 1:
            exit_time = min([tuple(exit_time), (14, 40)])
            logger.info(
                f"{underlying.name} exit time changed to {exit_time} because expiry is today"
            )

        # Setting caching
        underlying.caching = use_cache

        # Setting the initial position size
        spot_price = underlying.fetch_ltp()
        max_qty_shares = round_shares_to_lot_size(
            exposure / spot_price, underlying.lot_size
        )
        base_qty_shares = round_shares_to_lot_size(
            base_exposure / spot_price, underlying.lot_size
        )

        # Setting the delta threshold
        delta_adjustment_threshold = delta_threshold_pct * base_qty_shares
        starting_message = (
            f"{underlying.name} {self.strategy_tag}, "
            f"exposure: {exposure}, "
            f"max qty: {max_qty_shares}, "
            f"base qty: {base_qty_shares}, "
            f"delta threshold: {delta_adjustment_threshold}. "
        )
        notifier(starting_message, self.webhook_url, "INFO")

        delta_position: DeltaPosition = DeltaPosition(
            underlying=underlying,
            base_exposure_qty=base_qty_shares,
            greek_settings={"theta_time_jump": theta_time_jump_hours / (365 * 24)},
            exit_triggers={"end_time": False, "qty_breach_exit": False},
            order_tag=self.strategy_tag,
            notifier_url=self.webhook_url,
        )

        def interruption_condition():
            # Hard coded 15% of base qty shares as the threshold for interruption
            condition_1 = (
                (
                    abs(delta_position.aggregate_greeks().delta)
                    >= (0.15 * base_qty_shares)
                )
                if interrupt
                else False
            )
            condition_2 = False  # todo: Add a condition that always maximizes Theta
            return condition_1 or condition_2

        date = current_time().strftime("%d-%m-%Y")
        file_name = (
            f"{ActiveSession.obj.userId}\\"
            f"{underlying.name.lower()}_{self.strategy_tag.lower().strip().replace(' ', '_')}\\"
            f"{date}.json"
        )

        delta_position.set_options()
        recording_task = partial(record_position_status, delta_position, file_name)
        recording_task = timed_executor(55)(recording_task)
        while current_time().time() < time(*exit_time):
            delta_position.update_underlying()
            delta_position.set_recommended_qty(
                target_delta, delta_cutoff, optimized, optimize_gamma
            )
            delta_position.adjust_recommended_qty()
            delta_position.enter_positions(at_market=at_market)

            # Delta hedging begins here
            while not any(delta_position.exit_triggers.values()):
                # delta_position.get_position_status()  # Storing the position status before the sleep
                sleep_until_next_action(
                    delta_interval_minutes,
                    exit_time,
                    tasks_to_perform=[recording_task],
                    interruption_condition=interruption_condition,
                )
                if current_time().time() >= time(*exit_time):
                    delta_position.exit_triggers["end_time"] = True
                    break

                delta_position.update_underlying()
                aggregate_delta: float = (
                    delta_position.aggregate_greeks().delta
                )  # The prices and greeks of the options are updated and cached here

                #  If aggregate delta breaches the threshold then adjust
                if abs(aggregate_delta) > delta_adjustment_threshold:
                    # We have already encountered a spike, check if its recent
                    if handle_spikes and delta_position.spike_start_time is not None:
                        spike = (
                            current_time() - delta_position.spike_start_time
                        ) < timedelta(minutes=5)
                        if not spike:
                            delta_position.spike_start_time = None
                    # Else check for new spike
                    elif handle_spikes:
                        spike = delta_position.check_for_iv_spike(aggregate_delta)
                        if spike:
                            delta_position.spike_start_time = current_time()
                    else:
                        spike = False

                    if spike:
                        # todo: Need a condition here to check if we are overshooting qtys
                        notifier(
                            f"{underlying.name} IV spike detected.",
                            self.webhook_url,
                            "INFO",
                        )
                        adj_func = partial(
                            delta_position.set_hedge_qty,
                            aggregate_delta,
                        )
                        delta_position.modify_positions(adj_func, at_market=at_market)
                        notifier(
                            f"{underlying.name} IV spike handled.",
                            self.webhook_url,
                            "INFO",
                        )
                        continue
                    # We will end up here if we are not hedging with atm options or if there is a breach
                    delta_position.exit_triggers["qty_breach_exit"] = True
                    message = (
                        f"{underlying.name} delta breached. Shuffling positions. "
                        f"Delta: {aggregate_delta}, "
                        f"Threshold: {delta_adjustment_threshold}. "
                    )
                    logger.info(message)

        # Exiting the position
        message = f"{underlying.name} {self.strategy_tag} exit time reached."
        notifier(message, self.webhook_url, "INFO")
        delta_position.exit_positions(at_market=at_market)

        return delta_position.position_statuses


class ReentryStraddle(BaseStrategy):

    def logic(
        self,
        underlying: Index | Stock,
        exposure: int | float,
        strike_offset: float = 0,
        call_strike_offset: float = None,
        put_strike_offset: float = None,
        equality_constraint: bool = True,
        call_stop_loss: Optional[float] = None,
        put_stop_loss: Optional[float] = None,
        stop_loss: Optional[float] = 0.5,
        call_reentries: int = None,
        put_reentries: int = None,
        reentries: int = 1,
        adjust_stop_loss: bool = False,
        move_other_to_cost: bool = False,
        diversify_time: tuple[int, int] = None,
        exit_time: tuple[int, int] = (15, 29),
        sleep_duration: int = 1,
        at_market: bool = False,
    ) -> list[dict]:

        if time(*exit_time) < current_time().time():
            notifier(
                f"{underlying.name} {self.strategy_tag} not being deployed after exit time",
                self.webhook_url,
                "INFO",
            )
            return []

        # Setting up option specific parameters
        call_stop_loss = call_stop_loss or stop_loss
        put_stop_loss = put_stop_loss or stop_loss
        call_strike_offset = (
            strike_offset if call_strike_offset is None else call_strike_offset
        )
        put_strike_offset = (
            -strike_offset if put_strike_offset is None else put_strike_offset
        )

        # Now if diversify_time is None we proceed with the most equal strangle
        if diversify_time is None:
            # Identifying the strangle
            strangle = identify_strangle(
                underlying,
                equality_constraint=equality_constraint,
                call_strike_offset=call_strike_offset,
                put_strike_offset=put_strike_offset,
                range_of_strikes=1,
            )
        else:
            time_now = current_time()
            diversify_time = datetime.combine(time_now.date(), time(*diversify_time))
            sleep_time_minutes = (diversify_time - time_now).total_seconds() / 60
            sleep_until_next_action(
                interval_minutes=sleep_time_minutes, exit_time=exit_time
            )
            logger.info(f"{underlying.name} diversifying at {diversify_time}")
            previous_strangle = identify_strangle(
                underlying,
                equality_constraint=equality_constraint,
                call_strike_offset=call_strike_offset,
                put_strike_offset=put_strike_offset,
                range_of_strikes=1,
            )
            # noinspection PyUnboundLocalVariable
            time_now = current_time()
            actual_start_time = diversify_time + timedelta(minutes=30)  # Hardcoded
            # minutes delay from last diversification
            sleep_time_minutes = (actual_start_time - time_now).total_seconds() / 60
            sleep_until_next_action(
                interval_minutes=sleep_time_minutes, exit_time=exit_time
            )

            # Now we start tracking the trade-able strangle until the cut_off time is reached
            cutoff_time = actual_start_time + timedelta(minutes=15)  # Hardcoded
            strangle = None
            while current_time() < cutoff_time:
                strangle = identify_strangle(
                    underlying,
                    equality_constraint=equality_constraint,
                    call_strike_offset=call_strike_offset,
                    put_strike_offset=put_strike_offset,
                    range_of_strikes=1,
                )
                if strangle != previous_strangle:
                    logger.info(
                        f"{underlying.name} diversification strangle found: {strangle}"
                    )
                    break
                sleep_until_next_action(interval_minutes=0.02, exit_time=exit_time)

        # Setting the base exposure qty
        spot_price = underlying.fetch_ltp()
        quantity_in_shares = round_shares_to_lot_size(
            exposure / spot_price, underlying.lot_size
        )

        reentry_position = ReentryPosition(
            underlying=underlying,
            base_exposure_qty=quantity_in_shares,
            notifier_url=self.webhook_url,
            order_tag=self.strategy_tag,
        )

        # Position status file name
        date = current_time().strftime("%d-%m-%Y")
        file_name = (
            f"{ActiveSession.obj.userId}\\"
            f"{underlying.name.lower()}_{self.strategy_tag.lower().strip().replace(' ', '_')}\\"
            f"{date}.json"
        )

        call_active_option = ActiveOption.from_option(strangle.call_option, underlying)
        put_active_option = ActiveOption.from_option(strangle.put_option, underlying)
        reentry_position.set_options(
            calls=[call_active_option], puts=[put_active_option]
        )

        def get_state() -> str:
            return (
                "neutral"
                if len(reentry_position.active_options) == 2
                else "directional"
            )

        def new_append_position_status(self, **additional_info) -> None:
            self._append_position_status(state=get_state(), **additional_info)

        reentry_position._append_position_status = (
            reentry_position.append_position_status
        )
        reentry_position.append_position_status = MethodType(
            new_append_position_status, reentry_position
        )

        # Entering the positions
        reentry_position.set_main_entry_recommendation()
        execution_details = reentry_position.enter_positions(at_market=at_market)

        def set_stop_loss(opt: ActiveOption, selling_price: float) -> None:
            opt.stop_loss = selling_price * (1 + opt.stop_loss_pct)

        # Setting the avg price, stop loss and reentries for the active options
        call_active_option.avg_price = execution_details[call_active_option]
        call_active_option.stop_loss_pct = call_stop_loss
        set_stop_loss(call_active_option, execution_details[call_active_option])
        call_active_option.reentries = call_reentries or reentries

        put_active_option.avg_price = execution_details[put_active_option]
        put_active_option.stop_loss_pct = put_stop_loss
        set_stop_loss(put_active_option, execution_details[put_active_option])
        put_active_option.reentries = put_reentries or reentries

        notifier(
            f"{underlying.name} {self.strategy_tag} starting with "
            f"straddle {strangle} and prices {(call_active_option.avg_price, put_active_option.avg_price)}",
            self.webhook_url,
            "INFO",
        )

        recording_task = partial(record_position_status, reentry_position, file_name)
        recording_task = timed_executor(55)(recording_task)
        while current_time().time() < time(*exit_time):
            if all(
                [
                    call_active_option.active_qty == 0,
                    put_active_option.active_qty == 0,
                    call_active_option.reentries == 0,
                    put_active_option.reentries == 0,
                ]
            ):
                notifier(
                    f"{underlying.name} {self.strategy_tag} all positions exited.",
                    self.webhook_url,
                    "INFO",
                )
                return reentry_position.position_statuses

            sleep_until_next_action(
                sleep_duration,
                exit_time,
                tasks_to_perform=[recording_task],
            )

            for option in reentry_position.all_options:
                # If it has an active qty check for sl
                if option.active_qty != 0:
                    if option.fetch_ltp() >= option.stop_loss:
                        adj_func = partial(
                            reentry_position.adjust_qty_for_option,
                            option=option,
                            stop_loss=True,
                        )
                        execution_details = reentry_position.modify_positions(
                            recommendation_func=adj_func, at_market=at_market
                        )
                        option_exit_price = execution_details[option]
                        notifier(
                            f"{underlying.name} {self.strategy_tag} {option} stop loss hit. "
                            f"Exit price: {option_exit_price}",
                            self.webhook_url,
                            "INFO",
                        )
                        if move_other_to_cost:
                            other_option = (
                                call_active_option
                                if option == put_active_option
                                else put_active_option
                            )
                            other_option.stop_loss = other_option.avg_price

                # If its inactive but has reattempts left, check for reentry
                elif option.reentries > 0:
                    if option.fetch_ltp() <= option.avg_price:
                        adj_func = partial(
                            reentry_position.adjust_qty_for_option,
                            option=option,
                            reentry=True,
                        )
                        execution_details = reentry_position.modify_positions(
                            recommendation_func=adj_func, at_market=at_market
                        )
                        option_entry_price = execution_details[option]
                        notifier(
                            f"{underlying.name} {self.strategy_tag} {option} reentry condition met. "
                            f"Reentry price: {option_entry_price}",
                            self.webhook_url,
                            "INFO",
                        )
                        option.reentries -= 1
                        if adjust_stop_loss:
                            set_stop_loss(option, option_entry_price)
                else:
                    pass

        # Exit open positions if any
        notifier(
            f"{underlying.name} {self.strategy_tag} exiting.", self.webhook_url, "INFO"
        )
        if len(reentry_position.active_options) > 0:
            reentry_position.exit_positions(at_market=at_market)

        return reentry_position.position_statuses


class OvernightStraddle(BaseStrategy):
    """Since the overnight straddle is a combination of two strategies (main and hedge),
    the parameters should be a list of two dictionaries. The first dictionary will be used
    for the main strategy and the second dictionary will be used for the hedge strategy.

    Similarly, the special parameters should be a dictionary of lists. The keys of the dictionary
    should be the index names and the values should be a list of two dictionaries. The first dictionary
    will be used for the main strategy and the second dictionary will be used for the hedge strategy.
    """

    def logic(
        self,
        underlying: Index | Stock,
        exposure: int | float,
        call_strike_offset: Optional[float] = 0.02,
        put_strike_offset: Optional[float] = -0.02,
        take_avg_price: Optional[bool] = False,
        avg_till: Optional[tuple] = (15, 28),
        at_market: Optional[bool] = False,
    ):
        """Rollover overnight short straddle to the next expiry.
        Args:
            underlying (Index | Stock): Underlying object.
            exposure (int | float): Exposure in rupees.
            call_strike_offset (float): Call strike offset in percentage terms. eg 0.02 for 2% above current price.
            put_strike_offset (float): Put strike offset in percentage terms. eg -0.02 for 2% below current price.
            take_avg_price (bool): Take average price of the index over 5m timeframes.
            avg_till (tuple): Time till which to average the price.
            at_market (bool): Whether to place market orders
        """

        def is_next_day_expiry(tte: float) -> bool:
            return 1 < tte < 2

        def check_eligibility_for_overnight_straddle(effective_tte: float) -> bool:
            after_weekend = check_for_weekend(underlying.current_expiry)
            square_off_tte = (
                effective_tte - 1
            )  # Square off 1 day after because duration of the trade is 1 day

            logger.info(f"{underlying.name} current expiry tte is {effective_tte} days")

            if after_weekend:
                logger.info(f"{underlying.name} current expiry is after a weekend")
                return False

            if square_off_tte < 1:
                if is_next_day_expiry(effective_tte):
                    logger.info(
                        f"{underlying.name} current expiry is next day so the trade is eligible on next expiry"
                    )
                    return True

                logger.info(
                    f"{underlying.name} current expiry is today so the trade is not eligible"
                )
                return False

            logger.info(
                f"{underlying.name} current expiry has enough TTE to trade so the trade is eligible"
            )
            return True

        def get_expiry_to_trade_for_overnight_straddle(effective_tte: float) -> str:
            if is_next_day_expiry(effective_tte):
                return underlying.next_expiry
            return underlying.current_expiry

        # Entering main function
        quantity_in_lots = convert_exposure_to_lots(
            exposure, underlying.fetch_ltp(), underlying.lot_size, 10
        )

        effective_time_to_expiry = time_to_expiry(
            underlying.current_expiry, effective_time=True, in_days=True
        )
        eligible_for_short = check_eligibility_for_overnight_straddle(
            effective_time_to_expiry
        )

        # Taking avg price
        avg_ltp = None
        if take_avg_price:
            if current_time().time() < time(15, 00):
                notifier(
                    f"{underlying.name} Cannot take avg price before 3pm. Try running the strategy after 3pm",
                    self.webhook_url,
                    "ERROR",
                )
                raise Exception(
                    "Cannot take avg price before 3pm. Try running the strategy after 3pm"
                )
            notifier(
                f"{underlying.name} Taking average price of the index over 5m timeframes.",
                self.webhook_url,
                "INFO",
            )
            price_list = [underlying.fetch_ltp()]
            while current_time().time() < time(*avg_till):
                _ltp = underlying.fetch_ltp()
                price_list.append(_ltp)
                sleep(60)
            avg_ltp = np.mean(price_list)

        # Assigning vix
        vix = IndiaVix.fetch_ltp()

        # Initializing the straddle if eligible
        if eligible_for_short:
            # Assigning straddle with strike and expiry
            ltp = avg_ltp if avg_ltp else underlying.fetch_ltp()
            call_strike = find_strike(
                ltp, base=underlying.base, offset=call_strike_offset
            )
            put_strike = find_strike(
                ltp, base=underlying.base, offset=put_strike_offset
            )
            expiry_to_trade = get_expiry_to_trade_for_overnight_straddle(
                effective_time_to_expiry
            )
            sell_strangle = Strangle(
                call_strike, put_strike, underlying.name, expiry_to_trade
            )
            call_iv, put_iv, iv = sell_strangle.fetch_ivs()
            iv = iv * 100
            notifier(
                f"{underlying.name} Deploying overnight short straddle with {sell_strangle}. IV: {iv}, VIX: {vix}",
                self.webhook_url,
                "INFO",
            )
        else:
            sell_strangle = None
            quantity_in_lots = 0
            notifier(
                f"{underlying.name} No straddle eligible for overnight short. VIX: {vix}",
                self.webhook_url,
                "INFO",
            )

        # Loading current position
        buy_strangle, buy_quantity_in_lots = load_current_strangle(
            underlying_str=underlying.name,
            user_id=ActiveSession.obj.userId,
            file_appendix="overnight_positions",
        )

        notifier(
            f"{underlying.name} Exiting current position {buy_strangle}",
            self.webhook_url,
            "INFO",
        )

        trade_info_dict = {
            "Date": current_time().strftime("%d-%m-%Y %H:%M:%S"),
            "Underlying": underlying.name,
        }

        call_buy_avg, put_buy_avg = np.nan, np.nan
        call_sell_avg, put_sell_avg = np.nan, np.nan

        # Placing orders
        if buy_strangle is None and sell_strangle is None:
            notifier(f"{underlying.name} No trade possible.", self.webhook_url, "INFO")
        elif sell_strangle is None:  # only exiting current position
            execution_details = execute_instructions(
                {
                    buy_strangle: {
                        "action": Action.BUY,
                        "quantity_in_lots": buy_quantity_in_lots,
                        "order_tag": self.strategy_tag,
                    }
                },
                at_market=at_market,
            )
            call_buy_avg, put_buy_avg = execution_details[buy_strangle]

        elif buy_strangle is None:  # only entering new position
            execution_details = execute_instructions(
                {
                    sell_strangle: {
                        "action": Action.SELL,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": self.strategy_tag,
                    }
                },
                at_market=at_market,
            )
            call_sell_avg, put_sell_avg = execution_details[sell_strangle]

        else:  # both entering and exiting positions
            if buy_strangle == sell_strangle:
                notifier(
                    f"{underlying.name} Same straddle. No trade required.",
                    self.webhook_url,
                    "INFO",
                )
                call_ltp, put_ltp = sell_strangle.fetch_ltp()
                call_buy_avg, put_buy_avg, call_sell_avg, put_sell_avg = (
                    call_ltp,
                    put_ltp,
                    call_ltp,
                    put_ltp,
                )
            else:
                execution_details = execute_instructions(
                    {
                        buy_strangle: {
                            "action": Action.BUY,
                            "quantity_in_lots": buy_quantity_in_lots,
                            "order_tag": self.strategy_tag,
                        },
                        sell_strangle: {
                            "action": Action.SELL,
                            "quantity_in_lots": quantity_in_lots,
                            "order_tag": self.strategy_tag,
                        },
                    },
                    at_market=at_market,
                )
                call_buy_avg, put_buy_avg = execution_details[buy_strangle]
                call_sell_avg, put_sell_avg = execution_details[sell_strangle]

        trade_info_dict.update(
            {
                "Buy Straddle": buy_strangle,
                "Buy Call Price": call_buy_avg,
                "Buy Put Price": put_buy_avg,
                "Buy Total Price": call_buy_avg + put_buy_avg,
                "Sell Straddle": sell_strangle,
                "Sell Call Price": call_sell_avg,
                "Sell Put Price": put_sell_avg,
                "Sell Total Price": call_sell_avg + put_sell_avg,
            }
        )

        trade_data = {
            underlying.name: {
                "strangle": sell_strangle,
                "quantity": quantity_in_lots,
            }
        }
        save_json_data(
            trade_data,
            f"{ActiveSession.obj.userId}\\{underlying.name}_overnight_positions.json",
        )  # Currently overwriting the file with the new data. Can be changed to use load_combine_save_json_data
        # to append the new data to the existing data.


class BiweeklyStraddle(BaseStrategy):
    """Since the biweekly straddle is a combination of two strategies (main and hedge),
    the parameters should be a list of two dictionaries. The first dictionary will be used
    for the main strategy and the second dictionary will be used for the hedge strategy.

    Similarly, the special parameters should be a dictionary of lists. The keys of the dictionary
    should be the index names and the values should be a list of two dictionaries. The first dictionary
    will be used for the main strategy and the second dictionary will be used for the hedge strategy.
    """

    def logic(
        self,
        underlying: Index | Stock,
        exposure: int | float,
        strike_offset: Optional[float] = 1,
        override_expiry_day_restriction: Optional[bool] = False,
    ):
        """Sells the far expiry straddle."""

        quantity_in_lots = convert_exposure_to_lots(
            exposure, underlying.fetch_ltp(), underlying.lot_size, 10
        )

        approved = approve_execution(
            underlying,
            override_expiry_day_restriction,
        )

        if not approved:
            notifier(
                f"{underlying.name} not eligible for biweekly straddle since it is not expiry day",
                self.webhook_url,
                "INFO",
            )
            return

        # Loading current position
        buy_straddle = load_current_strangle(
            underlying_str=underlying.name,
            user_id=ActiveSession.obj.userId,
            file_appendix="biweekly_position",
        )

        # Initializing new position
        ltp = underlying.fetch_ltp()
        strike = find_strike(ltp * strike_offset, underlying.base)
        expiry = underlying.far_expiry
        sell_straddle = Straddle(strike, underlying.name, expiry)
        call_iv, put_iv, iv = sell_straddle.fetch_ivs()
        notifier(
            f"{underlying.name} Deploying biweekly straddle\n"
            f"Square up position: {buy_straddle}\n"
            f"New position: {sell_straddle}\n"
            f"IV: {iv}",
            self.webhook_url,
            "INFO",
        )

        order_instructions = {}

        if buy_straddle:
            order_instructions[buy_straddle] = {
                "action": Action.BUY,
                "quantity_in_lots": quantity_in_lots,
                "order_tag": self.strategy_tag,
            }

        order_instructions[sell_straddle] = {
            "action": Action.SELL,
            "quantity_in_lots": quantity_in_lots,
            "order_tag": self.strategy_tag,
        }

        execution_details = execute_instructions(order_instructions)
        call_sell_avg, put_sell_avg = execution_details[sell_straddle]
        call_buy_avg, put_buy_avg = execution_details.get(
            buy_straddle, (np.nan, np.nan)
        )

        position_to_save = {underlying.name: {"strangle": sell_straddle}}
        save_json_data(
            position_to_save,
            f"{ActiveSession.obj.userId}\\{underlying.name}_biweekly_position.json",
        )  # Currently overwriting the file with the new data. Can use load_combine_save_json_data in the future
        # to append the new data to the existing data. (Use case: multiple indices using the same file)

        trade_info_dict = {
            "Date": current_time().strftime("%d-%m-%Y %H:%M:%S"),
            "Underlying": underlying.name,
            "Buy Straddle": buy_straddle,
            "Buy Call Price": call_buy_avg,
            "Buy Put Price": put_buy_avg,
            "Buy Total Price": call_buy_avg + put_buy_avg,
            "Sell Straddle": sell_straddle,
            "Sell Call Price": call_sell_avg,
            "Sell Put Price": put_sell_avg,
            "Sell Total Price": call_sell_avg + put_sell_avg,
        }


class BuyHedge(BaseStrategy):

    def logic(
        self,
        underlying: Index | Stock,
        exposure: int | float,
        strike_offset: Optional[float] = 1,
        call_offset: Optional[float] = None,
        put_offset: Optional[float] = None,
        at_market: Optional[bool] = False,
        override_expiry_day_restriction: Optional[bool] = False,
    ):
        """Buys next weeks strangle or straddle as a hedge. Offsets are the multipliers for the strike price.
        Example: 1.01 means 1.01 times the current price (1% above current price). If call_offset and put_offset are
        not provided, strike_offset is used for both call and put."""

        quantity_in_lots = convert_exposure_to_lots(
            exposure, underlying.fetch_ltp(), underlying.lot_size, 10
        )

        approved = approve_execution(
            underlying,
            override_expiry_day_restriction,
        )

        if not approved:
            notifier(
                f"{underlying.name} not eligible for weekly hedge since it is not expiry day",
                self.webhook_url,
                "INFO",
            )
            return

        ltp = underlying.fetch_ltp()
        if call_offset and put_offset:
            pass
        elif strike_offset:
            call_offset = put_offset = strike_offset
        else:
            raise Exception(
                "Either strike_offset or call_offset and put_offset required"
            )

        call_strike = find_strike(ltp * call_offset, underlying.base)
        put_strike = find_strike(ltp * put_offset, underlying.base)
        instrument = Strangle(
            call_strike, put_strike, underlying.name, underlying.next_expiry
        )

        call_iv, put_iv, iv = instrument.fetch_ivs()
        notifier(
            f"{underlying.name} Buying weekly hedge with {instrument}. IV: {iv}",
            self.webhook_url,
            "INFO",
        )
        execution_details = execute_instructions(
            {
                instrument: {
                    "action": Action.BUY,
                    "quantity_in_lots": quantity_in_lots,
                    "order_tag": self.strategy_tag,
                }
            },
            at_market=at_market,
        )
        call_buy_avg, put_buy_avg = execution_details[instrument]

        trade_info_dict = {
            "Date": current_time().strftime("%d-%m-%Y %H:%M:%S"),
            "Underlying": underlying.name,
            "Buy Instrument": instrument,
            "Buy Call Price": call_buy_avg,
            "Buy Put Price": put_buy_avg,
            "Buy Total Price": call_buy_avg + put_buy_avg,
        }


def initialize_indices(strategy, indices: list[str], dtes: list[int]) -> list[Index]:
    indices = [Index(index) for index in indices]
    # Hard coding safe indices for now. Lets wait for indices to mature
    indices: list[Index] | [] = get_n_dte_indices(*indices, dtes=dtes, safe=True)
    notify_indices_being_traded(strategy, indices)
    return indices


def get_n_dte_indices(
    *indices: Index, dtes: list[int], safe: bool
) -> list[Index] | list[None]:
    safe_indices = ["NIFTY", "BANKNIFTY", "FINNIFTY"]

    time_to_expiries = {
        index: int(
            time_to_expiry(index.current_expiry, effective_time=True, in_days=True)
        )
        for index in indices
    }

    if 0 in dtes:
        dte0 = filter(lambda x: time_to_expiries.get(x) == 0, time_to_expiries)
    else:
        dte0 = []

    if any([dte >= 1 for dte in dtes]) and safe:
        dte_above_0 = filter(
            lambda x: time_to_expiries.get(x) in dtes and x.name in safe_indices,
            time_to_expiries,
        )

    elif any([dte >= 1 for dte in dtes]):
        dte_above_0 = filter(
            lambda x: time_to_expiries.get(x) in dtes, time_to_expiries
        )

    else:
        dte_above_0 = []

    eligible_indices = set(dte0).union(set(dte_above_0))

    return list(eligible_indices)


def notify_indices_being_traded(strategy, indices: list[Index]) -> None:
    if indices:
        notifier(
            f"Trading {strategy.__class__.__name__} on {', '.join([index.name for index in indices])}.",
            strategy.webhook_url,
            "INFO",
        )
    else:
        notifier(
            f"No indices to trade for {strategy.__class__.__name__}.",
            strategy.webhook_url,
            "INFO",
        )
