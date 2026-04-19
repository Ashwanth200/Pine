# pragma pylint: disable=missing-docstring, invalid-name
from pandas import DataFrame

import numpy as np
import pandas as pd
import talib.abstract as ta
from freqtrade.strategy import IStrategy


class SupertrendConservativeStrategy(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "1h"
    startup_candle_count = 199
    process_only_new_candles = True

    minimal_roi = {
        "0": 0.087,
        "372": 0.058,
        "861": 0.029,
        "2221": 0.0,
    }

    stoploss = -0.265
    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.144
    trailing_only_offset_is_reached = False

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

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
        buy_specs = [(4, 8), (7, 9), (1, 8)]
        sell_specs = [(1, 16), (3, 18), (6, 18)]

        for index, (multiplier, period) in enumerate(buy_specs, start=1):
            st = self.supertrend(dataframe, multiplier, period)
            dataframe[f"supertrend_{index}_buy"] = st["STX"]

        for index, (multiplier, period) in enumerate(sell_specs, start=1):
            st = self.supertrend(dataframe, multiplier, period)
            dataframe[f"supertrend_{index}_sell"] = st["STX"]

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["supertrend_1_buy"] == "up")
                & (dataframe["supertrend_2_buy"] == "up")
                & (dataframe["supertrend_3_buy"] == "up")
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["supertrend_1_sell"] == "down")
                & (dataframe["supertrend_2_sell"] == "down")
                & (dataframe["supertrend_3_sell"] == "down")
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe

    def supertrend(self, dataframe: DataFrame, multiplier: int, period: int) -> DataFrame:
        high = dataframe["high"].to_numpy()
        low = dataframe["low"].to_numpy()
        close = dataframe["close"].to_numpy()
        length = len(dataframe)

        tr = ta.TRANGE(dataframe)
        atr = pd.Series(tr).rolling(period).mean().to_numpy()

        basic_ub = (high + low) / 2 + multiplier * atr
        basic_lb = (high + low) / 2 - multiplier * atr

        final_ub = np.zeros(length)
        final_lb = np.zeros(length)

        for idx in range(period, length):
            final_ub[idx] = (
                basic_ub[idx]
                if basic_ub[idx] < final_ub[idx - 1] or close[idx - 1] > final_ub[idx - 1]
                else final_ub[idx - 1]
            )
            final_lb[idx] = (
                basic_lb[idx]
                if basic_lb[idx] > final_lb[idx - 1] or close[idx - 1] < final_lb[idx - 1]
                else final_lb[idx - 1]
            )

        st = np.zeros(length)
        for idx in range(period, length):
            if st[idx - 1] == final_ub[idx - 1]:
                st[idx] = final_ub[idx] if close[idx] <= final_ub[idx] else final_lb[idx]
            elif st[idx - 1] == final_lb[idx - 1]:
                st[idx] = final_lb[idx] if close[idx] >= final_lb[idx] else final_ub[idx]

        stx = np.where(st > 0, np.where(close < st, "down", "up"), None)
        result = pd.DataFrame({"ST": st, "STX": stx}, index=dataframe.index)
        result.fillna(0, inplace=True)
        return result
