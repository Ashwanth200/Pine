# pragma pylint: disable=missing-docstring, invalid-name
from datetime import datetime

import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, stoploss_from_absolute, stoploss_from_open


class HlhbIctRiskStrategy(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "4h"
    startup_candle_count = 199
    process_only_new_candles = True

    minimal_roi = {
        "0": 0.05,
        "720": 0.025,
        "2160": 0.01,
        "4320": 0.0,
    }

    stoploss = -0.12
    use_custom_stoploss = True
    trailing_stop = False

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
        hl2 = (dataframe["close"] + dataframe["open"]) / 2
        dataframe["rsi"] = ta.RSI(hl2, timeperiod=10)
        dataframe["ema5"] = ta.EMA(dataframe, timeperiod=5)
        dataframe["ema10"] = ta.EMA(dataframe, timeperiod=10)
        dataframe["adx"] = ta.ADX(dataframe)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]
        dataframe["atr_pct_mean"] = dataframe["atr_pct"].rolling(20).mean()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["rsi"], 50)
                & qtpylib.crossed_above(dataframe["ema5"], dataframe["ema10"])
                & (dataframe["adx"] > 25)
                & (dataframe["atr_pct"] < dataframe["atr_pct_mean"] * 1.5)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (
                    qtpylib.crossed_below(dataframe["rsi"], 50)
                    | qtpylib.crossed_below(dataframe["ema5"], dataframe["ema10"])
                    | (dataframe["atr_pct"] > dataframe["atr_pct_mean"] * 2.0)
                )
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> float | None:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        current_candle = dataframe.loc[dataframe["date"] <= current_time].iloc[-1]
        atr_stop = stoploss_from_absolute(
            current_rate - (current_candle["atr"] * 2.0),
            current_rate,
            is_short=trade.is_short,
            leverage=trade.leverage,
        )

        if current_profit >= 0.04:
            protected_stop = stoploss_from_open(
                0.01,
                current_profit,
                is_short=trade.is_short,
                leverage=trade.leverage,
            )
            return min(atr_stop, protected_stop)

        if current_profit >= 0.02:
            breakeven_stop = stoploss_from_open(
                0.0,
                current_profit,
                is_short=trade.is_short,
                leverage=trade.leverage,
            )
            return min(atr_stop, breakeven_stop)

        return atr_stop
