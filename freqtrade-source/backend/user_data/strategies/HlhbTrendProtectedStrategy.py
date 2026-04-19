# pragma pylint: disable=missing-docstring, invalid-name
from pandas import DataFrame

import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
from freqtrade.strategy import IStrategy


class HlhbTrendProtectedStrategy(IStrategy):
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

    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        current_candle = dataframe.loc[dataframe["date"] <= current_time].iloc[-1]

        if current_profit < -0.01 and current_candle["ema5"] < current_candle["ema10"]:
            return "early_trend_fail"

        if current_profit < -0.005 and current_candle["rsi"] < 45:
            return "early_rsi_fail"

        if (
            current_profit > 0.01
            and current_candle["ema5"] < current_candle["ema10"]
            and current_candle["rsi"] < 50
        ):
            return "protect_profit"

        return None
