# ==============================================================================================
# "3.9 Million" trading strategy for FUTURES/SPOT
#
# Made by:
# ______         _         _      _____                      _         ______            _
# |  _  \       | |       | |    /  __ \                    | |        |  _  \          | |
# | | | | _   _ | |_  ___ | |__  | /  \/ _ __  _   _  _ __  | |_  ___  | | | | __ _   __| |
# | | | || | | || __|/ __|| '_ \ | |    | '__|| | | || '_ \ | __|/ _ \ | | | |/ _` | / _` |
# | |/ / | |_| || |_| (__ | | | || \__/\| |   | |_| || |_) || |_| (_) || |/ /| (_| || (_| |
# |___/   \__,_| \__|\___||_| |_| \____/|_|    \__, || .__/  \__|\___/ |___/  \__,_| \__,_|
#                                               __/ || |
#                                              |___/ |_|
# Become my Patron: https://www.patreon.com/dutchalgotrading
#
# Version : 1.0
# Date    : 2023-09
#
# Remarks :
# As published, explained and tested in my Youtube video on my channel: https://www.youtube.com/@dutchalgotrading
#
# This strategy is inspired by the following Youtube video's
# * https://www.youtube.com/watch?v=E6pgaBOXwCk
# * https://www.youtube.com/watch?v=0dnwWvo4WOY
# * https://www.youtube.com/watch?v=dwlXUt40Mp8
# * https://www.youtube.com/watch?v=J4lGSNwftsM
#
# All credits go to these people if this strategy will also make you 3.9 million usd. I'm just coding this stuff for you.
#
# freqtrade backtesting -c user_data/spot_config.json -s Million --timerange=20190101-20210530 --timeframe=1d
# freqtrade plot-dataframe -c user_data/spot_config.json -s Million --timerange=20200101-20210530 --timeframe=1d -p BTC/USDT
#
# freqtrade backtesting -c user_data/futures_config.json -s Million --timerange=20210101-20210530 --timeframe=1d
# freqtrade plot-dataframe -c user_data/futures_config.json -s Million --timerange=20200101-20210530 --timeframe=1d -p MATIC/USDT:USDT
# ==============================================================================================
# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
from functools import reduce
import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional, Union

from freqtrade.strategy import (
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    IStrategy,
    merge_informative_pair,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
from technical import qtpylib


class GIDLE(IStrategy):
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Proposed timeframe for the strategy. Can be altered to your own preferred timeframe.
    timeframe = "1d"

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # Set to 100%
    minimal_roi = {"0": 10.0}

    # Optimal stoploss designed for the strategy.
    # Set to 100%
    stoploss = -1.0

    # Trailing stoploss
    trailing_stop = False

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    # Set to the default of 30.
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    # Optional order time in force.
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Gann Hilo
        dataframe['hilo'] = pta.hilo(high=dataframe['high'], low=dataframe['low'], close=dataframe['close'],
                                     high_length=13, low_length=21, mamode=None, offset=None)["HILO_13_21"]

        # Ichimoku Chikou span
        # dataframe['chikou'] = pta.ichimoku(high=dataframe['high'], low=dataframe['low'], close=dataframe['close'], tenkan=9, kijun=10, senkou=52, include_chikou=True, offset=0)[0]['ICS_10']

        dataframe['imi'] = calculate_imi(dataframe, length=50)

        dataframe['imi_ema'] = pta.ema(close=dataframe['imi'], length=7)

        # Assuming you have a DataFrame 'dataframe' with columns: 'date', 'open', 'high', 'low', 'close', 'volume'
        # You can calculate the IMI like this:
        dataframe['imi'] = calculate_imi(dataframe, length=7)

        # Detrended Price Oscillator
        dataframe['dpo'] = pta.dpo(close=dataframe['close'], length=14,
                                   centered=True, lookahead=False)

        dataframe['lsma'] = calculate_lsma(dataframe, 14)

        # Ehlers Ficher transform indicator
        dataframe['fisherT'] = pta.fisher(high=dataframe['high'], low=dataframe['low'],
                                          close=dataframe['close'], length=9)['FISHERT_9_1']
        dataframe['fishers'] = pta.fisher(high=dataframe['high'], low=dataframe['low'],
                                          close=dataframe['close'], length=9)['FISHERTs_9_1']

        # Add trade and exit signals to the dataframe.
        entry_signals(dataframe)
        exit_signals(dataframe)

        # first check if dataprovider is available
        if self.dp:
            if self.dp.runmode.value in ("live", "dry_run"):
                ob = self.dp.orderbook(metadata["pair"], 1)
                dataframe["best_bid"] = ob["bids"][0][0]
                dataframe["best_ask"] = ob["asks"][0][0]

        print(self)
        print(metadata)
        print(dataframe.tail(15))
        # print(dataframe[['date', 'close', 'regression_line', 'trend', 'ut_direction', 'ut_bot_signal', 'trade_signal', 'exit_signal']][(
        #     dataframe['trade_signal'] == 'Go_long') | (dataframe['trade_signal'] == 'Go_short')].tail(20))
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Long trades here:
        conditions = []
        conditions.append(
            (dataframe['entry_direction'] == 'Go_long' & dataframe['entry_signal'] == True)
            # (dataframe['trend'] == 'Rising' and dataframe['ut_direction'] == 1 and dataframe['ut_bot_signal'])
            & (dataframe["volume"] > 0)  # Guard
        )
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1

        # For short trades, use the section below
        conditions.append(
            (dataframe['entry_direction'] == 'Go_short' & dataframe['entry_signal'] == True)
            # (dataframe['trend'] == 'Falling' and dataframe['ut_direction'] == 0 and dataframe['ut_bot_signal'])
            & (dataframe["volume"] < 0)  # Guard
        )
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Exit long here:
        conditions = []
        conditions.append(
            (dataframe['exit_direction'] == 'Exit_long' & dataframe['exit_signal'] == True)
            # (dataframe['ut_direction'] == 0 and dataframe['ut_bot_signal'])
            & (dataframe["volume"] > 0)  # Guard
        )
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'] = 1

        # For short trades, use the section below
        conditions.append(
            (dataframe['exit_direction'] == 'Exit_short' & dataframe['exit_signal'] == True)
            # (dataframe['ut_direction'] == 1 and dataframe['ut_bot_signal'])
            & (dataframe["volume"] > 0)  # Guard
        )
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_short'] = 1

        return dataframe


# === Functions section ===
def entry_signals(df):
    # Create boolean masks for each condition
    long_condition = (df['dpo'] > 0) & (df['lsma'] > df['hilo']) & (df['imi'] > df['imi_ema'])
    short_condition = (df['dpo'] < 0) & (df['lsma'] < df['hilo']) & (df['imi'] < df['imi_ema'])

    # Create 'trade_direction' column based on conditions
    df['entry_direction'] = np.where(long_condition, 'Go_long', np.where(
        short_condition, 'Go_short', 'Stay_neutral'))

    # Calculate trade signals based on changes in 'trade_direction' and trend condition
    df['entry_changed'] = df['entry_direction'].shift(1) != df['entry_direction']
    df['entry_signal'] = np.where(df['entry_changed'] & (
        (df['entry_direction'] == 'Go_long') | (df['entry_direction'] == 'Go_short')), True, False)

    # Clean up by dropping the 'trend_changed' column
    df.drop(columns=['entry_changed'], inplace=True)

    return df


def exit_signals(df):
    # Create boolean masks for exit conditions
    exit_long_condition = (df['fisherT'] < df['fishers'])
    exit_short_condition = (df['fisherT'] > df['fishers'])

    # Create 'exit_signal' column based on exit conditions
    df['exit_direction'] = np.where(exit_long_condition, 'Exit_long', np.where(
        exit_short_condition, 'Exit_short', 'Do_nothing'))

    # Calculate exit trade signals based on changes in 'exit_signal'
    df['exit_signal'] = df['exit_direction'].shift(1) != df['exit_direction']

    return df


def calculate_imi(dataframe, length=14):
    # Calculate gains and losses
    dataframe['gain'] = 0.0
    dataframe['loss'] = 0.0

    for i in range(1, len(dataframe)):
        if dataframe['close'].iloc[i] > dataframe['open'].iloc[i]:
            dataframe.at[dataframe.index[i], 'gain'] = dataframe['close'].iloc[i] - \
                dataframe['open'].iloc[i]
        else:
            dataframe.at[dataframe.index[i], 'loss'] = dataframe['open'].iloc[i] - \
                dataframe['close'].iloc[i]

    # Calculate sums of gains and losses over 'length' periods
    dataframe['up_sum'] = dataframe['gain'].rolling(window=length).sum()
    dataframe['down_sum'] = dataframe['loss'].rolling(window=length).sum()

    # Calculate IMI
    dataframe['imi'] = 100 * dataframe['up_sum'] / (dataframe['up_sum'] + dataframe['down_sum'])

    # Clean up and drop intermediate columns
    dataframe.drop(['gain', 'loss', 'up_sum', 'down_sum'], axis=1, inplace=True)

    return dataframe['imi']


def calculate_lsma(data, period=21):
    lsma_values = []

    for i in range(period, len(data)):
        # Extract the most recent N data points
        subset = data.iloc[i - period:i]

        # Perform linear regression to fit a line
        x = np.arange(len(subset))
        y = subset['close'].values
        slope, intercept = np.polyfit(x, y, 1)

        # Calculate the LSMA value using the linear equation
        lsma = intercept + slope * (period - 1)
        lsma_values.append(lsma)

    lsma_series = pd.Series(lsma_values, index=data.index[period:])

    return lsma_series
