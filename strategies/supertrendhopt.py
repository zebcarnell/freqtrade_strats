# --- Do not remove these libs ---
import talib.abstract as ta
import pandas_ta as pta
import numpy as np  # noqa
import pandas as pd  # noqa
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
from functools import reduce
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)

class supertrendhopt(IStrategy):
    timeframe = "1d"
    stoploss = -1
    minimal_roi = {"0": 100.0}

# --- Plotting ---

    # Use this section if you want to plot the indicators on a chart after backtesting
    plot_config = {
        'main_plot': {
            # Create sma line
            'supertrend': {'color': 'green'},
        },
#        'subplots': {
#            "MACD": {
#                'macd': {'color': 'blue', 'fill_to': 'macdsignal'},
#                'macdsignal': {'color': 'orange'},
#                'macdhist': {'color': 'green', 'type': 'bar', 'plotly': {'opacity': 0.4}}
#            },
#        },
    }

# --- Define spaces for the indicators ---
    # st_length = IntParameter(14, 17, default=21, space="buy")
    st_length = CategoricalParameter([14, 15, 16, 17, 18], default=14, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Supertrend
        # Loop over length space
        smult = 5.0
        for i in self.st_length.range:
            print(metadata['pair'], self.st_length.range, i)
            dataframe[f"supertrend_{i}"] = pta.supertrend(
                high=dataframe["high"],
                low=dataframe["low"],
                close=dataframe["close"],
                length=i,
                multiplier=smult,
            )[f"SUPERT_{i}_{smult}"]

        # print(self.st_length.range)
        # print(dataframe)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
       conditions = []
       conditions.append(
           (dataframe['close'] > dataframe[f'supertrend_{self.st_length.value}'])
           )

       if conditions:
           dataframe.loc[
               reduce(lambda x, y: x & y, conditions),
               'buy'] = 1

       return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
       conditions = []
       conditions.append(
           (dataframe['close'] < dataframe[f'supertrend_{self.st_length.value}'])
           )

       if conditions:
           dataframe.loc[
               reduce(lambda x, y: x & y, conditions),
               'sell'] = 1

       return dataframe
