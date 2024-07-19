import numpy as np
import pandas as pd


class FiinIndicator:
    def __init__(self):

        """
        Initialize the FiinIndicator class with a DataFrame containing stock data.

        """
        pass

    def ema(self, col: pd.Series, window: int):

        """
        Calculate the Exponential Moving Average (EMA) of a data series.

        Parameters:
        col (pd.Series, optional): Input data series
        window (int): Number of observations to use for calculating EMA.
        
        Returns:
        pd.Series: Calculated EMA data series.
        """

        ema = col.ewm(span=window, min_periods=window, adjust=False).mean()
        return ema
            
    def sma(self, col: pd.Series, window: int):

        """
        Calculate the Simple Moving Average (SMA) of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window (int): Number of observations to use for calculating SMA.
        
        Returns:
        - pd.Series: Calculated SMA data series.
        """

        sma = col.rolling(window=window, min_periods=window).mean()
        return sma
    
    def rsi(self, col: pd.Series, window: int = 14):

        """
        Calculate the Relative Strength Index (RSI) of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window (int): Number of observations to use for calculating RSI. Default is 14

        Returns:
        pd.Series: Calculated RSI values.
        """

        delta = col.diff() 
        gain = delta.where(delta > 0, 0) 
        loss = -delta.where(delta < 0, 0) 
        avg_gain = gain.ewm(com=window - 1, min_periods=window, adjust=False).mean() 
        avg_loss = loss.ewm(com=window - 1, min_periods=window, adjust=False).mean() 
        rs = avg_gain / avg_loss.abs() 
        rsi = 100 - (100 / (1 + rs)) 
        rsi[(avg_loss == 0) | (avg_loss == -avg_gain)] = 100  
        return rsi
    
    def macd(self, col: pd.Series, window_slow: int = 26, window_fast: int = 12):

        """
        Calculate the Moving Average Convergence Divergence (MACD) of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window_slow (int): Number of observations for the slow EMA in MACD calculation. Default is 26
        window_fast (int): Number of observations for the fast EMA in MACD calculation. Default is 12

        Returns:
        pd.Series: Calculated MACD values.
        """
         
        ema_fast = self.ema(col, window_fast)
        ema_slow = self.ema(col, window_slow)
        macd_line = ema_fast - ema_slow
        return macd_line

    def macd_signal(self, col: pd.Series, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9):

        """
        Calculate the signal line (SIGNAL) for the MACD of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window_slow (int): Number of observations for the slow EMA in MACD calculation. Default is 26
        window_fast (int): Number of observations for the fast EMA in MACD calculation. Default is 12
        window_sign (int): Number of observations for the signal line calculation. Default is 9

        Returns:
        pd.Series: Calculated MACD signal line values.
        """

        macd_signal_line = self.macd(col, window_slow, window_fast).ewm(span=window_sign, min_periods=window_sign, adjust=False).mean()
        return macd_signal_line

    def macd_diff(self, col: pd.Series, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9):
        
        """
        Calculate the MACD Histogram (MACD Diff) of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window_slow (int): Number of observations for the slow EMA in MACD calculation. Default is 26
        window_fast (int): Number of observations for the fast EMA in MACD calculation. Default is 12
        window_sign (int): Number of observations for the signal line calculation. Default is 9

        Returns:
        pd.Series: Calculated MACD Histogram (MACD Diff) values.
        """
        
        macd_diff_line = self.macd(col, window_slow, window_fast) - self.macd_signal(col, window_sign)
        return macd_diff_line

    def bollinger_mavg(self, col: pd.Series, window: int = 20):

        """
        Calculate the Bollinger Bands - Middle Band (MAVG) of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window (int): Number of observations for calculating the moving average. Default is 20

        Returns:
        pd.Series: Calculated Bollinger Bands - Middle Band values.
        """

        bollinger_mavg = self.sma(col, window)
        return bollinger_mavg

    def bollinger_std(self, col: pd.Series, window: int = 20):

        """
        Calculate the standard deviation of the Bollinger Bands (STD) of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window (int): Number of observations for calculating the standard deviation. Default is 20

        Returns:
        pd.Series: Calculated Bollinger Bands - Standard Deviation values.
        """

        try:
            rolling_windows = np.lib.stride_tricks.sliding_window_view(col, window)
            stds = np.std(rolling_windows, axis=1)
            stds = np.concatenate([np.full(window - 1, np.nan), stds])
            std = pd.Series(stds, index=col.index)
            return std
        except:
            std = pd.Series([np.nan] * col.shape[0])
            return std

    def bollinger_hband(self, col: pd.Series, window: int = 20, window_dev = 2):
        
        """
        Calculate the upper band of the Bollinger Bands (HBAND) of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window (int): Number of observations for calculating the moving average. Default is 20
        window_dev (int): Number of standard deviations for calculating the upper band. Default is 2

        Returns:
        - pd.Series: Calculated Bollinger Bands - Upper Band values.
        """

        bollinger_hband = self.sma(col, window) + (window_dev * self.bollinger_std(col, window))
        return bollinger_hband

    def bollinger_lband(self, col: pd.Series, window: int = 20, window_dev = 2):

        """
        Calculate the lower band of the Bollinger Bands (LBAND) of a data series.

        Parameters:
        col (pd.Series): Input data series.
        window (int): Number of observations for calculating the moving average. Default is 20
        window_dev (int): Number of standard deviations for calculating the lower band. Default is 2

        Returns:
        pd.Series: Calculated Bollinger Bands - Lower Band values.
        """

        bollinger_lband = self.sma(col, window) - (window_dev * self.bollinger_std(col, window))
        return bollinger_lband
    
    def stoch(self, low: pd.Series, high: pd.Series, close: pd.Series, window: int = 14):

        """
        Calculate the Stochastic Oscillator (STOCH) of a data series.

        Parameters:
        low (pd.Series): Input low data series.
        high (pd.Series): Input high data series.
        close (pd.Series): Input close data series.
        window (int): Number of observations for calculating the Stochastic Oscillator. Default is 14

        Returns:
        pd.Series: Calculated Stochastic Oscillator values.
        """

        lowest_low = low.rolling(window=window).min()
        highest_high = high.rolling(window=window).max()
        stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        return stoch_k

    def stoch_signal(self, low: pd.Series, high: pd.Series, close: pd.Series, window: int = 14, smooth_window: int = 3):

        """
        Calculate the signal line (SIGNAL) for the Stochastic Oscillator (STOCH) of a data series.

        Parameters:
        window (int): Number of observations for calculating the Stochastic Oscillator. Default is 14
        smooth_window (int): Number of observations for smoothing the signal line. Default is 3

        Returns:
        pd.Series: Calculated Stochastic Oscillator signal line values.
        """

        stoch_d = self.sma(col=self.stoch(low, high, close, window), window=smooth_window)
        return stoch_d
    
