# pragma pylint: disable=missing-docstring, invalid-name
from pandas import DataFrame

import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
from freqtrade.strategy import IStrategy


class HlhbTrendDynamicRiskStrategy(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "4h"
    startup_candle_count = 199
    process_only_new_candles = True

    minimal_roi = {
        "0": 0.6225,
        "703": 0.2187,
        "2849": 0.0363,
        "5520": 0.0,
    }

    stoploss = -0.10
    trailing_stop = True
    trailing_stop_positive = 0.0117
    trailing_stop_positive_offset = 0.0186
    trailing_only_offset_is_reached = True

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True

    order_types = {
        "entry": "market",
        "exit": "market",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC",
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        hl2 = (dataframe["close"] + dataframe["open"]) / 2
        dataframe["rsi"] = ta.RSI(hl2, timeperiod=10)
        dataframe["ema5"] = ta.EMA(dataframe, timeperiod=5)
        dataframe["ema10"] = ta.EMA(dataframe, timeperiod=10)
        dataframe["adx"] = ta.ADX(dataframe)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["rsi"], 50)
                & qtpylib.crossed_above(dataframe["ema5"], dataframe["ema10"])
                & (dataframe["adx"] > 25)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["rsi"], 50)
                & qtpylib.crossed_below(dataframe["ema5"], dataframe["ema10"])
                & (dataframe["adx"] > 25)
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        starting_balance = self.wallets.get_starting_balance()
        current_equity = self.wallets.get_total_stake_amount()

        risk_pct = 0.01 if current_equity >= starting_balance else 0.005
        risk_amount = current_equity * risk_pct
        stop_distance = abs(self.stoploss)

        stake = risk_amount / stop_distance
        stake = min(stake, max_stake)
        if min_stake is not None:
            stake = max(stake, min_stake)
        return stake
