from datetime import datetime, timedelta
import pandas as pd
import requests
from .HistoricalReturnData import HistoricalReturnData

HISTORICAL_API = "https://fiinquant-staging.fiintrade.vn/TradingView/GetStockChartData"

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

