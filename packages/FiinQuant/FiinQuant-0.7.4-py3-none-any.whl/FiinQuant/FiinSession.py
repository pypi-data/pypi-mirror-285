from datetime import datetime
import time
import requests
from .FiinIndicator import FiinIndicator
from .FiinDataHistorical import FiinDataHistorical
from .SubscribeForRealTime import SubscribeForRealTime


TOKEN_URL = "http://42.112.22.11:9900/connect/token"

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

