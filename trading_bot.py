import datetime
import math
import time

import utils
from config import *


def exec_volatility(ticker):
    # 잔고 조회
    balance = upbit.get_balance(ticker="KRW")
    # balances = upbit.get_balances()

    # True -> 신규 포지션 진입 가능
    op_mode = False

    # 목표 수익률 | 손절율
    take_profit_rate = 3.0
    loss_cut_rate = -2.0

    # 분할 매도 비율
    split_sell_rate = 0.8

    position = {
        'type': None,
        'time': None,
        'order_price': 0,
        'volume': 0
    }

    try:
        # 현재 시간
        now = datetime.datetime.now()

        # 현재 가격
        cur_price = pyupbit.get_current_price(ticker=ticker)

        # 목표 가격
        # TODO 매 호출마다 목표 가격 정하지 않고 데이터베이스에 저장
        target = utils.calc_target(ticker=ticker)

        # btc sma 20 이격률
        btc_sma20_sep_rate = utils.calc_btc_sma20_sep_rate()

        # rsi14
        rsi14 = utils.calc_rsi14(ticker)


        print(now)
        if position['type'] is None:
            print(
                'ticker:', ticker,
                "목표가:", target,
                "현재가:", cur_price, '\n'
                                   "btc sma 20 이격도:", btc_sma20_sep_rate,
                "rsi14:", rsi14,
                "op_mode:", op_mode
            )
        else:
            print(
                "진입시간:", position['time'],
                "주문가:", position["order_price"],
                "주문수량:", position['volume'],
                "현재가:", cur_price, '\n'
                                   "수익률:", utils.calc_pnl(position["order_price"], cur_price),
                "BTC 20일선 이격률:", btc_sma20_sep_rate,
                "op_mode:", op_mode
            )
        print("#"*100)

        # 목표가 갱신
        # TODO 캔들 interval 기준으로 목표가 갱신 후 목표가 데이터베이스에 저장
        if position['type'] is None and now.minute == 0 and (10 <= now.second < 20):
            print("=" * 100)
            print("목표가 갱신")
            target = utils.calc_target(ticker)
            op_mode = True

            time.sleep(10)
        # 포지션 없을 경우
        if op_mode and position['type'] is None:
            # rsi14가 70이상이면 포지션 진입 X
            if rsi14 > 70:
                print("rsi14 > 70: overbuying...!")

            # 포지션 진입
            # btc over sma20
            elif btc_sma20_sep_rate > 0.5:
                if target < cur_price:
                    price = 15_000
                    volume, order_price, position_type = utils.buy_order(ticker=ticker, price=price)
                    position['type'] = position_type
                    position['time'] = now
                    position['order_price'] = order_price
                    position['volume'] = volume

                    print(now)
                    print("매수 주문")
                    print("매수 수량: ", volume)
                    print("매수 금액: ", order_price)
                    print("=" * 100)

                    # telegram send
                    msg = "매수주문\n매수수량: {0}\n매수 평단가: {1}".format(volume, order_price)
                    utils.telegramMassageBot(msg)

        # 포지션이 있는 경우
        if op_mode and position['type'] is not None:
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
                    sell_volume = math.trunc(position['volume'] / 5)

                    # 주문금액이 5,000원 이하일 경우 전량 매도
                    if sell_volume * cur_price <= 5000:
                        sell_volume = position['volume']

                    utils.sell_order(ticker=ticker, volume=sell_volume)
                    position['volume'] -= sell_volume

                    # 남은 개수가 없으면 포지션 없음
                    if position['volume'] == 0:
                        position['type'] = None
                        op_mode = False

                    split_sell_rate *= 1.1

                    print(now)
                    print("매도 주문")
                    print("매도 수량: ", sell_volume)
                    print("매도 금액: ", cur_price)
                    print("=" * 100)

                    # 텔레그램 알림
                    utils.telegramMassageBot("매도주문\n매도수량: {0}\n매도금액: {1}".format(sell_volume, cur_price))

            # 포지션을 잡은 후 1시간 ~ 4시간
            elif 3600 + 10 < time_diff.seconds < 3600 * 4:
                if pnl > take_profit_rate:
                    sell_volume = position['volume']
                    utils.sell_order(ticker=ticker, volume=sell_volume)

                    position['type'] = None
                    op_mode = False

                    print(now)
                    print("매도 주문")
                    print("매도 수량: ", sell_volume)
                    print("매도 금액: ", cur_price)
                    print("=" * 100)

                    # 텔레그램 알림
                    utils.telegramMassageBot("매도주문\n매도수량: {0}\n매도금액: {1}".format(sell_volume, cur_price))

            elif time_diff >= 3600 * 4:
                sell_volume = position['volume']
                utils.sell_order(ticker=ticker, volume=sell_volume)

                position['type'] = None
                op_mode = False

                print(now)
                print("매도 주문")
                print("매도 수량: ", sell_volume)
                print("매도 금액: ", cur_price)
                print("=" * 100)

                # 텔레그램 알림
                utils.telegramMassageBot("매도주문\n매도수량: {0}\n매도금액: {1}".format(sell_volume, cur_price))

            # 손절 시나리오
            # 손절률 도달시 | btc sma20 하회시
            if pnl < loss_cut_rate or reversal:
                sell_volume = position['volume']
                utils.sell_order(ticker=ticker, volume=sell_volume)

                position['type'] = None
                op_mode = False

                print(now)
                print("매도 주문")
                print("매도 수량: ", sell_volume)
                print("매도 금액: ", cur_price)
                print("=" * 100)

                # 텔레그램 알림
                utils.telegramMassageBot("매도주문\n매도수량: {0}\n매도금액: {1}".format(sell_volume, cur_price))

        time.sleep(1)
    except Exception as e:
        print("Volatility Trading Bot Error:", e)
