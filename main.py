import datetime

import trading_bot
import utils
from config import INTERVAL

trading_coin_list = utils.select_top_trade_price_coins()
utils.telegramMassageBot("{0}\n PROGRAM START".format(str(datetime.datetime.now())))
now = datetime.datetime.now()

print(now)
print("기준 봉:", INTERVAL)
print("=" * 100)

while True:
    for ticker in trading_coin_list:
        trading_bot.exec_volatility(ticker)
