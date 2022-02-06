import json
import time

import numpy as np
import requests
import talib as ta

import config
from config import *


# 목표가 계산
def calc_target(ticker):
    df = pyupbit.get_ohlcv(ticker, interval=INTERVAL)
    previous_data = df.iloc[-2]
    now_data = df.iloc[-1]

    noise = calc_noise_rate(14, df)
    previous_range = previous_data['high'] - previous_data['low']
    target = now_data['open'] + previous_range * noise
    return target


# noise ratio 계산
def calc_noise_rate(period, df):
    # 노이즈 = 1 - 절댓값(시가-종가)  / (고가-저가)
    # noise = 1 - abs(previous_data['open'] - previous_data['close']) / (previous_data['high'] - previous_data['low'])
    sum_noise = 0
    for i in range(2, period + 2):
        tmp_data = df.iloc[-i]
        sum_noise += 1 - abs(tmp_data['open'] - tmp_data['close']) / (tmp_data['high'] - tmp_data['low'])
    noise_ratio = round(sum_noise / period, 4)
    return noise_ratio


# fee 계산
def calc_fee(price):
    # 거래 수수료율
    # 가격 x 수수료
    fee_rate = 0.05
    fee = price * fee_rate
    return fee


# 비트코인 20일선 이격률 계산
def calc_btc_sma20_sep_rate():
    try:
        df_btc = pyupbit.get_ohlcv('KRW-BTC', interval=INTERVAL, count=20)
        sma20 = df_btc["close"].rolling(20).mean()
        cur_price = pyupbit.get_current_price('KRW-BTC')
        return round((cur_price / sma20.iloc[-1]) * 100 - 100, 3)
    except Exception as e:
        print("calc_btc_sma20_sep_rate", e)
        # telegramMassageBot("calc_btc_sma20_sep_rate" + str(e))


# rsi 계산기
def calc_rsi14(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker, interval=INTERVAL, count=15)
        rsi14 = ta.RSI(np.asarray(df['close']), 14)
        return rsi14[-1]
    except Exception as e:
        print("calc_rsi", e)


# pnl 계산
def calc_pnl(order_price, cur_price):
    return round((cur_price / order_price) * 100 - 100, 4)


# 매수 주문
def buy_order(ticker, price):
    try:
        volume = 0
        buy_price = 0
        position_type = None

        resp = upbit.buy_market_order(ticker=ticker, price=price)
        time.sleep(1)
        order = upbit.get_order(resp['uuid'])

        if order is not None and len(order['trades']) > 0:
            volume = upbit.get_balance(ticker)
            buy_price = upbit.get_avg_buy_price(ticker)
            position_type = 'buy'

        return volume, buy_price, position_type
    except Exception as e:
        print("buy_order", e)


# 매도 주문
def sell_order(ticker, volume):
    try:
        resp = upbit.sell_market_order(ticker=ticker, volume=volume)
        time.sleep(1)
        order = upbit.get_order(resp['uuid'])

        if order is not None and len(order['trades']) > 0:
            pass
    except Exception as e:
        print("sell_order", e)


# 텔레그램 메세지 보내기
def telegramMassageBot(msg):
    params = {'chat_id': telebotid, 'text': msg}
    # 텔레그램으로 메시지 전송
    try:
        requests.get(teleurl, params=params)
    except Exception as e:
        print('telegram error: ', e)


# 거래대금 상위 코인 고르기
def select_top_trade_price_coins():
    try:
        URL = config.all_ticker_url

        ticker_volume_dict = []

        tickers = pyupbit.get_tickers(fiat="KRW")
        symbols = ''
        for ticker in tickers:
            symbols += ticker + ","
        symbols = symbols[:-1]

        params = {'markets': symbols}
        res = requests.get(URL, params=params)
        datas = json.loads(res.text)
        for data in datas:
            ticker_volume_dict.append(
                {
                    'ticker': data["market"],
                    'price24': data["acc_trade_price_24h"]
                }
            )

        ticker_volume_dict.sort(key=lambda x: -x['price24'])
        top_tickers = ticker_volume_dict[:10]
        top_tickers = [x['ticker'] for x in top_tickers]
        return top_tickers
    except Exception as e:
        print("select top trade price coins: ", e)
