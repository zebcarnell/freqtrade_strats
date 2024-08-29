# Freqtrade trading strategy file

# Import necessary libraries
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SEMAv1(IStrategy):
    """
    This strategy buys when the EMA 50 crosses the EMA 200 upwards and sells when the EMA 50 crosses the EMA 200 downwards.
    """

    # Define the short and long EMAs
    short_ema = 50
    long_ema = 200

    # Define the minimum profit required to sell
    min_profit = 0.01

    # Define the minimum volume required to buy
    min_volume = 100

    # Define the stop loss percentage
    stop_loss = -0.30

    # Define the take profit percentage
    take_profit = 0.10

    # Define the timeframe for the EMA calculations
    timeframe = '1h'

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.30

    # Define the indicators
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds custom indicators to the dataframe.
        """
        # Calculate the short and long EMAs
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=self.short_ema)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=self.long_ema)

        # Calculate the crossover
        dataframe['cross'] = (dataframe['ema_short'] > dataframe['ema_long']) & (dataframe['ema_short'].shift(1) <= dataframe['ema_long'].shift(1))

        # Add the stop_loss column to the DataFrame
        dataframe['stop_loss'] = self.stop_loss

        return dataframe

    # Define the buy conditions
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds custom buy conditions to the dataframe.
        """
        # Buy when the EMA 50 crosses the EMA 200 upwards
        dataframe.loc[
            (dataframe['cross'] & (dataframe['ema_short'].shift(1) <= dataframe['ema_long'].shift(1))),
            'buy'] = 1

        return dataframe

    # Define the sell conditions
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds custom sell conditions to the dataframe.
        """
        # Sell when the EMA 50 crosses the EMA 200 downwards
        dataframe.loc[
            (dataframe['cross'] & (dataframe['ema_short'].shift(1) > dataframe['ema_long'].shift(1))),
            'sell'] = 1

        # Sell when the price drops below the stop loss
        dataframe.loc[
            (dataframe['close'] < dataframe['stop_loss']),
            'sell'] = 1

        return dataframe