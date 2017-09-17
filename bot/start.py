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

"""
是否使用eth交易对， 未调试过, 不要轻易使用
"""
PAIR_ETH = False
CURRENCY = 'eth'
"""差价触发百分比，不能低于0.7"""
DIFF_TRIGGER = Decimal('0.7')

"""
单次交易的数量, 各个币种如下:
    1, eth: 0.1
    2, ltc: 0.1
    3, eos: 1
"""
AMOUNT_ONCE = Decimal('0.1')


"""
平台单次交易的最小数量,各个平台标准不一样:
    1,lq的限制是每次的total不能低于0.0001, 
    2,bfx暂定为0.01
该参数暂时只对bfx有效， 各个币种不一样, 比如辣条根据botvs的标准是0.01, 
暂时设置成这样，出了问题再调整
"""
AMOUNT_MIN = Decimal('0.01')

# 单次交易最小的btc量，计算是amount * price
"""
liqui平台的限制，买卖单的btc total必须大于0.0001, 该参数暂时只对liqui平台有效
liqui各个币种都遵循这个标准, 所以liqui只要处理好这个就行
"""
PRICE_MIN = Decimal('0.0001')

"""liqui如果走maker需要设置该参数"""
SLIDE_PRICE = Decimal('0.0000001')

FEE_BFX = Decimal('0.2')
FEE_LQ = Decimal('0.25')

INTERVAL = 0.5
TICK_INTERVAL = 1

# 取深度里的第几条数据, 总公5条
DEPTH_INDEX_LQ = 0
DEPTH_INDEX_BFX = 2

MAX_DELAY = Decimal('3000')

# max_amount的几分之一
AMOUNT_RATE = Decimal('2')

# 账户内保留的stock数，这里指的是lq的btc量
AMOUNT_RETAIN = Decimal('0.001')

D_FORMAT = Decimal('0.00000000')

all_stop = False


def cancel_all_orders():
    while True:
        order_ids_lq = lqClient.active_orders()
        if order_ids_lq is None:
            time.sleep(INTERVAL)
            continue

        if len(order_ids_lq) == 0:
            break

        for order_id in order_ids_lq:
            lqClient.cancel_order(order_id)

    bfxClient.cancel_all_orders()


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
                time.sleep(INTERVAL)
                continue
            break
    else:
        while True:
            order_r = bfxClient.get_order(order_id)
            if order_r is None:
                time.sleep(INTERVAL)
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
        raise ValueError('liquiq账户不存在btc')

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
    buy_order_price_total = (buy_order_amount * buy_price_and_fee).quantize(D_FORMAT)

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
    balance_enough_bfx = (sell_order_amount >= AMOUNT_MIN) and (sell_order_amount >= AMOUNT_ONCE)
    if balance_enough_bfx:
        state.bfx.can_sell = sell_order_amount
    else:
        state.bfx.can_sell = 0

    if state.lq.can_buy <= 0:
        logger.info("当前差价满足但是lq的btc数量%s不足，或者买单数量%s不满足AmountOnce要求, 循环退出" %
                    (balance_btc_lq, buy_order_amount))
        return
    if state.bfx.can_sell <= 0:
        logger.info("当前差价满足但是bfx的卖单数量%s不足, 循环退出" % sell_order_amount)
        return

    logger.info("当前最多能买%s, 最能能卖%s" % (state.lq.can_buy, state.bfx.can_sell))

    """
    这里是先在lq买进现货，然后在bfx开同等数量的空单
    计算买卖交易的最大amount
    """
    buy_amount = min(AMOUNT_ONCE, state.lq.can_buy, state.bfx.can_sell)
    buy_amount_fee = buy_amount * (state.lq.fee / Decimal('100'))
    buy_amount_real = buy_amount + buy_amount_fee
    buy_order_total = buy_amount_real * buy_price_real
    if buy_order_total < PRICE_MIN:
        logger.debug("当前订单liqui的btc total %s小于0.0001, 循环退出" % str(state.lq.fee))
        return
    # lq下买单
    logger.info("当前liqui 委买单======> 价格: %s, 数量: %s" % (str(buy_price_real), str(buy_amount_real)))
    buy_order_result = lqClient.buy(symbol=get_symbol(constant.EX_LQ, CURRENCY), price=buy_price_real,
                                    amount=buy_amount_real)
    if buy_order_result is None:
        logger.info("当前liqui委买单失败, 退出循环")
        return
    if buy_order_result.error is not None:
        logger.info("lq 委买单失败, 原因: %s, 循环退出" % str(buy_order_result.error))
        return

    logger.info("当前liqui 委买单成功, 订单id: %s" % str(buy_order_result.order_id))

    """
    liqui 下单如果order_id返回0那么表示已成交
    """
    if int(buy_order_result.order_id) == 0:
        """buy_amount是不带手续费"""
        logger.info("当前liqui买单的成交量%s, 订单id: %s" % (str(buy_amount_real), str(buy_order_result.order_id)))
        buy_deal_amount = buy_amount
    else:
        """没有马上完全成交，则查询order的成交数量"""
        time.sleep(TICK_INTERVAL)
        buy_deal_amount = get_deal_amount(constant.EX_LQ, buy_order_result.order_id)
        logger.info("当前liqui买单的成交量%s, 订单id: %s" % (str(buy_deal_amount), str(buy_order_result.order_id)))
        """这里需要增加限制，如果已经成交的部分不满足bfx的下单要求，则直接return, 也就是说成交量太小了直接结束本次交易"""
        """目前还不知道bfx最低交易限制，所以先用自定义的AMOUNT_MIN判断"""
        if buy_deal_amount < AMOUNT_MIN:
            logger.info('当前liqui买单成交量%s小于AMOUNT_MIN, 循环退出' % str(buy_deal_amount))
            return
        """这里如果成交了部分，需要减去手续费"""
        buy_deal_amount = buy_deal_amount - buy_amount_fee

    # bfx期货准备开空单, 数量和lq买单成交的量相同
    sell_amount = buy_deal_amount
    sell_price = state.bfx.ticker.buy.price - SLIDE_PRICE
    while True:
        logger.info("当前bitfinex开空单======>价格: %s,  数量: %s" % (str(sell_price), str(sell_amount)))
        """
        由于bfx直接返回了order对象，所以这里用order.Order对象来接收，接着就可以
        bfx流程如下:
            1, 下margin卖单，得到order.Order对象，这里就不返回id了，减少一次查询的时间
            2, 判断order状态是否完全成交
            3, 如果订单未完成，则1秒后根据order_id继续查询deal_amount,并继续在循环开空单交易
            4, 如果订单完成，则直接退出
        """
        sell_order = bfxClient.margin_sell(get_symbol(constant.EX_BFX, CURRENCY), sell_amount, sell_price)
        if sell_order is None or sell_order.order_id is None:
            """开空单直接失败，继续循环开空单"""
            logger.info("当前bitfinex开空单失败, 0.5秒后重试")
            time.sleep(INTERVAL)
            continue
        else:
            """开空单成功，检查是否完成"""
            if sell_order.is_closed():
                """已全部成交，终止本次流程"""
                logger.info("当前bitfinex订单%s直接完成，交易循环完成" % str(sell_order.order_id))
                break
            else:
                if sell_order.is_canceled():
                    """正常情况下不会是取消，不排除系统强制给取消了"""
                    logger.info("当前bitfinex订单%s处于取消状态，异常状态需要排查" % str(sell_order.order_id))

                """查询成交量"""
                time.sleep(INTERVAL)
                sell_deal_amount = get_deal_amount(constant.EX_BFX, sell_order.order_id)
                logger.info("当前bitfinex卖单的成交量: %s, 订单id: %s" % (str(sell_deal_amount), str(sell_order.order_id)))

                diff_amount = Decimal(str(sell_amount)) - Decimal(str(sell_deal_amount))
                if diff_amount < AMOUNT_MIN:
                    """all_stop只是调试用，仅成交一个循环"""
                    # global all_stop
                    # all_stop = True
                    logger.info('当前liqui和bitfinex交易循环完成')
                    break
                """更新数量"""
                sell_amount = diff_amount
        """
        更新bfx 的价格，以最新的ticker来开空单，此过程大概率亏损
        """
        time.sleep(INTERVAL)
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
    cancel_all_orders()

    state = get_state()
    update_state(state)
    if 'exception' in state.keys() and state.exception is not None:
        logger.debug(str(state.exception))
        return
    buy_price = state.lq.ticker.buy.price if state.lq.is_maker else state.lq.ticker.sell.price
    logger.debug("当前价差========>{buy: " + str(buy_price) +
                 ", sell: " + str(state.bfx.ticker.buy.price) +
                 ", diff_percent: " + str(state.diff_percent) +
                 "}")

    on_action_ticker(state)


def main():
    init()
    while True:
        if all_stop:
            break
        time.sleep(TICK_INTERVAL)
        on_tick()


if __name__ == '__main__':
    main()
