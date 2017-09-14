#!/usr/bin/python
# -*- coding: UTF-8 -*-

# import sys
# sys.path.append('/root/workspace/python/quant')

from config import settings

from util import timestamp

from common import constant, util

import time
from decimal import Decimal

from liqui.client import PrivateClient as LqClient
from bitfinex.client import PrivateClient as BfxClient

from bunch import Bunch

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
lqClient = LqClient(settings.LIQUI_API_KEY, settings.LIQUI_API_SECRET)

# SYMBOL_BFX = u'ltcbtc'
# SYMBOL_OK = u'ltc_btc'
# SYMBOL_LTC = u'ltc'

# PAIR_ETH = True 表示eth交易对，目前支持omg和eos
PAIR_ETH = False
CURRENCY = 'eos'
# 差价百分比触发为0.7%
DIFF_TRIGGER = Decimal('0.7')

FEE_BFX = Decimal('0.2')
FEE_LQ = Decimal('0')

INTERVAL = 0.5
TICK_INTERVAL = 1

# 取深度里的第几条数据, 总公5条
DEPTH_INDEX_LQ = 0
DEPTH_INDEX_BFX = 1

MAX_DELAY = Decimal('3000')


# 单次交易最小的btc量，计算是amount * price
PRICE_MIN = Decimal('0.0001')

# ltc单次交易数量 ,  eos 设置成1, eth 设置成0.1
AMOUNT_ONCE = Decimal('1')

# ltc单次交易的最小数量, 平台限制,lqcoin计算每次的total, bfx为0.01, 所以okex这里也设置为0.1
AMOUNT_MIN = Decimal('0.1')

# max_amount的几分之一
AMOUNT_RATE = Decimal('2')

# 账户内保留的stock数，这里指的是lq的btc量
AMOUNT_RETAIN = Decimal('0.001')

# ltc交易滑价，暂时不用
SLIDE_PRICE = Decimal('0')

D_FORMAT = Decimal('0.00000000')
FORMAT_FOUR = Decimal('0.0000')
FORMAT_FIVE = Decimal('0.0000')

interrupt = False


# def cancel_all_orders() {
#     for (var i = 0; i < exchanges.length; i++) {
#         while (true) {
#             var orders = null;
#             while (!(orders = exchanges[i].GetOrders())) {
#                 Sleep(Interval);
#             }
#
#             if (orders.length == 0) {
#                 break;
#             }
#
#             for (var j = 0; j < orders.length; j++) {
#                 exchanges[i].CancelOrder(orders[j].Id, orders[j]);
#             }
#         }
#     }
# }

def init():
    pass


def get_max_amount(list_tmp, index):
    amount = Decimal('0')
    for i in range(5):
        item = list_tmp[i]
        if i == index:
            amount = amount + item.amount
    return amount


def get_symbol(ex_name, currency):
    if PAIR_ETH is True:
        return util.get_symbol_eth(ex_name, currency)
    else:
        return util.get_symbol_btc(ex_name, currency)


def update_state(state):
    start = Decimal(timestamp.get_current_time())
    depth_bfx = bfxClient.depth(get_symbol(constant.EX_BFX, CURRENCY))
    if depth_bfx is None:
        state.exception = 'bitfinex深度信息获取失败'
        return
    end = Decimal(timestamp.get_current_time())
    delay_bfx = end - start
    state.bfx.depth = depth_bfx

    start = Decimal(timestamp.get_current_time())
    depth_lq = lqClient.depth(get_symbol(constant.EX_LQ, CURRENCY))
    if depth_lq is None:
        state.exception = 'liqui深度信息获取失败'
        return
    end = Decimal(timestamp.get_current_time())
    delay_lq = end - start
    state.lq.depth = depth_lq

    delay = max(delay_lq, delay_bfx)
    state.delay = delay

    # make ticker dict
    price_sel_bfx = depth_bfx.asks[DEPTH_INDEX_BFX].price
    price_buy_bfx = depth_bfx.bids[DEPTH_INDEX_BFX].price
    amount_sell_bfx = get_max_amount(depth_bfx.asks, DEPTH_INDEX_BFX)
    amount_buy_bfx = get_max_amount(depth_bfx.bids, DEPTH_INDEX_BFX)

    state.bfx.ticker = Bunch({
        'buy': Bunch({
            'price': price_buy_bfx,
            'max_amount': amount_buy_bfx
        }),
        'sell': Bunch({
            'price': price_sel_bfx,
            'max_amount': amount_sell_bfx
        })
    })

    # lq make ticker dict
    price_sell_lq = depth_lq.asks[DEPTH_INDEX_LQ].price
    price_buy_lq = depth_lq.bids[DEPTH_INDEX_LQ].price
    amount_sell_lq = get_max_amount(depth_lq.asks, DEPTH_INDEX_LQ)
    amount_buy_lq = get_max_amount(depth_lq.bids, DEPTH_INDEX_LQ)

    state.lq.ticker = Bunch({
        'buy': Bunch({
            'price': price_buy_lq,
            'max_amount': amount_buy_lq
        }),
        'sell': Bunch({
            'price': price_sell_lq,
            'max_amount': amount_sell_lq
        })
    })

    # bfx卖 lq买，所以bfx-lq
    if state.lq.is_maker:
        state.diff = price_buy_bfx - price_buy_lq
        state.diff_percent = (state.diff / price_buy_lq * Decimal('100')).quantize(D_FORMAT)
    else:
        state.diff = price_buy_bfx - price_sell_lq
        state.diff_percent = (state.diff / price_sell_lq * Decimal('100')).quantize(D_FORMAT)


def get_state():
    while True:
        account_bfx = bfxClient.balance()
        if account_bfx is None:
            time.sleep(INTERVAL)
            continue
        break

    while True:
        account_lq = lqClient.balance()
        if account_lq is None:
            time.sleep(INTERVAL)
            continue
        break

    bfx_dict = Bunch()
    bfx_dict.account = account_bfx
    bfx_dict.fee = FEE_BFX
    bfx_dict.is_maker = False

    lq_dict = Bunch()
    lq_dict.account = account_lq
    lq_dict.fee = FEE_LQ
    lq_dict.is_maker = False

    state = Bunch({
        'bfx': bfx_dict,
        'lq': lq_dict
    })
    return state


def get_deal_amount(ex_name, order_id):
    """
    获取订单的成交量
    :param ex_name: lq or bitfinex
    :param order_id: order id
    :return: deal amount , type is Decimal
    """
    if ex_name == constant.EX_LQ:
        while True:
            order_r = lqClient.get_order(order_id)
            if order_r is None:
                continue
            break
    else:
        while True:
            order_r = bfxClient.get_order(order_id)
            if order_r is None:
                continue
            break

    if order_r.is_pending():
        logger.debug("订单%s未完成,  已完成%s, 初始%s" % (order_r.order_id, order_r.deal_amount, order_r.amount))
        if ex_name == constant.EX_LQ:
            lqClient.cancel_order(order_id)
        else:
            bfxClient.cancel_order(order_id)
        time.sleep(TICK_INTERVAL)
        return get_deal_amount(ex_name, order_id)
    else:
        if order_r.is_canceled():
            logger.debug("订单%s已取消,  已完成%s, 初始%s" % (order_r.order_id, order_r.deal_amount, order_r.amount))
        if order_r.is_closed():
            logger.debug("订单%s已完成,  已完成%s, 初始%s" % (order_r.order_id, order_r.deal_amount, order_r.amount))
        return order_r.deal_amount


def get_bfx_ticker():
    while True:
        ticker = bfxClient.ticker(get_symbol(constant.EX_BFX, CURRENCY))
        if ticker is None:
            continue
        break
    return ticker


def on_action_trade(state):
    """
    liqui流程如下
        1,判断是否满足买的条件，btc余额
        2,委托买单
        3,超时或者部分成交则取消买单
    条件因素:
        1,手续费
        2,是否走maker
        3,total计算并判断, liqui最低btc total限度为0.0001
    """

    btc_lq = None
    for i in state.lq.account:
        if i.currency == u'btc':
            btc_lq = i

    if btc_lq is None:
        raise ValueError('lq account not exist btc')

    balance_btc_lq = Decimal(repr(btc_lq.balance))
    if state.lq.is_maker:
        max_amount_lq = state.lq.ticker.buy.max_amount
        buy_price_lq = state.lq.ticker.buy.price
    else:
        max_amount_lq = state.lq.ticker.sell.max_amount
        buy_price_lq = state.lq.ticker.sell.price

    buy_price_real = buy_price_lq + SLIDE_PRICE
    buy_price_and_fee = buy_price_real * (state.lq.fee / Decimal('100') + Decimal('1'))
    can_buy = (balance_btc_lq - AMOUNT_RETAIN) / buy_price_and_fee
    buy_order_amount = min(max_amount_lq, can_buy)
    buy_order_price_total = (buy_order_amount * buy_price_and_fee).quantize(FORMAT_FIVE)

    # dd = {
    #     'balance_btc_lq:': balance_btc_lq,
    #     'max_amount_lq:': max_amount_lq,
    #     'buy_price_and_fee:': buy_price_and_fee,
    #     'can_buy:': can_buy,
    #     'buy_order_amount:': buy_order_amount
    # }
    # logger.debug(str(dd))
    balance_enough_lq = (buy_order_amount >= AMOUNT_ONCE) and (buy_order_amount >= AMOUNT_MIN)
    total_enough_lq = buy_order_price_total > PRICE_MIN
    if balance_enough_lq and total_enough_lq:
        state.lq.can_buy = buy_order_amount
    else:
        state.lq.can_buy = Decimal('0')

    # 判断bfx margin账户的余额是否足够，这里不做判断，bfx放很多余额，所以一定够？ 这个逻辑可能不对，先这样
    # bfx始终走taker, 所以取buy属性
    # 计算出bfx最大能卖的ltc数量

    """
    1,计算出bfx最大能卖的ltc数量?margin账户的余额是否足够，这里不做判断，bfx放很多余额，所以一定够？ 这个逻辑可能不对，先这样
    2,bfx始终走taker, 所以取buy属性
    """
    max_amount_bfx = state.bfx.ticker.buy.max_amount
    sell_order_amount = max_amount_bfx / AMOUNT_RATE
    balance_enough_bfx = (sell_order_amount >= AMOUNT_MIN) and (buy_order_amount >= AMOUNT_ONCE)
    if balance_enough_bfx:
        state.bfx.can_sell = sell_order_amount
    else:
        state.bfx.can_sell = 0

    if state.lq.can_buy <= 0:
        logger.info('差价满足但是lq的btc数量或不足，或者当前深度不满足AmountOnce要求')
        return
    if state.bfx.can_sell <= 0:
        logger.info('差价满足但是bfx margin账户余额不足')
        return

    """
    这里是先在lq买进现货，然后在bfx开同等数量的空单
    计算买卖交易的最大amount
    """
    buy_amount = min(AMOUNT_ONCE, state.lq.can_buy, state.bfx.can_sell)
    buy_amount_real = buy_amount * (state.lq.fee / Decimal('100') + Decimal('1'))
    buy_amount_real = buy_amount_real.quantize(FORMAT_FOUR)
    # lq下买单
    logger.info("lq 委买单======>  price: " + str(buy_price_real) + "   amount: " + str(buy_amount_real) +
                "   diff" + str(state.diff))
    buy_order_result = lqClient.buy(get_symbol(constant.EX_LQ, CURRENCY), buy_price_real, buy_amount_real)
    if buy_order_result is None:
        logger.info('lq 委买单失败, 直接return')
        return
    if buy_order_result.error is not None:
        logger.info("lq 委买单失败, %s" % str(buy_order_result.error))
        return

    logger.info("lq 委买单成功, 订单id %s" % str(buy_order_result.order_id))
    time.sleep(TICK_INTERVAL)
    buy_deal_amount = get_deal_amount(constant.EX_LQ, buy_order_result.order_id)
    logger.info("lq买单的成交量: " + str(buy_deal_amount) + "  order_id: " + str(buy_order_result.order_id))
    if buy_deal_amount < AMOUNT_MIN:
        logger.info('lq买单成交量小于AMOUNT_MIN, 直接return')
        return

    # bfx期货准备开空单, 数量和lq买单成交的量相同
    sell_amount = buy_deal_amount
    sell_price = state.lq.ticker.buy.price - SLIDE_PRICE
    while True:
        logger.info("bfx 开空单======>  price: " + str(sell_price) + "   amount: " + str(sell_amount) +
                    "   diff" + str(state.diff))
        sell_order_result = bfxClient.margin_sell(get_symbol(constant.EX_BFX, CURRENCY), sell_amount, sell_price)
        if sell_order_result.error is None:
            time.sleep(TICK_INTERVAL)
            sell_deal_amount = get_deal_amount(constant.EX_BFX, sell_order_result.order_id)
            logger.info("bfx卖单的成交量: " + str(sell_deal_amount) + "  order_id: " + str(sell_order_result.order_id))
            diff_amount = sell_amount - sell_deal_amount
            if diff_amount < AMOUNT_MIN:
                logger.info('交易循环完成')
                global interrupt
                interrupt = True
                break
            sell_amount = diff_amount

        """
        更新bfx 的价格，以最新的ticker来开空单，此过程大概率亏损
        """
        time.sleep(TICK_INTERVAL)
        bfx_ticker = get_bfx_ticker()
        sell_price = bfx_ticker.buy - SLIDE_PRICE


def on_action_ticker(state):
    if state.diff_percent >= DIFF_TRIGGER:
        if state.delay > MAX_DELAY:
            # 延迟超过2秒，放弃这次机会
            return
        logger.debug('差价触发,准备交易========>diff_percent: ' + str(state.diff_percent))
        on_action_trade(state)


def on_tick():
    state = get_state()
    update_state(state)
    if 'exception' in state.keys() and state.exception is not None:
        logger.debug(str(state.exception))
        return
    logger.debug("当前价差========>{buy: " + str(state.lq.ticker.sell.price) +
                 ", sell: " + str(state.bfx.ticker.buy.price) +
                 ", diff_percent: " + str(state.diff_percent) +
                 "}")

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