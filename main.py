import pyupbit

f = open("ym_api_key.txt")
lines = f.readlines()
ACCESS_KEY = lines[0].strip()
SECRET_KEY = lines[1].strip()
f.close()

INTERVAL = 'minutes60'

# upbit class instance
upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)



# 시장가 주문
# resp = upbit.buy_market_order(ticker="KRW-XRP",price=10000)
# pprint.pprint(resp)

# 시장가 매도
# xrp_balance = upbit.get_balance(ticker="KRW-XRP")
# upbit.sell_market_order(ticker="KRW-XRP", volume=xrp_balance)

# KRW 로 거래되는 모든 티커 리스트
# tickers = pyupbit.get_tickers(fiat="KRW")

# 캔들 정보
# df = pyupbit.get_ohlcv(ticker="KRW-BTC", interval="minute60")

# 현재가 정보
# price_dict = pyupbit.get_current_price(tickers)





# while True:
#     now = datetime.datetime.now()
#
#     price_dict = pyupbit.get_current_price(tickers)
#     price = price_dict[ticker]
#     print(now, price)
#
#     time.sleep(1)
