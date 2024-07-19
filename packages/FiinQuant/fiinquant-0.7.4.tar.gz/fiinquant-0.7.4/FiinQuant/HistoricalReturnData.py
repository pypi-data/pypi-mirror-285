class HistoricalReturnData:
    def __init__(self, data):
        self.__private_attribute = data
        self.Open = data.Open
        self.Close = data.Close
        self.Low = data.Low
        self.High = data.High
        self.Volume = data.Volume
        self.Timestamp = data.Timestamp

    def toDataFrame(self):
        return self.__private_attribute

