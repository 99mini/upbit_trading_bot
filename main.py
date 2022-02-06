import datetime

import db_helper
import trading_bot
import utils
from config import INTERVAL


trading_coin_list = utils.select_top_trade_price_coins(count=20)
utils.telegramMassageBot("{0}\n PROGRAM START".format(str(datetime.datetime.now())))
now = datetime.datetime.now()

print(now)
print("기준 봉:", INTERVAL)
print("=" * 100)

# init target price setting
for ticker in trading_coin_list:
    target = utils.calc_target(ticker)

    # insert db
    data = (ticker, target, 0)
    db_helper.insert_target_db(data=data)

while True:
    for ticker in trading_coin_list:
        trading_bot.exec_volatility(ticker)
