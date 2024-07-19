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

