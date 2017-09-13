#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from decimal import Decimal

from okex.client import PrivateClient as OkClient
from bitfinex.client import PrivateClient as BfxClient

from config import settings

from util import timestamp

from common import constant

import logging

logger = logging.getLogger('wsl')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logging.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

bfxClient = BfxClient(settings.BFX_API_KEY, settings.BFX_API_SECRET)
okClient = OkClient(settings.OKEX_API_KEY, settings.OKEX_API_SECRET)

SYMBOL_BFX = u'ltcbtc'
SYMBOL_OK = u'ltc_btc'
SYMBOL_LTC = u'ltc'

FEE_BFX = Decimal(0.2)
FEE_OK = Decimal(0)

INTERVAL = 0.5
TICK_INTERVAL = 1

# 取深度里的第几条数据, 总公5条
DEPTH_INDEX_OK = 1
DEPTH_INDEX_BFX = 1

MAX_DELAY = Decimal(2000)

DIFF_TRIGGER = Decimal(0.0001)

# ltc单次交易数量
AMOUNT_ONCE = Decimal(0.1)

# ltc单次交易的最小数量, 平台限制,okcoin为0.1, bfx为0.01, 所以okex这里也设置为0.1
AMOUNT_MIN = Decimal(0.1)

# max_amount的几分之一
AMOUNT_RATE = Decimal(2)

# 账户内保留的stock数，这里指的是ok的btc量
AMOUNT_RETAIN = Decimal(0.001)

# ltc交易滑价，暂时不用
SLIDE_PRICE = Decimal(0)

interrupt = False


def init():
    pass


def get_max_amount(list_tmp, index):
    amount = Decimal(0)
    for i in range(index):
        item = list_tmp[i]
        amount = amount + item[u'amount']
    return amount


def update_state(state):
    start = Decimal(timestamp.get_current_time())
    depth_bfx = bfxClient.depth(SYMBOL_BFX)
    if depth_bfx is None:
        state[u'exception'] = 'bitfinex深度信息获取失败'
        return
    end = Decimal(timestamp.get_current_time())
    delay_bfx = end - start
    state[u'bfx'][u'depth'] = depth_bfx

    start = Decimal(timestamp.get_current_time())
    depth_ok = okClient.depth(SYMBOL_OK)
    if depth_ok is None:
        state[u'exception'] = 'okex深度信息获取失败'
        return
    end = Decimal(timestamp.get_current_time())
    delay_ok = end - start
    state[u'ok'][u'depth'] = depth_ok

    delay = max(delay_ok, delay_bfx)
    state[u'delay'] = delay

    # make ticker dict
    sell_price_bfx = depth_bfx[u'asks'][DEPTH_INDEX_BFX][u'price']
    sell_amount_bfx = get_max_amount(depth_bfx[u'asks'], DEPTH_INDEX_BFX)
    buy_price_bfx = depth_bfx[u'bids'][DEPTH_INDEX_BFX][u'price']
    buy_amount_bfx = get_max_amount(depth_bfx[u'bids'], DEPTH_INDEX_BFX)
    ticker_bfx = {
        u'buy': {
            u'price': buy_price_bfx,
            u'max_amount': buy_amount_bfx
        },
        u'sell': {
            u'price': sell_price_bfx,
            u'max_amount': sell_amount_bfx
        }
    }
    state[u'bfx'][u'ticker'] = ticker_bfx

    # make ticker dict

    sell_price_ok = depth_ok[u'asks'][DEPTH_INDEX_OK][u'price']
    sell_amount_ok = get_max_amount(depth_ok[u'asks'], DEPTH_INDEX_OK)
    buy_price_ok = depth_ok[u'bids'][DEPTH_INDEX_OK][u'price']
    buy_amount_ok = get_max_amount(depth_ok[u'bids'], DEPTH_INDEX_OK)

    ticker_ok = {
        u'buy': {
            u'price': buy_price_ok,
            u'max_amount': buy_amount_ok
        },
        u'sell': {
            u'price': sell_price_ok,
            u'max_amount': sell_amount_ok
        }
    }

    state[u'ok'][u'ticker'] = ticker_ok
    # bfx卖 ok买，所以bfx-ok
    is_maker = state[u'ok'][u'use_maker']
    state[u'diff'] = buy_price_bfx - sell_price_ok
    if is_maker:
        state[u'diff'] = buy_price_bfx - buy_price_ok


def get_state():
    while True:
        account_bfx = bfxClient.balance()
        if account_bfx is None:
            time.sleep(INTERVAL)
            continue
        break

    while True:
        account_ok = okClient.balance()
        if account_bfx is None:
            time.sleep(INTERVAL)
            continue
        break

    bfx_dict = {
        u'account': account_bfx,
        u'fee': FEE_BFX,
        u'use_maker': False
    }
    ok_dict = {
        u'account': account_ok,
        u'fee': FEE_OK,
        u'use_maker': True
    }

    return {
        u'bfx': bfx_dict,
        u'ok': ok_dict,
    }


def get_deal_amount(is_ok, order_id):
    """
    获取订单的成交量
    :param is_ok: ok or bfx
    :param order_id: order id
    :return: deal amount , type is Decimal
    """
    if is_ok:
        while True:
            order_dict = okClient.get_order(SYMBOL_OK, order_id)
            if order_dict is None:
                continue
            break
    else:
        while True:
            order_dict = bfxClient.get_order(order_id)
            if order_dict is None:
                continue
            break

    if order_dict[u'status'] == constant.ORDER_STATE_PENDING:
        # cancel order then check again
        if is_ok:
            okClient.cancel_order(SYMBOL_OK, order_id)
        else:
            bfxClient.cancel_order(order_id)
        time.sleep(TICK_INTERVAL)
        return get_deal_amount(is_ok, order_id)
    return order_dict[u'deal_amount']


def get_bfx_ticker():
    while True:
        ticker = bfxClient.ticker(SYMBOL_BFX)
        if ticker is None:
            continue
        break
    return ticker


def on_action_trade(state):
    # 判断ok btc的量是否足够来买
    # Ok 买，取卖价
    # 考虑手续费
    # Ok 可能会走maker, is_maker
    # 计算出ok最大能买的ltc数量
    stocks_btc_ok = state[u'ok'][u'account'][u'stocks']
    is_maker = state[u'ok'][u'use_maker']
    buy_attr_ok = u'buy' if is_maker else u'sell'
    max_amount_ok = state[u'ok'][u'ticker'][buy_attr_ok][u'max_amount']
    taker_fee_ok = state[u'ok'][u'fee']
    buy_price_real = state[u'ok'][u'ticker'][buy_attr_ok][u'price'] + SLIDE_PRICE
    buy_price_and_fee = buy_price_real * (taker_fee_ok / 100 + 1)
    can_buy = (stocks_btc_ok - AMOUNT_RETAIN) / buy_price_and_fee
    buy_order_amount = min(max_amount_ok, can_buy)
    stocks_enough_ok = (buy_order_amount >= AMOUNT_ONCE) and (buy_order_amount >= AMOUNT_MIN)
    if stocks_enough_ok:
        state[u'ok'][u'can_buy'] = buy_order_amount
    else:
        state[u'ok'][u'can_buy'] = Decimal(0)

    # 判断bfx margin账户的余额是否足够，这里不做判断，bfx放很多余额，所以一定够？ 这个逻辑可能不对，先这样
    # bfx始终走taker, 所以取buy属性
    # 计算出bfx最大能卖的ltc数量

    max_amount_bfx = state[u'bfx'][u'ticker'][u'buy'][u'max_amount']
    sell_order_amount = max_amount_bfx / AMOUNT_RATE
    stocks_enough_bfx = (sell_order_amount >= AMOUNT_MIN) and (buy_order_amount >= AMOUNT_ONCE)
    if stocks_enough_bfx:
        state[u'bfx'][u'can_sell'] = sell_order_amount
    else:
        state[u'bfx'][u'can_sell'] = 0

    if state[u'ok'][u'can_buy'] <= 0:
        logger.info('差价满足但是ok的btc数量或不足，或者当前深度不满足AmountOnce要求')
        return
    if state[u'bfx'][u'can_sell'] <= 0:
        logger.info('差价满足但是bfx margin账户余额不足')
        return
    # 这里是先在ok买进现货，然后在bfx开同等数量的空单
    # 计算买卖交易的最大amount
    buy_amount = min(AMOUNT_ONCE, state[u'ok'][u'can_buy'], state[u'bfx'][u'can_sell'])
    buy_amount_real = buy_amount * (state[u'ok'][u'fee'] / Decimal('100') + Decimal('1'))
    # ok下买单
    logger.info("ok 委买单======>  price: " + str(buy_price_real) + "   amount: " + str(buy_amount_real) +
                "   diff" + str(state[u'diff']))
    buy_order_id = okClient.buy(SYMBOL_OK, buy_price_real, buy_amount_real)
    if buy_order_id is None:
        logger.info('ok 委买单失败, 直接return')
        return
    time.sleep(TICK_INTERVAL)
    buy_deal_amount = get_deal_amount(True, buy_order_id)
    logger.info("ok买单的成交量: " + str(buy_deal_amount) + "  order_id: " + str(buy_order_id))
    if buy_deal_amount < AMOUNT_MIN:
        logger.info('ok买单成交量小于AMOUNT_MIN, 直接return')
        return

    # bfx期货准备开空单, 数量和ok买单成交的量相同
    sell_amount = buy_deal_amount
    sell_price = state[u'ok'][u'ticker'][u'buy'][u'price'] - SLIDE_PRICE
    while True:
        logger.info("bfx 开空单======>  price: " + str(sell_price) + "   amount: " + str(sell_amount) +
                    "   diff" + str(state[u'diff']))
        sell_order_id = bfxClient.margin_sell(SYMBOL_BFX, sell_amount, sell_price)
        time.sleep(TICK_INTERVAL)
        sell_deal_amount = get_deal_amount(False, sell_order_id)
        logger.info("bfx卖单的成交量: " + str(sell_deal_amount) + "  order_id: " + str(sell_order_id))
        diff_amount = sell_amount - sell_deal_amount
        if diff_amount < AMOUNT_MIN:
            logger.info('交易循环完成')
            global interrupt
            interrupt = True
            break
        sell_amount = diff_amount
        time.sleep(TICK_INTERVAL)
        # 更新bfx 的价格，以最新的ticker来开空单，此过程大概率亏损
        bfx_ticker = get_bfx_ticker()
        sell_price = bfx_ticker[u'buy'] - SLIDE_PRICE


def on_action_ticker(state):
    if state[u'diff'] >= DIFF_TRIGGER:
        logger.debug('差价触发,准备交易========>diff: ' + str(state[u'diff']))
        if state[u'delay'] > MAX_DELAY:
            # 延迟超过2秒，放弃这次机会
            return
        on_action_trade(state)


def on_tick():
    state = get_state()
    update_state(state)
    if u'exception' in state.keys() and state[u'exception'] is not None:
        logger.debug(str(state[u'exception']))
        return
    logger.debug(str(state[u'diff']))

    on_action_ticker(state)


def main():
    init()
    while True:
        if interrupt:
            break
        time.sleep(TICK_INTERVAL)
        on_tick()


if __name__ == '__main__':
    main()
