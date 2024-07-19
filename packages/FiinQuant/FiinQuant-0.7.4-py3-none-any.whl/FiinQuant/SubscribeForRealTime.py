import threading
import time
import pandas as pd
from signalrcore.hub_connection_builder import HubConnectionBuilder
from .RealTimeReturnData import RealTimeReturnData

REALTIME_API = "https://fiinquant-realtime-staging.fiintrade.vn/RealtimeHub?access_token="

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
        
