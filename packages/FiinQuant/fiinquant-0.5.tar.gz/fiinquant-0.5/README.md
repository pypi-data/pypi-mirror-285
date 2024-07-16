# quant_indicators

Python package for financial technical indicators.

## Installation

You can install the package via pip:

```python
pip install FiinQuant
```

## Usage

### Historical Data

```python
from FiinQuant import FiinSession

client = FiinSession(
    username='fiinquant.staging@fiingroup.vn',
    password='sdksoiILelrbJ909)_)aOKknn456',
)

df = client.FiinDataHistorical(
    ticker="HPG", 
    from_date='2024-06-09 09:15', 
    to_date='2024-07-15 14:29', 
    multiplier=1, 
    timespan='minute',  
    limit=10000).toDataFrame()

fi = client.FiinIndicator()
df['EMA_5'] = fi.ema(df['Close'], window=5)
df['SMA_10'] = fi.sma(df['Close'], window=10)
df['RSI'] = fi.rsi(df['Close'], window=7)
df['MACD'] = fi.macd(df['Close'], window_slow=10, window_fast=7)
df['MACD_Signal'] = fi.macd_signal(df['Close'], window_slow=10, window_fast=7, window_sign=3)
df['BB_Up'] = fi.bollinger_hband(df['Close'], window=10, window_dev=2)
df['BB_Down'] = fi.bollinger_lband(df['Close'], window=10, window_dev=2)
df['Stochastic'] = fi.stoch(df['Low'], df['High'], df['Close'], window=10)
df['Stochastic_Signal'] = fi.stoch(df['Low'], df['High'], df['Close'], window=10)
print(df)
```

### Realtime Data

```python
import time
from FiinQuant import FiinSession
import pandas as pd

client = FiinSession(
    username='fiinquant.staging@fiingroup.vn',
    password='sdksoiILelrbJ909)_)aOKknn456',
)

df = pd.DataFrame()

def onRealtimeData(data):
    global df, ema, sma, macd
    df = pd.concat([df, data],ignore_index=True)

    fi = client.FiinIndicator()
    ema = fi.ema(df['ClosePrice'], window=5)
    sma = fi.sma(df['ClosePrice'], window=10)
    macd = fi.macd(df['ClosePrice'])

realtimedata = client.SubscribeForRealTime('HPG',callback = onRealtimeData)
realtimedata.start()
time.sleep(10)
realtimedata.stop()
```