import time
import requests
import threading
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from signalrcore.hub_connection_builder import HubConnectionBuilder


TOKEN_URL = "http://42.112.22.11:9900/connect/token"
HISTORICAL_API = "https://fiinquant-staging.fiintrade.vn/TradingView/GetStockChartData"
REALTIME_API = "https://fiinquant-realtime-staging.fiintrade.vn/RealtimeHub?access_token="
USERNAME_API = 'fiinquant.staging@fiingroup.vn'
PASSWORD_API = 'sdksoiILelrbJ909)_)aOKknn456'

GRANT_TYPE = 'password'
CLIENT_ID = 'FiinTrade.Customer.Client'
CLIENT_SECRET = 'fiintrade-Cus2023'
SCOPE = 'openid fiintrade.customer'
USERNAME = ''
PASSWORD = ''


class FiinSession:
    def __init__(self, username, password):

        """
        Initialize a session for fetching financial data.

        Parameters:
        username (str): The username for authentication.
        password (str): The password for authentication.
        """

        self.username = username
        self.password = password
        self.access_token = None
        self.expired_token = None
        self.urlGetToken = TOKEN_URL
        self.bodyGetToken = {
            'grant_type': GRANT_TYPE,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': SCOPE,
            'username': USERNAME,
            'password': PASSWORD
        }

    def login(self):
        self.bodyGetToken['username'] = self.username
        self.bodyGetToken['password'] = self.password

        try:
            response = requests.post(self.urlGetToken, data=self.bodyGetToken)
            if response.status_code == 200:
                res = response.json()
                self.access_token = res['access_token']
                self.expired_token = res['expires_in'] + int(time.time())
                self.is_login = True
            else:
                self.is_login = False
        except:
            self.is_login = False
        
    def is_expired_token(self): # expired => True, still valid => False
        expires_in = self.expired_token
        current_time = int(time.time())

        try: # login
            if expires_in < current_time: # expired 
                self.is_login = False
                return True       
            else: 
                self.is_login = True
                return False
        except:
            self.is_login = False
            return True
    
    def get_access_token(self):
        if self.is_expired_token():
            self.login()
        return self.access_token
    
    def FiinDataHistorical(self, 
                 ticker: str, 
                 from_date: datetime = '2000-01-01 00:00:00', 
                 to_date: datetime = datetime.now(), 
                 multiplier: int = 1, 
                 timespan: str = 'minute', 
                 limit: int = 1000):
        
        """
        Fetch financial data for a given ticker symbol within a specified date range.

        Parameters:
        ticker (str): The ticker symbol of the financial instrument.
        from_date (datetime): The start time of the data fetching period. format 'YYYY-MM-DD hh:mm:ss'
        to_date (datetime): The end time of the data fetching period. format 'YYYY-MM-DD hh:mm:ss'
        multiplier (int): The time period multiplier (e.g., 1 means 1 minute, 2 means 2 minutes). Default is 1.
        timespan (str): The granularity of the data ('minute', 'hour', 'day'). Default is 'minute'.
        limit (int): The maximum number of data points to fetch. Default is 1000.
        """

        access_token = self.get_access_token()    
        return FiinDataHistorical(access_token, ticker, from_date, to_date, multiplier, timespan, limit)

    def FiinIndicator(self):

        """
        Initialize the FiinIndicator function with a DataFrame containing stock data.

        Parameters:
        df (pd.DataFrame): A DataFrame containing stock data. 
        It should have columns such as 'Timestamp', 'Open', 'Low', 'High', 'Low' and 'volume'.
        """

        return FiinIndicator()
    
    def SubscribeForRealTime(self, ticker: str, callback: callable):
        access_token = self.get_access_token() 
        return SubscribeForRealTime(access_token, ticker, callback)


class HistoricalReturnData:
    def __init__(self, data):
        self.data = data
        self.Open = data.Open
        self.Close = data.Close
        self.Low = data.Low
        self.High = data.High
        self.Volume = data.Volume
        self.Timestamp = data.Timestamp

    def toDataFrame(self):
        return self.data


class RealTimeReturnData:
    def __init__(self, data):
        self.data = data
        self.TotalMatchVolume = data['TotalMatchVolume']
        self.MarketStatus = data['MarketStatus']
        self.TradingDate = data['TradingDate']
        self.MatchType = data['MatchType']
        self.ComGroupCode = data['ComGroupCode']
        self.OrganCode = data['OrganCode']
        self.Ticker = data['Ticker']
        self.ReferencePrice = data['ReferencePrice']
        self.OpenPrice = data['OpenPrice']
        self.ClosePrice = data['ClosePrice']
        self.CeilingPrice = data['CeilingPrice']
        self.FloorPrice = data['FloorPrice']
        self.HighestPrice = data['HighestPrice']
        self.LowestPrice = data['LowestPrice']
        self.MatchPrice = data['MatchPrice']
        self.PriceChange = data['PriceChange']
        self.PercentPriceChange = data['PercentPriceChange']
        self.MatchVolume = data['MatchVolume']
        self.MatchValue = data['MatchValue']
        self.TotalMatchValue = data['TotalMatchValue']
        self.TotalBuyTradeVolume = data['TotalBuyTradeVolume']
        self.TotalSellTradeVolume = data['TotalSellTradeVolume']
        self.DealPrice = data['DealPrice']
        self.TotalDealVolume = data['TotalDealVolume']
        self.TotalDealValue = data['TotalDealValue']
        self.ForeignBuyVolumeTotal = data['ForeignBuyVolumeTotal']
        self.ForeignBuyValueTotal = data['ForeignBuyValueTotal']
        self.ForeignSellVolumeTotal = data['ForeignSellVolumeTotal']
        self.ForeignSellValueTotal = data['ForeignSellValueTotal']
        self.ForeignTotalRoom = data['ForeignTotalRoom']
        self.ForeignCurrentRoom = data['ForeignCurrentRoom']

    def toDataFrame(self):
        return self.data


class FiinDataHistorical:
    def __init__(self,
                 access_token: str,
                 ticker: str, 
                 from_date, 
                 to_date, 
                 multiplier: int = 1, 
                 timespan: str = 'minute', 
                 limit: int = 1000):
        
        self.ticker = ticker
        self.from_date = from_date
        self.to_date = to_date
        self.multiplier = multiplier
        self.timespan = timespan
        self.limit = limit
        self.access_token = access_token
        self.urlGetDataStock = HISTORICAL_API
        self.data = self.formatData()

    def fetch_historical_data(self):

        # parameters for API
        param = {
            'Code' : self.ticker, 
            'Type' : 'stock', # Stock, Index, CoveredWarrant, Derivative
            'Frequency' : 'EachMinute', # EachMinute, EachOneHour, Daily
            'From' : self.from_date,
            'To' : self.to_date,
            'PageSize' : self.limit
        }
        bearer_token = self.access_token
        header = {'Authorization': f'Bearer {bearer_token}'}
        response = requests.get(url=self.urlGetDataStock, params=param, headers=header)

        if response.status_code == 200:
            res = response.json()
            df = pd.DataFrame(res['items'])
            return df
        
    def preprocess_data(self):
        self.df = self.df.drop(columns=['rateAdjusted', 'openInterest'])
        self.df = self.df.rename(columns={
            "tradingDate": "Timestamp", 
            "openPrice": "Open", 
            "lowestPrice": "Low", 
            "highestPrice": "High", 
            "closePrice": "Close", 
            "totalMatchVolume": "Volume", 
        })
        self.df[['Open', 'Low', 'High', 'Close']] /= 1000
        self.df['Volume'] = self.df['Volume'].astype(int)
        self.df = self.df[['Timestamp', 'Open', 'Low', 'High', 'Close', 'Volume']]
        return self.df
    
    def round_time(self, dt, start_time):
        if self.timespan == 'minute':
            interval = self.multiplier
        if self.timespan == 'hour':
            interval = self.multiplier * 60
        if self.timespan == 'day':
            interval = self.multiplier * 60 * 24

        time_diff = (dt - start_time).total_seconds() / 60
        rounded_minutes = round(time_diff / interval) * interval
        rounded_time = start_time + timedelta(minutes=rounded_minutes)
        return rounded_time
    
    def group_by_data(self):
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'])
        if self.timespan == 'minute':
            start_time = datetime.combine(datetime.today(), datetime.strptime("09:15", "%H:%M").time())
            self.df['Timestamp'] = self.df['Timestamp'].apply(lambda x: self.round_time(x, start_time)).dt.strftime('%Y-%m-%d %H:%M')
        if self.timespan == 'hour':
            start_time = datetime.combine(datetime.today(), datetime.strptime("09:00", "%H:%M").time())
            self.df['Timestamp'] = self.df['Timestamp'].apply(lambda x: self.round_time(x, start_time)).dt.strftime('%Y-%m-%d %H:00')
        if self.timespan == 'day':
            start_time = datetime.combine(datetime.today(), datetime.strptime("09:15", "%H:%M").time())
            self.df['Timestamp'] = self.df['Timestamp'].apply(lambda x: self.round_time(x, start_time)).dt.strftime('%Y-%m-%d 00:00')

        self.df = self.df.groupby('Timestamp').agg({
            'Open': 'first',
            'Low': 'min',
            'High': 'max',
            'Close': 'last',
            'Volume': 'sum'
        }).reset_index()

        return self.df

    def formatData(self):
        self.df = self.fetch_historical_data()
        self.df = self.preprocess_data()
        self.data = self.group_by_data()
        return self.data
    
    def getData(self):
        return HistoricalReturnData(self.data)


class SubscribeForRealTime:
    def __init__(self, access_token: str, ticker: str, callback: callable):
        self.url = REALTIME_API
        self.hub_connection = self._build_connection()
        self.connected = False 
        self.callback = callback
        self.access_token = access_token
        self.df = pd.DataFrame(columns=[
            'TotalMatchVolume', 'MarketStatus', 'TradingDate', 'MatchType', 'ComGroupCode',
            'OrganCode', 'Ticker', 'ReferencePrice', 'OpenPrice', 'ClosePrice', 'CeilingPrice',
            'FloorPrice', 'HighestPrice', 'LowestPrice', 'MatchPrice', 'PriceChange',
            'PercentPriceChange', 'MatchVolume', 'MatchValue', 'TotalMatchValue',
            'TotalBuyTradeVolume', 'TotalSellTradeVolume', 'DealPrice', 'TotalDealVolume',
            'TotalDealValue', 'ForeignBuyVolumeTotal', 'ForeignBuyValueTotal',
            'ForeignSellVolumeTotal', 'ForeignSellValueTotal', 'ForeignTotalRoom',
            'ForeignCurrentRoom'
        ])
        self.ticker = ticker
        self._stop_event = threading.Event()

    def data_handler(self, message):
        if message is not None:
            self.df.loc[len(self.df)] = message[0]['data'][0].split('|') 
            self.return_data = RealTimeReturnData(self.df[-1:])
            
            if self.callback:
                self.callback(self.return_data)

    def _build_connection(self):
        return HubConnectionBuilder()\
            .with_url(self.url, options={
                "access_token_factory": lambda: self.access_token
            })\
            .with_automatic_reconnect({
                "type": "raw",
                "keep_alive_interval": 1,
                "reconnect_interval": [1, 3, 5, 7, 11]
            }).build()

    def receive_message(self, message):
        self.data_handler(message)

    def handle_error(self, error):
        print(f"Error: {error}")

    def on_connect(self):
        self.connected = True
        print("Connection established")
        self.join_groups()

    def on_disconnect(self):
        self.connected = False
        print("Disconnected from the hub")

    def join_groups(self):
        if self.connected:
            self.hub_connection.send("JoinGroup", [f"Realtime.Ticker.{self.ticker}"])
            print(f"Joined group: Realtime.Ticker.{self.ticker}")
        else:
            print("Cannot join groups, not connected")

    def _run(self):
        if self.hub_connection.transport is not None:
            print("Already connected, stopping existing connection before starting a new one.")
            self.hub_connection.stop()

        self.hub_connection.on("ReceiveMessage", self.receive_message)
        self.hub_connection.on_close(self.handle_error)
        self.hub_connection.on_open(self.on_connect)
        self.hub_connection.on_close(self.on_disconnect)
        self.hub_connection.start()
        
        while not self._stop_event.is_set():
           time.sleep(1)
        
    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        
    def stop(self):
        self._stop_event.set()
        if self.connected:
            print("Disconnecting...")
            self.hub_connection.stop()
        self.thread.join()
        

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
    

