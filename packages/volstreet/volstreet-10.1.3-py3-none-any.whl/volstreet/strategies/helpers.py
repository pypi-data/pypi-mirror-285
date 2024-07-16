import numpy as np
from attrs import define, field, validators
from datetime import timedelta, time
from time import sleep
from itertools import product
import inspect
import traceback
from typing import Callable
from pulp import LpStatus
from volstreet import config
from volstreet.config import logger
from volstreet.blackscholes import Greeks
from volstreet.utils.core import (
    time_to_expiry,
    current_time,
    round_shares_to_lot_size,
    find_strike,
    custom_cacher,
    get_next_timestamp,
)
from volstreet.utils.communication import notifier
from volstreet.utils.data_io import load_json_data, save_json_data
from volstreet.angel_interface.interface import (
    ActiveSession,
    LiveFeeds,
    fetch_quotes,
    fetch_book,
    lookup_and_return,
)
from volstreet.trade_interface import (
    Index,
    Strangle,
    Straddle,
    Action,
    Option,
    OptionType,
    execute_instructions,
    place_option_order_and_notify,
    cancel_pending_orders,
)
from volstreet.strategies.optimization import (
    filter_greeks_frame,
    delta_neutral_optimization_lp,
    trend_following_optimization_lp,
)

if config.backtest_mode:
    from volstreet.backtests.proxy_functions import (
        execute_instructions,
        ProxyFeeds as LiveFeeds,
    )


@define(slots=False, repr=False, eq=False)
class ActiveOption(Option):
    """An extension of Option for more flexibility.
    Counterpart attribute is only implemented to conduct the hygiene check. It has no other use.
    """

    # class attributes
    _disable_singleton = True

    # Required arguments
    strike = field(validator=validators.instance_of((int, float)))
    option_type = field(
        validator=validators.instance_of(OptionType), repr=lambda x: x.value
    )
    underlying = field(validator=validators.instance_of(str))
    expiry = field(validator=validators.instance_of(str))
    underlying_instance = field(repr=False, validator=validators.instance_of(Index))

    # Optional arguments
    greek_settings = field(validator=validators.instance_of(dict), factory=dict)

    # Other attributes with default values
    recommended_qty = field(
        validator=validators.instance_of(int), default=0, init=False
    )  # Used for delta hedging for now
    _active_qty = field(validator=validators.instance_of(int), init=False, default=0)
    _premium_received = field(
        validator=validators.instance_of((int, float)), init=False, default=0
    )
    caching = field(default=config.CACHING, init=False)
    counterpart = field(init=False)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(strike={self.strike}, option_type={self.option_type.value}, "
            f"underlying={self.underlying}, expiry={self.expiry}, active_qty={self.active_qty}, "
            f"premium_received={self.premium_received}, "
            f"recommended_qty={self.recommended_qty})"
        )

    def __hash__(self):
        return hash((self.strike, self.option_type.value, self.underlying, self.expiry))

    def __eq__(self, other):
        if not isinstance(other, (Option, ActiveOption)):
            return False
        return (
            self.strike == other.strike
            and self.option_type == other.option_type
            and self.underlying == other.underlying
            and self.expiry == other.expiry
        )

    @counterpart.default
    def _counterpart_default(self):
        try:
            return Option(
                strike=self.strike,
                option_type=(
                    OptionType.PUT
                    if self.option_type == OptionType.CALL
                    else OptionType.CALL
                ),
                underlying=self.underlying,
                expiry=self.expiry,
            )
        except Exception as e:
            logger.error(
                f"Error while setting counterpart "
                f"for {(self.underlying, self.strike, self.option_type, self.expiry)} "
                f"with error {e}\nTraceback: {traceback.format_exc()}"
            )
            return None

    @classmethod
    def from_option(cls, option: Option, underlying_instance: Index, **kwargs):
        return cls(
            strike=option.strike,
            option_type=option.option_type,
            underlying=option.underlying,
            expiry=option.expiry,
            underlying_instance=underlying_instance,
            **kwargs,
        )

    @property
    def active_qty(self):
        return self._active_qty

    @active_qty.setter
    def active_qty(self, value):
        current_stack = inspect.stack()
        caller_function_name = current_stack[2].function
        if caller_function_name != "update_active_qty_and_premium":
            raise Exception(
                "active_qty can only be set from 'update_active_qty_and_premium' function. "
                "Please use that function to update the active qty."
            )
        self._active_qty = value

    @property
    def premium_received(self):
        return self._premium_received

    @premium_received.setter
    def premium_received(self, value):
        current_stack = inspect.stack()
        caller_function_name = current_stack[2].function
        if caller_function_name != "update_active_qty_and_premium":
            raise Exception(
                "premium_received can only be set from 'update_active_qty_and_premium' function. "
                "Please use that function to update the active qty."
            )
        self._premium_received = value

    @property
    def premium_outstanding(self):
        return self.active_qty * self.current_ltp

    @property
    def mtm(self):
        return self.premium_outstanding - self.premium_received

    @property
    def position_greeks(self) -> Greeks:
        return self.current_greeks * self.active_qty

    @property
    def current_ltp(self) -> float:
        return super().fetch_ltp()

    @property
    @custom_cacher
    def current_greeks(self) -> Greeks:
        """The difference between this function and the parent function is that
        this function will conduct a hygiene check"""
        r = self.underlying_instance.get_basis_for_expiry(expiry=self.expiry)
        greeks = super().fetch_greeks(r=r, **self.greek_settings)
        if (np.isnan(greeks.delta) or np.isnan(greeks.gamma)) and self.counterpart:
            counter_greeks = self.counterpart.fetch_greeks(
                r=r,
                **self.greek_settings,
            )
            greeks = greek_hygiene_check(
                target_greeks=greeks,
                counter_greeks=counter_greeks,
                option_type=self.option_type,
            )
        return greeks

    def execute_order(
        self,
        quantity_in_shares: int,
        price: float,
        order_tag: str = "",
        notifier_url: str | None = None,
    ) -> None:
        """This function should place an order and return the average price."""
        if quantity_in_shares == 0:
            return  # Safeguard against placing orders with 0 qty

        price = "LIMIT" if LiveFeeds.price_feed_connected() or price is None else price
        transaction_type = Action.BUY if quantity_in_shares > 0 else Action.SELL
        qty_in_lots = int(abs(quantity_in_shares) / self.lot_size)
        avg_price = place_option_order_and_notify(
            self,
            action=transaction_type,
            qty_in_lots=qty_in_lots,
            prices=price,
            order_tag=order_tag,
            webhook_url=notifier_url,
        )
        self.update_active_qty_and_premium(quantity_in_shares, avg_price)

    def update_active_qty_and_premium(self, adjustment_qty: int, avg_price: float):
        self.active_qty = self.active_qty + adjustment_qty
        self.premium_received += adjustment_qty * avg_price


class PositionMonitor:
    def __init__(self, underlying: Index, **kwargs):
        self.underlying = underlying
        self.instrument = None
        self.position_active = False
        self.exit_triggers = {}
        self.counter = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    def exit_triggered(self):
        return any(self.exit_triggers.values())


@define(slots=False)
class PositionManager:
    # Required attributes
    underlying: Index = field(validator=validators.instance_of(Index))
    base_exposure_qty = field()

    # Other attributes with default values
    greek_settings = field(factory=dict, validator=validators.instance_of(dict))
    order_tag = field(default="", validator=validators.instance_of(str))
    expiry = field(validator=validators.instance_of(str))
    all_calls = field(factory=list, repr=False)
    all_puts = field(factory=list, repr=False)
    exit_triggers: dict[str, bool] = field(factory=lambda: {"end_time": False})
    position_statuses = field(factory=list)
    last_position_status = field(default=None)
    notifier_url: str = field(default=None)

    @property
    def all_options(self):
        return self.all_calls + self.all_puts

    def get_prospective_options(self, options, option_type):
        """
        Filter out illiquid options from a given list of options (intended to be used on all_calls
        and all_puts) based on the option type.

        :param options: List of options to filter.
        :param option_type: Type of the options (CALL or PUT).
        :return: Filtered list of options.
        """
        try:
            otm_strikes = self.underlying.get_otm_strikes(
                [opt.strike for opt in options],
                option_type,
            )  # Very important to filter out itm strikes to avoid expensive API calls
            filtered_options = filter_out_illiquid_options(
                [opt for opt in options if opt.strike in otm_strikes],
                timedelta_minutes=3,
            )
        except Exception as e:
            logger.error(
                f"Error while filtering out illiquid options for {self.underlying.name} "
                f"with error {e} and traceback {traceback.format_exc()}"
            )
            filtered_options = options
        return filtered_options

    @property
    def prospective_calls(self):
        return self.get_prospective_options(self.all_calls, OptionType.CALL)

    @prospective_calls.setter
    def prospective_calls(self, value):
        raise Exception("prospective_calls attribute is read only")

    @property
    def prospective_puts(self):
        return self.get_prospective_options(self.all_puts, OptionType.PUT)

    @prospective_puts.setter
    def prospective_puts(self, value):
        raise Exception("prospective_puts attribute is read only")

    @property
    def prospective_options(self):
        return self.prospective_calls + self.prospective_puts

    @prospective_options.setter
    def prospective_options(self, value):
        raise Exception(f"prospective_options attribute is read only")

    @property
    def recommended_calls(self):
        if self.all_calls:
            recommended_calls = [
                call for call in self.all_calls if call.recommended_qty != 0
            ]
            return recommended_calls
        return []

    @recommended_calls.setter
    def recommended_calls(self, value):
        raise Exception("recommended_calls attribute is read only")

    @property
    def recommended_puts(self):
        if self.all_puts:
            recommended_puts = [
                put for put in self.all_puts if put.recommended_qty != 0
            ]
            return recommended_puts
        return []

    @recommended_puts.setter
    def recommended_puts(self, value):
        raise Exception("recommended_puts attribute is read only")

    @property
    def recommended_options(self):
        if self.all_options:
            return [opt for opt in self.all_options if opt.recommended_qty != 0]
        return []

    @recommended_options.setter
    def recommended_options(self, value):
        raise Exception("recommended_options attribute is read only")

    @property
    def active_call_options(self):
        if self.all_calls:
            return [opt for opt in self.all_calls if opt.active_qty != 0]
        return []

    @active_call_options.setter
    def active_call_options(self, value):
        raise Exception("active_call_options attribute is read only")

    @property
    def active_put_options(self):
        if self.all_puts:
            return [opt for opt in self.all_puts if opt.active_qty != 0]
        return []

    @active_put_options.setter
    def active_put_options(self, value):
        raise Exception("active_put_options attribute is read only")

    @property
    def active_options(self):
        if self.all_options:
            return [opt for opt in self.all_options if opt.active_qty != 0]
        return []

    @active_options.setter
    def active_options(self, value):
        raise Exception("active_options attribute is read only")

    @expiry.default
    def _expiry_default(self):
        return self.underlying.current_expiry

    @property
    def aggregate_call_active_qty(self):
        return sum(
            opt.active_qty
            for opt in self.all_calls
            if opt.option_type == OptionType.CALL
        )

    @property
    def aggregate_put_active_qty(self):
        return sum(
            opt.active_qty for opt in self.all_puts if opt.option_type == OptionType.PUT
        )

    def adjust_recommended_qty(self):
        """Adjusts the recommended qty to account for active qty in order to avoid unnecessary
        orders."""
        for option in self.all_options:
            if option.recommended_qty == 0 and option.active_qty == 0:
                continue
            option.recommended_qty = option.recommended_qty - option.active_qty

    def reset_options(self):
        for option in self.all_options:
            option.recommended_qty = 0

    @staticmethod
    def get_option_greeks(options, informative: bool = False) -> np.ndarray:
        """Returns a 2d array of greeks for each option in the collection"""
        greeks = np.array([option.current_greeks.as_array() for option in options])
        if informative:
            strikes = np.array([option.strike for option in options])
            ltp = np.array([option.current_ltp for option in options])
            return np.column_stack((strikes, ltp, greeks))
        else:
            return greeks

    @staticmethod
    def get_option_ivs(options: list[Option], filter_func: Callable = None):
        ivs = [option.current_greeks.iv for option in options]
        if filter_func:
            return np.array([*filter(filter_func, ivs)])
        else:
            return np.array(ivs)

    @staticmethod
    def get_option_deltas(options: list[Option], filter_func: Callable = None):
        deltas = [option.current_greeks.delta for option in options]
        if filter_func:
            return np.array([*filter(filter_func, deltas)])
        else:
            return np.array(deltas)

    @staticmethod
    def get_option_gammas(options: list[Option], filter_func: Callable = None):
        gammas = [option.current_greeks.gamma for option in options]
        if filter_func:
            return np.array([*filter(filter_func, gammas)])
        else:
            return np.array(gammas)

    def get_option_chain_with_greeks(self, delta_threshold: float) -> np.ndarray:
        """Returns a 2d array of greeks with options as the last column.
        Data columns: strike, ltp, delta, gamma, theta, vega, option.
        The universe of options are the prospective calls and prospective puts."""

        call_greeks = self.prepare_greek_frame_with_options(
            self.prospective_calls, delta_threshold, True
        )
        put_greeks = self.prepare_greek_frame_with_options(
            self.prospective_puts, delta_threshold, False
        )
        all_greeks = np.concatenate([call_greeks, put_greeks])

        return all_greeks

    def potential_greeks(self) -> Greeks:
        greeks = np.sum(
            [
                (opt.recommended_qty * opt.current_greeks)
                for opt in self.recommended_options
            ]
        )
        return greeks

    def aggregate_greeks(self) -> Greeks:
        return np.sum([opt.position_greeks for opt in self.active_options])

    def _generate_single_side_options(
        self,
        option_type: OptionType,
        available_strikes: list[int],
    ) -> list[ActiveOption]:
        prospective_options = [
            ActiveOption(
                strike=strike,
                option_type=option_type,
                underlying=self.underlying.name,
                expiry=self.expiry,
                underlying_instance=self.underlying,
                greek_settings=self.greek_settings,
            )
            for strike in available_strikes
        ]
        return prospective_options

    def generate_all_calls(
        self, available_strikes: dict[str, list[int]]
    ) -> list[ActiveOption]:
        return self._generate_single_side_options(
            OptionType.CALL,
            available_strikes["CE"],
        )

    def generate_all_puts(
        self, available_strikes: dict[str, list[int]]
    ) -> list[ActiveOption]:
        return self._generate_single_side_options(
            OptionType.PUT,
            available_strikes["PE"],
        )

    def set_options(
        self,
        *,
        calls: list[ActiveOption] = None,
        puts: list[ActiveOption] = None,
    ):
        """If the options are being set explicitly, then its sorts the options and sets them. Otherwise,
        it fetches the available strikes and sets all the options."""
        if calls is None or puts is None:
            available_strikes = self.underlying.get_available_strikes(
                expiry=self.expiry
            )
            if calls is None:
                calls = self.generate_all_calls(available_strikes)
            if puts is None:
                puts = self.generate_all_puts(available_strikes)

        # If the original attributes must be lists, convert them back
        self.all_calls = [*sorted(calls, key=lambda x: x.strike)]
        self.all_puts = [*sorted(puts, key=lambda x: -1 * x.strike)]  # Descending order

        # Updating the LiveFeeds backup tokens
        LiveFeeds.back_up_tokens.update(
            [opt.token for opt in self.all_options] + [self.underlying.token]
        )

    def prepare_greek_frame_with_options(
        self, options: list[Option], delta_threshold: float, is_call: bool
    ) -> np.ndarray:
        greeks = self.get_option_greeks(options, informative=True)
        array = np.array([option for option in options])
        greeks = np.column_stack((greeks, array))
        logger.info(f"Greeks: {greeks}. Dispatching to filter_greeks_frame")
        greeks = filter_greeks_frame(
            greeks,
            delta_threshold,
            is_call,
        )
        return greeks

    def update_underlying(self) -> None:
        """Updates the underlying price and the implied future interest rate."""
        self.underlying.fetch_ltp()
        self.underlying.get_basis_for_expiry(self.expiry)

    def set_weights_in_options(
        self, option_array: np.ndarray, weights: np.ndarray
    ) -> None:
        for option, weight in zip(option_array, weights):
            option.recommended_qty = round_shares_to_lot_size(
                weight * self.base_exposure_qty, option.lot_size
            )

    def _act_on_recommended_qty(
        self, at_market: bool, square_off_orders: bool
    ) -> dict[ActiveOption, float]:
        self.append_position_status(
            before_adjustment=True
        )  # Save positions before executing orders
        instructions = {
            option: {
                "action": Action.BUY if option.recommended_qty >= 0 else Action.SELL,
                "quantity_in_lots": abs(option.recommended_qty) / option.lot_size,
                "order_tag": self.order_tag,
                "square_off_order": square_off_orders,
            }
            for option in self.recommended_options
        }
        execution_details = execute_instructions(instructions, at_market=at_market)
        for option, avg_price in execution_details.items():
            option.update_active_qty_and_premium(option.recommended_qty, avg_price)
            option.recommended_qty = 0
        self.reset_trigger_flags()
        self.append_position_status(
            after_adjustment=True
        )  # Save positions after executing orders
        return execution_details

    def enter_positions(self, at_market: bool) -> dict[ActiveOption, float]:
        """To be used when there are no active positions and the recommended qty is set."""
        return self._act_on_recommended_qty(at_market, square_off_orders=False)

    def retain_existing_quantities(self):
        for option in self.active_options:
            option.recommended_qty = option.active_qty

    def modify_positions(
        self, recommendation_func: Callable, at_market: bool
    ) -> dict[ActiveOption, float]:
        """This function works as follows:
        1. Loads existing quantities
        2. Calls the recommendation function which sets new ideal quantities
        3. Adjusts the recommended quantities to account for existing quantities
        4. Executes the orders
        """
        self.retain_existing_quantities()
        recommendation_func()
        self.adjust_recommended_qty()
        return self._act_on_recommended_qty(at_market, square_off_orders=False)

    def exit_positions(self, at_market: bool) -> None:
        """Handles squaring up of the position"""
        for option in self.all_options:
            option.recommended_qty = 0
        self.adjust_recommended_qty()
        self._act_on_recommended_qty(at_market, square_off_orders=True)

    def get_position_status(self, **additional_info) -> dict:
        total_premium_outstanding = sum(
            [option.premium_outstanding for option in self.active_options]
        )
        total_premium_received = sum(
            [option.premium_received for option in self.all_options]
        )

        position_status = {
            "timestamp": current_time(),
            "underlying": self.underlying.name,
            "underlying_price": self.underlying.fetch_ltp(),
            "expiry": self.expiry,
            "base_exposure_qty": self.base_exposure_qty,
            "active_call_options": [
                {
                    "strike": option.strike,
                    "option_type": option.option_type.value,
                    "active_qty": option.active_qty,
                    "premium_received": option.premium_received,
                    "current_ltp": option.current_ltp,
                    "current_greeks": option.current_greeks.as_dict(),
                }
                for option in self.active_call_options
            ],
            "active_put_options": [
                {
                    "strike": option.strike,
                    "option_type": option.option_type.value,
                    "active_qty": option.active_qty,
                    "premium_received": option.premium_received,
                    "current_ltp": option.current_ltp,
                    "current_greeks": option.current_greeks.as_dict(),
                }
                for option in self.active_put_options
            ],
            "aggregate_greeks": (
                self.aggregate_greeks().as_dict() if self.active_options else {}
            ),
            "total_premium_received": total_premium_received,
            "total_premium_outstanding": total_premium_outstanding,
            "mtm": total_premium_outstanding - total_premium_received,
            "exit_triggers": self.exit_triggers.copy(),
            **additional_info,
        }
        self.last_position_status = position_status
        return position_status

    def append_position_status(self, **additional_info) -> None:
        """Designed to periodically save the position status to a file."""
        position_status = self.get_position_status(**additional_info)
        self.position_statuses.append(position_status)

    def reset_trigger_flags(self):
        self.exit_triggers = {"end_time": False, "qty_breach_exit": False}


@define(slots=False)
class TrendPosition(PositionManager):

    def set_recommended_qty_simple(
        self, hedge_offset: float, trend_direction: Action
    ) -> None:
        spot = self.underlying.fetch_ltp()
        atm_strike = find_strike(spot, self.underlying.base)

        hedge_strike_multiplier = (
            1 + hedge_offset if trend_direction == Action.BUY else 1 - hedge_offset
        )
        hedge_strike = find_strike(spot * hedge_strike_multiplier, self.underlying.base)
        hedge_option_type: OptionType = (
            OptionType.CALL if trend_direction == Action.BUY else OptionType.PUT
        )

        for option in self.all_calls:
            if option.strike == atm_strike:
                option.recommended_qty = (
                    self.base_exposure_qty * trend_direction.num_value
                )
            elif hedge_option_type == OptionType.CALL and option.strike == hedge_strike:
                option.recommended_qty = (
                    self.base_exposure_qty * -1
                )  # Hedge is always sold
        for option in self.all_puts:
            if option.strike == atm_strike:
                option.recommended_qty = (
                    -self.base_exposure_qty * trend_direction.num_value
                )
            elif hedge_option_type == OptionType.PUT and option.strike == hedge_strike:
                option.recommended_qty = (
                    self.base_exposure_qty * -1
                )  # Hedge is always sold

    def set_recommended_qty_optimized(
        self,
        target_delta: float,
        trend_direction: Action,
    ) -> None:
        all_greeks = self.get_option_chain_with_greeks(0.75)

        prob, weights = trend_following_optimization_lp(
            all_greeks[:, 2:6],
            target_delta=target_delta,
            trend_direction=trend_direction,
        )
        if prob.status != 1:
            logger.warning(
                f"Optimization in trend following failed with status {LpStatus[prob.status]}. "
                f"Check earlier messages from logs for more details."
            )
            raise Exception(f"Optimization failed with status {LpStatus[prob.status]}")

        self.set_weights_in_options(all_greeks[:, -1], weights)

    def set_recommended_qty(
        self,
        optimized: bool,
        target_delta: float,
        trend_direction: Action,
        hedge_offset: float,
    ) -> None:
        self.reset_options()
        if optimized:
            try:
                self.set_recommended_qty_optimized(target_delta, trend_direction)
            except Exception as e:
                notifier(
                    f"{self.underlying.name} Error while setting optimized recommended qty in trend: {e}\n"
                    f"Using simple implementation\n"
                    f"Traceback: {e.__traceback__}",
                    self.notifier_url,
                    "ERROR",
                )
                self.set_recommended_qty_simple(hedge_offset, trend_direction)
        else:
            self.set_recommended_qty_simple(hedge_offset, trend_direction)


@define(slots=False)
class DeltaPosition(PositionManager):
    current_hedge_strike = field(default=None)
    spike_start_time = field(default=None)

    def set_file_path(self):
        date = current_time().strftime("%Y-%m-%d")
        file_path = f"{ActiveSession.obj.userId}\\{self.underlying.name.lower()}_delta_data\\{date}.json"
        return file_path

    def get_hedge_options(self) -> tuple[ActiveOption, ActiveOption]:
        spot = self.underlying.fetch_ltp()
        atm_strike = find_strike(spot, self.underlying.base)
        # If its not too different (more than 2 strikes away), then use the last hedge strike
        if (
            self.current_hedge_strike
            and abs(atm_strike - self.current_hedge_strike) <= 2 * self.underlying.base
        ):
            pass
        else:
            self.current_hedge_strike = atm_strike
        hedge_call_option = next(
            (
                option
                for option in self.all_calls
                if option.strike == self.current_hedge_strike
            ),
            None,
        )
        hedge_put_option = next(
            (
                option
                for option in self.all_puts
                if option.strike == self.current_hedge_strike
            ),
            None,
        )
        return hedge_call_option, hedge_put_option

    def _handle_option_type(self, options, target_delta):
        higher_options = [
            *filter(lambda x: abs(x.current_greeks.delta) >= target_delta, options)
        ]
        lower_options = [
            *filter(lambda x: abs(x.current_greeks.delta) < target_delta, options)
        ]

        if not higher_options and not lower_options:
            notifier(
                f"{self.underlying.name} no options found for target delta {target_delta} "
                f"increasing target delta by 0.1.",
                self.notifier_url,
                "ERROR",
            )
            return False

        if higher_options and not lower_options:  # Only higher options are available
            option_to_sell = min(
                higher_options, key=lambda x: abs(x.current_greeks.delta)
            )
            option_to_sell.recommended_qty = -round_shares_to_lot_size(
                self.base_exposure_qty, option_to_sell.lot_size
            )
            return True

        upper_option = min(higher_options, key=lambda x: abs(x.current_greeks.delta))
        lower_option = max(lower_options, key=lambda x: abs(x.current_greeks.delta))

        ratio_upper = (target_delta - abs(lower_option.current_greeks.delta)) / (
            abs(upper_option.current_greeks.delta)
            - abs(lower_option.current_greeks.delta)
        )
        ratio_lower = (abs(upper_option.current_greeks.delta) - target_delta) / (
            abs(upper_option.current_greeks.delta)
            - abs(lower_option.current_greeks.delta)
        )

        if ratio_upper > 1 or ratio_lower > 1:
            notifier(
                f"Weird quantity ratios for {self.underlying.name}. "
                f"Ratios: {ratio_upper} and {ratio_lower}. "
                f"Upper option: {upper_option}. "
                f"Lower option: {lower_option}. Retrying...",
                self.notifier_url,
                "ERROR",
            )
            return "retry"

        upper_option_qty = round_shares_to_lot_size(
            self.base_exposure_qty * ratio_upper, upper_option.lot_size
        )
        lower_option_qty = round_shares_to_lot_size(
            self.base_exposure_qty * ratio_lower, lower_option.lot_size
        )

        upper_option.recommended_qty = -upper_option_qty
        lower_option.recommended_qty = -lower_option_qty
        return True

    def set_recommended_qty_backup(
        self, target_delta: float = None, attempt_no: int = 0
    ):
        self.reset_options()

        if target_delta > 0.7 or attempt_no > 5:
            raise ValueError(
                f"Unable to calibrate positions for {self.underlying.name} "
                f"after {attempt_no} attempts."
            )

        if attempt_no > 0:
            self.update_underlying()

        success_calls = self._handle_option_type(
            self.prospective_calls,
            target_delta,
        )
        success_puts = self._handle_option_type(
            self.prospective_puts,
            target_delta,
        )

        if success_calls == "retry" or success_puts == "retry":
            self.set_recommended_qty_backup(
                target_delta=target_delta, attempt_no=attempt_no + 1
            )

        if not success_calls or not success_puts:
            self.set_recommended_qty_backup(
                target_delta=target_delta + 0.1, attempt_no=attempt_no + 1
            )

    def set_optimized_recommended_qty(
        self, delta_threshold: float, optimize_gamma: bool
    ):
        self.reset_options()
        ivs = self.get_option_ivs(self.prospective_calls + self.prospective_puts)
        median_iv = np.nanmedian(ivs)
        logger.info(f"Using median IV {median_iv} for optimization")
        all_greeks = self.get_option_chain_with_greeks(delta_threshold)

        # Solving the optimization problem

        prob, weights = delta_neutral_optimization_lp(
            all_greeks[:, 2:6],
            optimize_gamma=optimize_gamma,
            spot=self.underlying.fetch_ltp(),
            time_to_expiry=time_to_expiry(self.expiry),
            r=self.underlying.get_basis_for_expiry(self.expiry),
            iv=median_iv,
        )  # Using delta, gamma, theta, vega

        if prob.status != 1:
            logger.warning(
                f"Optimization in delta hedging failed with status {LpStatus[prob.status]}. "
                f"Check earlier messages from logs for more details."
            )
            raise Exception(f"Optimization failed with status {LpStatus[prob.status]}")

        self.set_weights_in_options(all_greeks[:, -1], weights)

    def set_recommended_qty(
        self,
        target_delta: float,
        delta_threshold: float,
        optimized: bool,
        optimize_gamma: bool,
    ) -> None:
        if optimized:
            try:
                self.set_optimized_recommended_qty(
                    optimize_gamma=optimize_gamma, delta_threshold=delta_threshold
                )
            except Exception as e:
                notifier(
                    f"{self.underlying.name} Error while setting optimized recommended qty in delta: {e}\n"
                    f"Using backup implementation\n"
                    f"Traceback: {e.__traceback__}",
                    self.notifier_url,
                    "ERROR",
                )
                self.set_recommended_qty_backup(target_delta)
        else:
            self.set_recommended_qty_backup(target_delta)

    def get_flagship_sell_option(self, option_type: OptionType):
        return min(
            (
                self.active_call_options
                if option_type == OptionType.CALL
                else self.active_put_options
            ),
            key=lambda x: x.active_qty,
        )

    def get_flagship_hedge_option(self, option_type: OptionType):
        return max(
            (
                self.active_call_options
                if option_type == OptionType.CALL
                else self.active_put_options
            ),
            key=lambda x: x.active_qty,
        )

    def check_for_iv_spike(self, aggregate_delta: float):
        option_to_check = OptionType.CALL if aggregate_delta < 0 else OptionType.PUT
        flagship_option = self.get_flagship_sell_option(option_to_check)
        flagship_iv = flagship_option.current_greeks.iv
        type_field = "put" if aggregate_delta > 0 else "call"
        last_valid_position = self.last_position_status[f"active_{type_field}_options"]
        last_iv = min(last_valid_position, key=lambda x: x["active_qty"])[
            "current_greeks"
        ]["iv"]
        return flagship_iv / last_iv >= 1.1

    def set_hedge_qty(self, aggregate_delta: float):
        hedge_call, hedge_put = self.get_hedge_options()

        # Using call just for convenience
        qty_to_hedge = round_shares_to_lot_size(
            abs(aggregate_delta), hedge_call.lot_size
        )

        # Using call just for convenience
        if qty_to_hedge <= hedge_call.lot_size:
            notifier(
                f"For some reason the qty to hedge is less than lot size for {self.underlying.name}. "
                f"Aggregate delta: {aggregate_delta}.",
                self.notifier_url,
                "ERROR",
            )
            return

        # we increment qtys instead of setting them
        if aggregate_delta > 0:  # Sell the synthetic future
            hedge_call.recommended_qty -= qty_to_hedge
            hedge_put.recommended_qty += qty_to_hedge
        else:  # Buy the synthetic future
            hedge_call.recommended_qty += qty_to_hedge
            hedge_put.recommended_qty -= qty_to_hedge


class ReentryPosition(PositionManager):

    def set_main_entry_recommendation(self):
        self.all_calls[0].recommended_qty = -self.base_exposure_qty
        self.all_puts[0].recommended_qty = -self.base_exposure_qty

    def adjust_qty_for_option(
        self,
        option: ActiveOption,
        stop_loss: bool = False,
        reentry: bool = False,
    ):
        if stop_loss:
            option.recommended_qty += self.base_exposure_qty
        elif reentry:
            option.recommended_qty -= self.base_exposure_qty


def generate_optimized_result(
    greeks: np.ndarray, weights: np.ndarray, idx: np.ndarray
) -> np.ndarray:
    optimized_result = np.round(
        (greeks[idx] * weights.reshape(-1, 1)).sum(
            axis=0,
        ),
        4,
    )
    return optimized_result


def generate_optimized_weight_array(
    number_of_rows: int, indices: np.ndarray, weights: np.ndarray
) -> np.ndarray:
    # Step 1: Create a new zero-filled column
    new_column = np.zeros((number_of_rows, 1))

    # Step 2: Insert new values at specified indices
    new_column[indices] = weights.reshape(-1, 1)

    return new_column


def greek_hygiene_check(
    target_greeks: Greeks, counter_greeks: Greeks, option_type: OptionType
) -> Greeks:
    """Currently only handles delta and gamma"""
    target_delta = getattr(target_greeks, "delta")
    counter_delta = getattr(counter_greeks, "delta")

    target_gamma = getattr(target_greeks, "gamma")
    counter_gamma = getattr(counter_greeks, "gamma")

    if np.isnan(target_delta):
        if option_type == OptionType.CALL:
            setattr(target_greeks, "delta", counter_delta + 1)
        elif option_type == OptionType.PUT:
            setattr(target_greeks, "delta", counter_delta - 1)

    if np.isnan(target_gamma):
        setattr(target_greeks, "gamma", counter_gamma)

    return target_greeks


def get_above_below_strangles_with_prices(
    underlying: Index,
    spot_price: float,
    expiry: str,
    for_type: bool = None,
) -> tuple[tuple[Strangle, tuple[float, float]], tuple[Strangle, tuple[float, float]]]:
    above_strangle, above_prices = get_strangle_with_prices(
        underlying, spot_price, 1, expiry, for_type
    )
    below_strangle, below_prices = get_strangle_with_prices(
        underlying, spot_price, -1, expiry, for_type
    )
    return (above_strangle, above_prices), (below_strangle, below_prices)


def get_strangle_with_prices(
    underlying: Index,
    spot_price: float,
    n_steps: int,
    expiry: str,
    for_type: bool = None,
) -> tuple[Strangle, tuple[float, float]]:
    offset = underlying.base * n_steps
    # Dividing offset by 2 because sometimes the above strike is very close to the spot
    strike = find_strike(spot_price + (offset / 2), underlying.base)
    strangle: Strangle = Strangle(strike, strike, underlying.name, expiry)
    prices = strangle.fetch_ltp(for_type=for_type)
    return strangle, prices


def disparity_calculator(call_ltp, put_ltp):
    disparity = abs(call_ltp - put_ltp) / min(call_ltp, put_ltp)
    return disparity


def efficient_ltp_for_options(
    options: list[Option] | set[Option],
) -> dict[Option, float]:
    """
    Fetches the latest trading prices (LTPs) for a set of options.

    :param options: A list of Option objects.
    :return: A dictionary mapping each unique option to its latest trading price (LTP).
    """
    # Fetch the LTP for each unique option
    tokens = [option.token for option in options]

    all_quotes = fetch_quotes(tokens)

    ltp_cache = {
        option: quote["ltp"]
        for quote in all_quotes
        for option in options
        if option.token == quote["token"]
    }

    return ltp_cache


def efficient_ltp_for_strangles(strangles: list[Strangle]) -> dict[Option, float]:
    """
    Fetches the latest trading prices (LTPs) for a set of options extracted from a list of strangles.

    :param strangles: A list of Strangle objects.
    :return: A dictionary mapping each unique option to its latest trading price (LTP).
    """
    # Create a set of all distinct options from the strangles
    options = set(
        option
        for strangle in strangles
        for option in (strangle.call_option, strangle.put_option)
    )

    # Fetch the LTP for each unique option
    ltp_cache = efficient_ltp_for_options(options)
    return ltp_cache


def get_range_of_strangles(
    underlying: Index,
    call_strike_offset: float | int = 0,
    put_strike_offset: float | int = 0,
    expiry: str = None,
    strike_range: int = 10,
):
    if expiry is None:
        expiry = underlying.current_expiry

    if call_strike_offset == put_strike_offset:  # Straddle
        strikes = underlying.get_active_strikes(strike_range, call_strike_offset)
        return [Straddle(strike, underlying.name, expiry) for strike in strikes]
    else:
        underlying_ltp = underlying.fetch_ltp()
        call_strike_range = underlying.get_active_strikes(
            strike_range, call_strike_offset, ltp=underlying_ltp
        )
        put_strike_range = underlying.get_active_strikes(
            strike_range, put_strike_offset, ltp=underlying_ltp
        )
        pairs = product(call_strike_range, put_strike_range)
        strangles = [
            Strangle(pair[0], pair[1], underlying.name, expiry) for pair in pairs
        ]
        return strangles


def filter_strangles_by_delta(
    deltas: dict[Strangle, tuple[float, float]],
    delta_range: tuple[float, float],
) -> dict[Strangle, tuple[float, float]]:
    """Filtering for strangles with delta between delta_range"""
    min_range = delta_range[0]
    max_range = delta_range[1]
    filtered = {
        strangle: deltas[strangle]
        for strangle in deltas
        if all([min_range <= abs(delta) <= max_range for delta in deltas[strangle]])
    }  # Condition is that both call and put delta should be within the range

    return filtered


def most_equal_strangle(
    underlying: Index,
    call_strike_offset: float | int = 0,
    put_strike_offset: float | int = 0,
    disparity_threshold: float = 1000,
    exit_time: tuple[int, int] = (15, 25),
    range_of_strikes: int = 4,
    expiry: str = None,
    notification_url: str = None,
) -> Strangle | Straddle | None:
    if expiry is None:
        expiry = underlying.current_expiry

    strangles = get_range_of_strangles(
        underlying,
        call_strike_offset=call_strike_offset,
        put_strike_offset=put_strike_offset,
        expiry=expiry,
        strike_range=range_of_strikes,
    )
    # logger.info(f"{underlying.name} prospective strangles: {strangles}")

    # Define the price disparity function
    def price_disparity(strangle):
        call_ltp = ltp_cache.get(strangle.call_option, np.nan)
        put_ltp = ltp_cache.get(strangle.put_option, np.nan)
        return abs(call_ltp - put_ltp) / min(call_ltp, put_ltp)

    last_notified_time = current_time() - timedelta(minutes=6)

    while current_time().time() < time(*exit_time):
        ltp_cache = efficient_ltp_for_strangles(strangles)
        if call_strike_offset == put_strike_offset:  # Straddle
            disparities = [price_disparity(strangle) for strangle in strangles]
            min_disparity = min(disparities)
            # Now if there are two straddles with v v similar disparities, return the one with the close strike to spot
            # Similar is defined as within 0.0075 from the minimum disparity
            most_equal, min_disparity = min(
                [
                    (strangle, disparity)
                    for strangle, disparity in zip(strangles, disparities)
                    if disparity <= min_disparity + 0.0075
                ],
                key=lambda x: abs(x[0].strike - underlying.fetch_ltp()),
            )
        else:
            most_equal, min_disparity = min(
                ((s, price_disparity(s)) for s in strangles), key=lambda x: x[1]
            )

        # If the lowest disparity is below the threshold, return the most equal strangle
        if min_disparity <= disparity_threshold:
            return most_equal

        if last_notified_time < current_time() - timedelta(minutes=5):
            notifier(
                f"Most equal strangle: {most_equal} with disparity {min_disparity} "
                f"and prices {ltp_cache[most_equal.call_option]} and {ltp_cache[most_equal.put_option]}",
                notification_url,
                "INFO",
            )
            logger.info(f"Most equal ltp cache: {ltp_cache}")
            last_notified_time = current_time()

        sleep(0.1)

    else:
        return None


def identify_strangle(
    underlying: Index,
    equality_constraint: bool,
    expiry: str = None,
    call_strike_offset: float | int = 0,
    put_strike_offset: float | int = 0,
    *args,
    **kwargs,
) -> Strangle | Straddle:
    if equality_constraint:
        return most_equal_strangle(
            underlying,
            call_strike_offset=call_strike_offset,
            put_strike_offset=put_strike_offset,
            expiry=expiry,
            *args,
            **kwargs,
        )
    else:
        spot = underlying.fetch_ltp()
        call_strike = find_strike(spot * (1 + call_strike_offset), underlying.base)
        put_strike = find_strike(spot * (1 + put_strike_offset), underlying.base)
        expiry = expiry or underlying.current_expiry
        return Strangle(call_strike, put_strike, underlying.name, expiry)


def approve_execution(
    underlying: Index,
    override_expiry_day_restriction: bool,
) -> bool:
    """Used in long-standing strategies to check if the strategy is eligible for execution"""

    current_expiry_tte = time_to_expiry(underlying.current_expiry, in_days=True)
    if current_expiry_tte < 1:
        return True
    # If current expiry is more than 1 day away, then the strategy is not eligible
    # unless override_expiry_day_restriction is True
    elif current_expiry_tte >= 1 and not override_expiry_day_restriction:
        return False


def most_even_delta_strangle(
    underlying: Index,
    delta_range: tuple[float, float] = (0.0, 100),
    expiry: str = None,
    strike_range: int = 6,
) -> tuple[Strangle | Straddle, float] | tuple[None, np.nan]:
    strangles = get_range_of_strangles(
        underlying,
        call_strike_offset=0.001,  # Setting a small offset to force return Strangle instead of Straddle
        put_strike_offset=0.001,
        expiry=expiry,
        strike_range=strike_range,
    )
    strangle_deltas: dict = calculate_strangle_deltas(underlying, strangles)
    strangle_deltas: dict = filter_strangles_by_delta(strangle_deltas, delta_range)
    unevenness: dict = calculate_unevenness_of_deltas(strangle_deltas)
    logger.info(
        f"{current_time()} {underlying.name} strangle deltas: {strangle_deltas}"
    )
    logger.info(
        f"{current_time()} {underlying.name} unevenness of deltas: {unevenness} "
    )
    # Checking if the unevenness dictionary is empty
    if not unevenness:
        return None, np.nan
    target_strangle: Strangle | Straddle = min(unevenness, key=unevenness.get)
    minimum_unevenness: float = unevenness[target_strangle]
    return target_strangle, minimum_unevenness


def calculate_strangle_deltas(
    index: Index, strangles: list[Strangle | Straddle]
) -> dict[Strangle, tuple[float, float]]:
    underlying_ltp = index.fetch_ltp()
    option_prices: dict[Option, float] = efficient_ltp_for_strangles(strangles)
    # Now determining the prevailing interest rate
    if [
        strangle for strangle in strangles if isinstance(strangle, Straddle)
    ]:  # Randomly choosing the first straddle
        synthetic_future_price = (
            strangles[0].call_strike
            + option_prices[strangles[0].call_option]
            - option_prices[strangles[0].put_option]
        )
    else:
        synthetic_future_price = None

    interest_rate = index.get_basis_for_expiry(
        strangles[0].expiry,
        underlying_price=underlying_ltp,
        future_price=synthetic_future_price,
    )

    option_greeks = {
        option: option.fetch_greeks(
            spot=underlying_ltp, price=option_prices[option], r=interest_rate
        )
        for option in option_prices
    }

    strangle_deltas = {
        strangle: (
            option_greeks[strangle.call_option].delta,
            option_greeks[strangle.put_option].delta,
        )
        for strangle in strangles
    }

    return strangle_deltas


def calculate_unevenness_of_deltas(
    deltas: dict[Strangle, tuple[float, float]],
) -> dict[Strangle, float]:
    # Filter for any nan values
    deltas = {
        strangle: deltas[strangle]
        for strangle in deltas
        if not any(np.isnan(deltas[strangle]))
    }

    return {
        strangle: (max(np.abs(deltas[strangle])) / min(np.abs(deltas[strangle])))
        for strangle in deltas
    }


def load_current_strangle(
    underlying_str, user_id: str, file_appendix: str
) -> tuple[Straddle | None, int]:
    """Load current position for a given underlying, user and strategy (file_appendix)."""

    # Loading current position
    trade_data = load_json_data(
        f"{user_id}\\{underlying_str}_{file_appendix}.json",
        default_structure=dict,
    )
    trade_data = trade_data.get(underlying_str, {})
    buy_strangle = trade_data.get("strangle", None)
    buy_quantity = trade_data.get("quantity", 0)
    if buy_strangle:
        buy_strangle = eval(buy_strangle)
    return buy_strangle, buy_quantity


def generate_butterfly_conversion_items(
    strangle: Strangle,
    underlying: Index,
    call_avg_price: float,
    put_avg_price: float,
    call_stop_loss: float,
    put_stop_loss: float,
    stop_loss: float,
) -> tuple[Strangle, float]:
    """This function returns the hedge strangle and the profit that should be attained
    after buying the hedges for the purchase to be justified"""

    hedge_call_strike = strangle.call_strike + underlying.base
    hedge_put_strike = strangle.put_strike - underlying.base
    hedge = Strangle(
        hedge_call_strike, hedge_put_strike, underlying.name, strangle.expiry
    )
    call_stop_loss = call_stop_loss if call_stop_loss is not None else stop_loss
    put_stop_loss = put_stop_loss if put_stop_loss is not None else stop_loss
    profit_if_call_sl = put_avg_price - (call_avg_price * call_stop_loss)
    profit_if_put_sl = call_avg_price - (put_avg_price * put_stop_loss)
    conversion_threshold_break_even = max(profit_if_call_sl, profit_if_put_sl)
    return hedge, conversion_threshold_break_even


def conversion_to_butterfly_triggered(
    hedge_strangle: Strangle,
    total_premium_collected: float,
    profit_threshold: float,
    strike_difference: float,
) -> bool:
    hedge_total_ltp = hedge_strangle.fetch_total_ltp()
    hedge_profit = total_premium_collected - hedge_total_ltp - strike_difference
    if (
        hedge_profit >= profit_threshold
        and hedge_total_ltp <= 0.15 * total_premium_collected
    ):
        return True
    else:
        return False


def sleep_until_next_action(
    interval_minutes: int,
    exit_time: tuple,
    interruption_condition: Callable = lambda: False,
    tasks_to_perform: list[Callable] = None,
    interruption_check_interval: int | float = None,
) -> None:
    # Tasks are supplied as a tuple of callable and the duration in seconds
    # to wait between calls to the callable
    if tasks_to_perform is None:
        tasks_to_perform = []  # Empty list if not provided

    time_now = current_time()
    next_action_time = get_next_timestamp(
        interval_minutes, from_time=time_now, exit_time_tuple=exit_time
    )

    if interruption_check_interval is None:
        interruption_check_interval = min(1, interval_minutes)

    while time_now < next_action_time:

        next_check_time = get_next_timestamp(
            interruption_check_interval, time_now, exit_time
        )
        sleep_until_time = min(next_action_time, next_check_time)
        sleep_duration = (sleep_until_time - time_now).total_seconds()

        if sleep_duration > 0:
            sleep(sleep_duration)

        if interruption_condition():
            return
        for task in tasks_to_perform:
            task()
        time_now = current_time()

    sleep(0.05)  # Just in case to prevent a very tight loop


def filter_out_illiquid_options(
    options: list[ActiveOption], timedelta_minutes: float | int = 3
) -> list[ActiveOption]:
    if config.backtest_mode:
        return options
    try:
        if LiveFeeds.price_feed_connected():
            data_bank = LiveFeeds.price_feed.data_bank
        elif LiveFeeds.back_up_feed:
            data_bank = LiveFeeds.back_up_feed
        else:
            return back_up_illiquid_filter(options, timedelta_minutes)
        if all([option.token in data_bank for option in options]):
            return [
                option
                for option in options
                if current_time()
                - data_bank[option.token].get("last_traded_datetime", current_time())
                < timedelta(minutes=timedelta_minutes)
            ]
        else:
            return back_up_illiquid_filter(options, timedelta_minutes)
    except Exception as e:
        logger.error(f"Error in filter_out_illiquid_options: {e}", exc_info=True)
        return back_up_illiquid_filter(options, timedelta_minutes)


def back_up_illiquid_filter(
    options: list[ActiveOption], timedelta_minutes: float | int = 3
):
    quotes = fetch_quotes(
        [option.token for option in options], structure="dict", from_source=True
    )
    return [
        option
        for option in options
        if current_time() - quotes[option.token]["last_traded_datetime"]
        < timedelta(minutes=timedelta_minutes)
    ]


def record_position_status(position_manager: PositionManager, file_name: str):
    try:
        position_manager.append_position_status()
        if config.backtest_mode:
            return
        save_json_data(position_manager.position_statuses, file_name)
    except Exception as e:
        notifier(
            f"{position_manager.underlying.name} Error while recording position status: {e}\n"
            f"Traceback: {e.__traceback__}",
            position_manager.notifier_url,
            "ERROR",
        )
        position_manager.position_statuses = []
        position_manager.append_position_status = lambda: None


def process_stop_loss_order_statuses(
    order_book,
    order_ids,
    context="",
    notify_url=None,
):
    pending_text = "trigger pending"
    context = f"{context.capitalize()} " if context else ""

    statuses = lookup_and_return(order_book, "orderid", order_ids, "status")

    if not isinstance(statuses, np.ndarray) or statuses.size == 0:
        logger.error(f"Statuses is {statuses} for orderid(s) {order_ids}")

    if all(statuses == pending_text):
        return False, False

    elif all(statuses == "rejected") or all(statuses == "cancelled"):
        rejection_reasons = lookup_and_return(order_book, "orderid", order_ids, "text")
        if all(rejection_reasons == "17070 : The Price is out of the LPP range"):
            return True, False
        else:
            notifier(
                f"{context}Order(s) rejected or cancelled. Reasons: {rejection_reasons[0]}",
                notify_url,
                "ERROR",
            )
            raise Exception(f"Order(s) rejected or cancelled.")

    elif all(statuses == "pending"):
        sleep(5)
        order_book = fetch_book("orderbook")
        statuses = lookup_and_return(order_book, "orderid", order_ids, "status")

        if all(statuses == "pending"):
            try:
                cancel_pending_orders(order_ids, "NORMAL")
            except Exception as e:
                logger.error(
                    f"{context}Could not cancel orders with variety NORMAL: {e}"
                )
                try:
                    cancel_pending_orders(order_ids, "STOPLOSS")
                except Exception as e:
                    notifier(
                        f"{context}Could not cancel orders: {e}", notify_url, "ERROR"
                    )
                    raise Exception(f"Could not cancel orders: {e}")
            notifier(
                f"{context}Orders pending and cancelled. Please check.",
                notify_url,
                "ERROR",
            )
            return True, False

        elif all(statuses == "complete"):
            return True, True

        else:
            logger.error(
                f"Orders in unknown state. Statuses: {statuses}, Order ids: {order_ids}"
            )
            raise Exception(f"Orders in unknown state.")

    elif all(statuses == "complete"):
        return True, True

    else:
        notifier(
            f"{context}Orders in unknown state. Statuses: {statuses}",
            notify_url,
            "ERROR",
        )
        raise Exception(f"Orders in unknown state.")
