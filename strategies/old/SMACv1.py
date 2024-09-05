from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib

class SMACv1(IStrategy):
    INTERFACE_VERSION = 2

    # Define the minimum profit required to sell
    min_profit = 0.01

    # Define the minimum volume required to buy
    min_volume = 100

    # Define the stop loss percentage
    stop_loss = -0.30

    # Define the take profit percentage
    take_profit = 0.10

    # Define the timeframe
    timeframe = '1h'

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.30

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['macd'] = talib.MACD(dataframe['close'])
        dataframe['macd_signal'] = dataframe['macd'].iloc[:, 1]
        dataframe['macd_hist'] = dataframe['macd'].iloc[:, 2]
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['macd_hist'].shift(1) < 0) &
                (dataframe['macd_hist'] > 0)
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['macd_hist'].shift(1) > 0) &
                (dataframe['macd_hist'] < 0)
            ),
            'sell'] = 1
        return dataframe