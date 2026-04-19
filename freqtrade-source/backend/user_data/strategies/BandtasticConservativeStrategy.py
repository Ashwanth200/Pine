# pragma pylint: disable=missing-docstring, invalid-name
from pandas import DataFrame

import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
from freqtrade.strategy import IStrategy


class BandtasticConservativeStrategy(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "15m"
    startup_candle_count = 50
    process_only_new_candles = True

    minimal_roi = {
        "0": 0.162,
        "69": 0.097,
        "229": 0.061,
        "566": 0.0,
    }

    stoploss = -0.345
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.058
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
        dataframe["rsi"] = ta.RSI(dataframe)
        dataframe["mfi"] = ta.MFI(dataframe)

        bollinger_1 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=1)
        dataframe["bb_lowerband1"] = bollinger_1["lower"]
        dataframe["bb_upperband1"] = bollinger_1["upper"]

        bollinger_2 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe["bb_lowerband2"] = bollinger_2["lower"]
        dataframe["bb_upperband2"] = bollinger_2["upper"]

        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=211)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=250)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"] < dataframe["bb_lowerband1"])
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"] > dataframe["bb_upperband2"])
                & (dataframe["mfi"] > 46)
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe
