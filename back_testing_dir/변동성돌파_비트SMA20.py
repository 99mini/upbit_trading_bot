import os
import pprint

import numpy as np
import pandas as pd
import pyupbit
import talib as ta
import xlsxwriter

INTERVAL = "minutes60"
COUNT = 240

datas = []

# pd.set_option('display.max_columns', 500)

# btc dateFrame
df_btc = pyupbit.get_ohlcv(ticker="KRW-BTC", interval=INTERVAL, count=COUNT)

tickers = pyupbit.get_tickers(fiat="KRW")
for ticker in tickers:
    # btc sma20 rate
    df = pyupbit.get_ohlcv(ticker=ticker, interval=INTERVAL, count=COUNT)
    df['btc_sma20_rate'] = df_btc['close'] / ta.SMA(np.asarray(df_btc['close']), 20) * 100 - 100
    df['btc_sma20_rate'] = df['btc_sma20_rate'].fillna(0)

    # rsi
    df['rsi14'] = ta.RSI(np.asarray(df['close']), 14)

    # mfi
    df['mfi'] = ta.MFI(df['high'], df['low'], df['close'], df['volume'])

    # target
    noise = 0.5
    # mean of noise 14
    df['range'] = df['high'] - df['low']
    df['target'] = df['open'] + df['range'].shift(1) * noise

    df['buy'] = (df['high'] > df['target']) & (df['btc_sma20_rate'] > 0.8) & (df['rsi14'] > 70)  # rsi14 > 70 이면 거래 X
    # df['buy'] = (df['high'] > df['target']) & (df['btc_sma20_rate'] > 0.8) & (df['mfi'] > 80)  # mfi > 80 이면 거래 X

    df['pnl'] = df[df['buy']]['close'] / df[df['buy']]['target']
    df['pnl'] = df['pnl'].replace(np.nan, 1)
    df['cumulative_pnl'] = df['pnl'].cumprod()

    data = {
        'ticker': ticker,
        'trading_count': len(df[df['buy']]),
        'loss_trading_count': len(df[df['pnl'] < 1.0]),
        'MDD': round(min(df['pnl']) * 100 - 100, 4),
        'cumulative_pnl': round(df.iloc[-1]['cumulative_pnl'] * 100 - 100, 4)
    }
    datas.append(data)
    print("complete", ticker)

datas.sort(key=lambda x: -x['cumulative_pnl'])

df = pd.DataFrame(datas)
df = df[['ticker', 'trading_count', 'loss_trading_count', 'MDD', 'cumulative_pnl']]

file = 'Back_Testing.xlsx'
strategy = 'RSI'

if not os.path.isfile(file):
    df.to_excel(file, sheet_name=INTERVAL)
else:
    with pd.ExcelWriter(file, mode="a", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name='{0} {1}'.format(INTERVAL, strategy))
print(df)
