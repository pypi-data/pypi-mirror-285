import pandas as pd
import numpy as np
from typing import Iterable
from fuzzywuzzy import process
from volstreet.decorators import timeit
from volstreet.exceptions import ScripsLocationError
from volstreet.config import logger, symbol_df, scrips
from volstreet import config
from volstreet.utils import (
    get_expiry_dates,
    get_symbol_token,
    get_lot_size,
    get_base,
    find_strike,
    get_range_of_strikes,
    time_to_expiry,
    get_available_strikes,
    custom_cacher,
)
from volstreet.angel_interface.interface import fetch_ltp
from volstreet.trade_interface.instruments import Straddle, Strangle, Option, OptionType

if config.backtest_mode:
    from volstreet.backtests.proxy_functions import (
        get_expiry_dates,
        get_available_strikes,
        get_symbol_token,
        get_base,
        get_lot_size,
    )


class Index:
    """Initialize an index with the name of the index in uppercase"""

    def __init__(self, name):
        self.name = name.upper()
        self.current_expiry = None
        self.next_expiry = None
        self.far_expiry = None
        self.exchange = "BSE" if self.name in ["SENSEX", "BANKEX"] else "NSE"
        self.fno_exchange = "BFO" if self.name in ["SENSEX", "BANKEX"] else "NFO"
        self.symbol, self.token = get_symbol_token(self.name)
        self.future_symbol_tokens = {}
        self.fetch_exps()
        self.lot_size = get_lot_size(self.name, self.current_expiry)
        self.available_strikes = None
        self.available_straddle_strikes = None
        self.base = get_base(self.name, self.current_expiry)
        self.exchange_type = 1

        # Caching attributes
        self.caching = config.CACHING

        logger.info(
            f"Initialized {self.name} with lot size {self.lot_size} and base {self.base}"
        )

    def __hash__(self):
        # Hash will be base on the name
        return hash(self.name)

    def __eq__(self, other):
        # Equality will be based on the name
        if isinstance(other, Index):
            return self.name == other.name
        return False

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(Name: {self.name}, Current Expiry: {self.current_expiry}, "
            f"Lot Size: {self.lot_size}, Symbol: {self.symbol}, Token: {self.token})"
        )

    def fetch_exps(self):
        exps = get_expiry_dates(self.name)
        exps = pd.DatetimeIndex(exps).strftime("%d%b%y").str.upper().tolist()

        self.current_expiry = exps[0]
        self.next_expiry = exps[1]
        self.far_expiry = exps[2]

    def set_future_symbol_tokens(self):
        if not self.future_symbol_tokens:
            for i in range(0, 3):
                try:
                    self.future_symbol_tokens[i] = get_symbol_token(self.name, future=i)
                except ScripsLocationError:
                    self.future_symbol_tokens[i] = (None, None)
                    continue

    def _fetch_future_ltp(self, future):
        try:
            ltp = fetch_ltp(
                self.fno_exchange,
                self.future_symbol_tokens[future][0],
                self.future_symbol_tokens[future][1],
            )
        except Exception as e:
            error_message_to_catch = (
                "Error in fetching LTP: 'NoneType' object is not subscriptable"
            )
            if str(e) == error_message_to_catch:
                ltp = np.nan
            else:
                raise e
        return ltp

    def fetch_ltp(self, future=None):
        """Fetch LTP of the index."""
        if isinstance(future, int):
            ltp = self._fetch_future_ltp(future)
            return ltp
        else:  # Spot price
            ltp = fetch_ltp(self.exchange, self.symbol, self.token)
            return ltp

    def get_strangle(
        self,
        expiry: str = None,
        underlying_price: float = None,
        offset: float = 0,
        steps: int = 0,
        invert: bool = False,
    ) -> Straddle | Strangle:
        expiry = self.current_expiry if expiry is None else expiry
        underlying_price = (
            self.fetch_ltp() if underlying_price is None else underlying_price
        )
        offset = abs(offset)
        steps = abs(steps)
        call_strike = find_strike(underlying_price, self.base, offset, steps)
        put_strike = find_strike(underlying_price, self.base, -offset, -steps)
        if call_strike == put_strike:
            return Straddle(call_strike, self.name, expiry)

        if invert:
            call_strike, put_strike = put_strike, call_strike

        return Strangle(call_strike, put_strike, self.name, expiry)

    @custom_cacher
    def get_synthetic_future_price(
        self, expiry: str = None, underlying_price: float = None
    ) -> float:
        expiry = self.current_expiry if expiry is None else expiry
        underlying_price = (
            self.fetch_ltp() if underlying_price is None else underlying_price
        )
        atm_straddle: Straddle = self.get_strangle(expiry, underlying_price)
        call_price, put_price = atm_straddle.fetch_ltp()
        synthetic_price = atm_straddle.strike + call_price - put_price
        return synthetic_price

    @custom_cacher
    def get_basis_for_expiry(
        self,
        expiry: str = None,
        underlying_price: float = None,
        future_price: float = None,
    ) -> float:
        expiry = self.current_expiry if expiry is None else expiry
        underlying_price = (
            self.fetch_ltp() if underlying_price is None else underlying_price
        )

        if future_price is None:
            atm_straddle: Straddle = self.get_strangle(expiry, underlying_price)
            call_price, put_price = atm_straddle.fetch_ltp()
            future_price = atm_straddle.strike + call_price - put_price
        # The minimum time to expiry is 1 minute to avoid division by zero
        tte = max(time_to_expiry(expiry), 1 / (365 * 24 * 60))
        basis = (future_price / underlying_price) - 1
        annualized_basis = basis / tte
        adjusted_annualized_basis = (
            annualized_basis * 1.01
        )  # A small 1% adjustment to avoid intrinsic value errors
        # Can be removed later
        return adjusted_annualized_basis

    def fetch_atm_info(self, expiry="current", effective_iv=False):
        expiry_dict = {
            "current": self.current_expiry,
            "next": self.next_expiry,
        }
        expiry = expiry_dict[expiry]
        price = self.fetch_ltp()
        atm_straddle = self.get_strangle(expiry, price)
        call_price, put_price = atm_straddle.fetch_ltp()
        synthetic_price = atm_straddle.strike + call_price - put_price
        r = self.get_basis_for_expiry(expiry, price, synthetic_price)
        total_price = call_price + put_price
        call_iv, put_iv, avg_iv = atm_straddle.fetch_ivs(
            spot=price, prices=(call_price, put_price), effective_iv=effective_iv, r=r
        )
        return {
            "underlying_price": price,
            "strike": atm_straddle.strike,
            "call_price": call_price,
            "put_price": put_price,
            "total_price": total_price,
            "synthetic_future_price": synthetic_price,
            "annualized_basis": r,
            "call_iv": call_iv,
            "put_iv": put_iv,
            "avg_iv": avg_iv,
        }

    def fetch_otm_info(self, strike_offset, expiry="current", effective_iv=False):
        expiry_dict = {
            "current": self.current_expiry,
            "next": self.next_expiry,
        }
        expiry = expiry_dict[expiry]
        price = self.fetch_ltp()
        call_strike = price * (1 + strike_offset)
        put_strike = price * (1 - strike_offset)
        call_strike = find_strike(call_strike, self.base)
        put_strike = find_strike(put_strike, self.base)
        otm_strangle = Strangle(call_strike, put_strike, self.name, expiry)
        call_price, put_price = otm_strangle.fetch_ltp()
        total_price = call_price + put_price
        call_iv, put_iv, avg_iv = otm_strangle.fetch_ivs(
            spot=price, prices=(call_price, put_price), effective_iv=effective_iv
        )
        return {
            "underlying_price": price,
            "call_strike": call_strike,
            "put_strike": put_strike,
            "call_price": call_price,
            "put_price": put_price,
            "total_price": total_price,
            "call_iv": call_iv,
            "put_iv": put_iv,
            "avg_iv": avg_iv,
        }

    def get_available_strikes(self, *args, **kwargs):
        return get_available_strikes(self.name, *args, **kwargs)

    def get_constituents(self, cutoff_pct=101):
        constituents = (
            pd.read_csv(f"data/{self.name}_constituents.csv")
            .sort_values("Index weight", ascending=False)
            .assign(cum_weight=lambda df: df["Index weight"].cumsum())
            .loc[lambda df: df.cum_weight < cutoff_pct]
        )

        constituent_tickers, constituent_weights = (
            constituents.Ticker.to_list(),
            constituents["Index weight"].to_list(),
        )

        return constituent_tickers, constituent_weights

    def get_active_strikes(
        self, range_of_strikes: int, offset: float = 0, ltp: float = None
    ) -> list[int]:
        ltp = self.fetch_ltp() if ltp is None else ltp
        strike_range = get_range_of_strikes(ltp, self.base, range_of_strikes, offset)
        return strike_range

    def get_otm_strikes(
        self,
        strike_range: Iterable[int],
        option_type: OptionType,
        spill: int = 2,
        cut_off_pct: float = None,
        spot_price: bool = None,
    ) -> list[int]:
        """Filters out itm strikes and returns tradeable strikes. Spill decides the itm range.
        Cut off percentage is the percentage of strikes to be considered from the ATM strike.
        Default is 3%. Strikes beyond this percentage are filtered out.
        """
        ltp = spot_price or self.fetch_ltp()
        if cut_off_pct is None:
            atm_iv = self.fetch_atm_info()["avg_iv"]
            cut_off_pct = max(4.0, atm_iv * 10)
            # Cap at 10% mainly for backtesting purposes. Can be removed in live.
            cut_off_pct = min(10.0, cut_off_pct)
        cut_off_price = (
            ltp * (1 + cut_off_pct / 100)
            if option_type == OptionType.CALL
            else ltp * (1 - cut_off_pct / 100)
        )
        return [
            strike
            for strike in strike_range
            if option_type == OptionType.CALL
            and ((ltp - spill * self.base) < strike < cut_off_price)
            or option_type == OptionType.PUT
            and ((ltp + spill * self.base) > strike > cut_off_price)
        ]

    def return_greeks_for_strikes(
        self, strike_range=4, expiry=None, option_type=OptionType.CALL
    ):
        if expiry is None:
            expiry = self.current_expiry
        underlying_price = self.fetch_ltp()
        atm_strike = find_strike(underlying_price, self.base)
        strikes = (
            np.arange(atm_strike, atm_strike + strike_range * self.base, self.base)
            if option_type == OptionType.CALL
            else np.arange(
                atm_strike - strike_range * self.base, atm_strike + self.base, self.base
            )
        )
        options = [Option(strike, option_type, self.name, expiry) for strike in strikes]
        greek_dict = {option: option.fetch_greeks() for option in options}
        return greek_dict

    @timeit()
    def most_resilient_strangle(
        self,
        strike_range=40,
        expiry=None,
        extra_buffer=1.07,
    ) -> Strangle:
        def expected_movement(option: Option):
            print(ltp_cache[option])
            raise NotImplementedError

        def find_favorite_strike(expected_moves, options, benchmark_movement):
            for i in range(1, len(expected_moves)):
                if (
                    expected_moves[i] > benchmark_movement * extra_buffer
                    and expected_moves[i] > expected_moves[i - 1]
                ):
                    return options[i]
            return None

        if expiry is None:
            expiry = self.current_expiry

        spot_price = self.fetch_ltp()
        atm_strike = find_strike(spot_price, self.base)

        half_range = int(strike_range / 2)
        strike_range = np.arange(
            atm_strike - (self.base * half_range),
            atm_strike + (self.base * (half_range + 1)),
            self.base,
        )

        options_by_type = {
            OptionType.CALL: [
                Option(
                    strike=strike,
                    option_type=OptionType.CALL,
                    underlying=self.name,
                    expiry=expiry,
                )
                for strike in strike_range
                if strike >= atm_strike
            ],
            OptionType.PUT: [
                Option(
                    strike=strike,
                    option_type=OptionType.PUT,
                    underlying=self.name,
                    expiry=expiry,
                )
                for strike in strike_range[::-1]
                if strike <= atm_strike
            ],
        }

        ltp_cache = {
            option: option.fetch_ltp()
            for option_type in options_by_type
            for option in options_by_type[option_type]
        }

        expected_movements = {
            option_type: [expected_movement(option) for option in options]
            for option_type, options in options_by_type.items()
        }

        expected_movements_ce = np.array(expected_movements[OptionType.CALL])
        expected_movements_pe = np.array(expected_movements[OptionType.PUT])
        expected_movements_pe = expected_movements_pe * -1

        benchmark_movement_ce = expected_movements_ce[0]
        benchmark_movement_pe = expected_movements_pe[0]

        logger.info(
            f"{self.name} - Call options' expected movements: "
            f"{list(zip(options_by_type[OptionType.CALL], expected_movements_ce))}"
        )
        logger.info(
            f"{self.name} - Put options' expected movements: "
            f"{list(zip(options_by_type[OptionType.PUT], expected_movements_pe))}"
        )

        favorite_strike_ce = (
            find_favorite_strike(
                expected_movements_ce,
                options_by_type[OptionType.CALL],
                benchmark_movement_ce,
            )
            or options_by_type[OptionType.CALL][0]
        )  # If no favorite strike, use ATM strike
        favorite_strike_pe = (
            find_favorite_strike(
                expected_movements_pe,
                options_by_type[OptionType.PUT],
                benchmark_movement_pe,
            )
            or options_by_type[OptionType.PUT][0]
        )  # If no favorite strike, use ATM strike

        ce_strike = favorite_strike_ce.strike
        pe_strike = favorite_strike_pe.strike
        strangle = Strangle(ce_strike, pe_strike, self.name, expiry)

        return strangle


class Stock(Index):
    def __init__(self, name):
        check_stock_name(name, symbol_df["SYMBOL"].values)
        super().__init__(name)


class CashStock:
    def __init__(self, name: str):
        self.name = name
        check_stock_name(name, scrips["name"].unique().tolist())
        self.symbol, self.token = get_symbol_token(name)


class IndiaVix:
    if config.backtest_mode:
        symbol, token = "India Vix", "India Vix"
    else:
        symbol, token = None, None

    @classmethod
    def fetch_ltp(cls):
        if cls.symbol is None or cls.token is None:
            cls.symbol, cls.token = get_symbol_token("INDIA VIX")
        return fetch_ltp("NSE", cls.symbol, cls.token)


def check_stock_name(name, list_of_names):
    if name not in list_of_names:
        closest_match, confidence = process.extractOne(name, list_of_names)
        if confidence > 80:
            raise Exception(f"Index {name} not found. Did you mean {closest_match}?")

        else:
            raise ValueError(f"Index {name} not found")
