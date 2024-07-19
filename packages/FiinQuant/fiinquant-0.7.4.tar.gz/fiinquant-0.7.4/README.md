# FiinQuant
Python package for financial technical indicators.

## Installation
You can install the package via pip:

```python
pip install --upgrade FiinQuant
```

## Usage

### Historical Data
```python
from FiinQuant import FiinSession

client = FiinSession(
    username='fiinquant.staging@fiingroup.vn',
    password='sdksoiILelrbJ909)_)aOKknn456',
)

data = client.FiinDataHistorical(
    ticker="HPG", 
    from_date='2024-06-16 09:15:00', 
    to_date='2024-07-17 14:29:00', 
    multiplier=1, 
    timespan='minute',  
    limit=100).getData()

df = data.toDataFrame()

fi = client.FiinIndicator()
df['EMA_5'] = fi.ema(df['Close'], window = 5)
df['SMA_5'] = fi.sma(df['Close'], window = 5)
df['RSI'] = fi.rsi(df['Close'], window = 14)
df['MACD'] = fi.macd(df['Close'], window_slow = 26, window_fast = 12)
df['MACD_Signal'] = fi.macd_signal(df['Close'], window_slow = 26, window_fast = 12, window_sign = 9)
df['MACD_Diff'] = fi.macd_diff(df['Close'], window_slow = 26, window_fast = 12, window_sign = 9)
df['BB_Up'] = fi.bollinger_hband(df['Close'], window = 20, window_dev = 2)
df['BB_Down'] = fi.bollinger_lband(df['Close'], window = 20, window_dev = 2)
df['Stochastic'] = fi.stoch(df['Low'], df['High'], df['Close'], window = 14)
df['Stochastic_Signal'] = fi.stoch_signal(df['Low'], df['High'], df['Close'], window = 14)

print(df)
```

### Realtime Data

```python
import time
import pandas as pd
from FiinQuant import FiinSession, RealTimeReturnData

client = FiinSession(
    username='fiinquant.staging@fiingroup.vn',
    password='sdksoiILelrbJ909)_)aOKknn456',
)

fi = client.FiinIndicator()
df = pd.DataFrame()

def onRealtimeData(data: RealTimeReturnData):
    global df, ema_5, sma_5, rsi, macd, macd_signal, macd_diff, bb_up, bb_down, stochastic, stochastic_Signal   
    data = data.toDataFrame()
    df = pd.concat([df, data], ignore_index=True)

    ema_5 = fi.ema(df['ClosePrice'], window = 5)
    sma_5 = fi.sma(df['ClosePrice'], window = 5)
    rsi = fi.rsi(df['ClosePrice'], window = 14)
    macd = fi.macd(df['ClosePrice'], window_slow = 26, window_fast = 12)
    macd_signal = fi.macd_signal(df['ClosePrice'], window_slow = 26, window_fast = 12, window_sign = 9)
    macd_diff = fi.macd_diff(df['Close'], window_slow = 26, window_fast = 12, window_sign = 9)
    bb_up = fi.bollinger_hband(df['Close'], window = 20, window_dev = 2)
    bb_down = fi.bollinger_lband(df['Close'], window = 20, window_dev = 2)
    stochastic = fi.stoch(df['Low'], df['High'], df['Close'], window = 14)
    stochastic_Signal = fi.stoch_signal(df['Low'], df['High'], df['Close'], window = 14)

realtimedata = client.SubscribeForRealTime(ticker = 'HPG', callback = onRealtimeData)
realtimedata.start()
time.sleep(100)
realtimedata.stop()

print(df)
```