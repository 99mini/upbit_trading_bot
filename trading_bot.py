import datetime
import time
import utils
from main import *

ticker = "KRW-STRAX"

# 잔고 조회
balance = upbit.get_balance(ticker="KRW")
# balances = upbit.get_balances()

# 포지션 있으면 True
op_mode = False

# 목표 수익률 | 손절율
take_profit_rate = 3.0
loss_cut_rate = -2.0

# 분할 매도 비율
split_sell_rate = 0.8

position = {
    'time': None,
    'order_price': 0,
    'volume': 0
}

now = datetime.datetime.now()
print(now)
print("잔고: ", balance)
print("기준 봉: ", INTERVAL)
print("=" * 100)

utils.telegramMassageBot("{0}\n PROGRAM START".format(str(now)))

while True:
    try:
        # 현재 시간
        now = datetime.datetime.now()

        # 현재 가격
        cur_price = pyupbit.get_current_price(ticker=ticker)

        # 목표 가격
        target = utils.calc_target(ticker=ticker)

        # btc sma 20 이격률
        btc_sma20_sep_rate = utils.calc_btc_sma20_sep_rate()

        # rsi14
        rsi14 = utils.calc_rsi14(ticker)

        if now.second % 10 == 0:
            print(now)
            print('ticker: ', ticker,
                  "목표가: ", target,
                  "현재가: ", cur_price,
                  "btc sma 20 이격도: ", btc_sma20_sep_rate,
                  "rsi14: ", rsi14)

        # 포지션 없을 경우
        if not op_mode:

            # 목표가 갱신
            if now.minute == 0 and (10 <= now.second < 20):
                print("=" * 100)
                print("목표가 갱신")
                target = utils.calc_target(ticker)
                op_mode = True

                time.sleep(10)
                continue


            # rsi14가 70이상이면 포지션 진입 X
            if rsi14 > 70:
                pass

            # 포지션 진입
            # btc over sma20
            elif btc_sma20_sep_rate > 0.5:
                if target < cur_price:
                    volume = balance
                    utils.buy_order(ticker, price=volume)
                    position['time'] = now
                    position['order_price'] = cur_price
                    position['volume'] = volume

                    print(now)
                    print("매수 주문")
                    print("매수 수량: ", volume)
                    print("매수 금약: ", cur_price)
                    print("=" * 100)

        # 포지션이 있는 경우
        else:
            # 주문시간과 현재시간의 차이
            time_diff = now - position['time']

            # 수익률
            pnl = utils.calc_pnl(position['order_price'], cur_price)

            # btc sma20이 음전하면 reversal -> True
            reversal = btc_sma20_sep_rate < 0

            # 익절 시나리오
            # 포지션을 잡은 후 1시간 이내
            if time_diff.seconds <= 3600:
                if pnl > take_profit_rate * split_sell_rate:
                    sell_volume = position['volume'] / 5

                    utils.sell_order(ticker=ticker, volume=sell_volume)
                    position['volume'] -= sell_volume
                    split_sell_rate *= 1.1

                    print(now)
                    print("매도 주문")
                    print("매도 수량: ", sell_volume)
                    print("매도 금약: ", cur_price)
                    print("=" * 100)


            # 포지션을 잡은 후 1시간 ~ 4시간
            elif 3600 + 10 < time_diff.seconds < 3600 * 4:
                if pnl > take_profit_rate:
                    sell_volume = position['volume']
                    utils.sell_order(ticker=ticker, volume=sell_volume)

                    op_mode = False

                    print(now)
                    print("매도 주문")
                    print("매도 수량: ", sell_volume)
                    print("매도 금약: ", cur_price)
                    print("=" * 100)
            elif time_diff >= 3600 * 4:
                sell_volume = position['volume']
                utils.sell_order(ticker=ticker, volume=sell_volume)

                op_mode = False

                print(now)
                print("매도 주문")
                print("매도 수량: ", sell_volume)
                print("매도 금약: ", cur_price)
                print("=" * 100)

            # 손절 시나리오
            # 손절률 도달시 | btc sma20 하회시
            if pnl < loss_cut_rate or reversal:
                sell_volume = position['volume']
                utils.sell_order(ticker=ticker, volume=sell_volume)

                op_mode = False

                print(now)
                print("매도 주문")
                print("매도 수량: ", sell_volume)
                print("매도 금약: ", cur_price)
                print("=" * 100)

        time.sleep(1)
    except Exception as e:
        print("Trading Bot Error:", e)
