#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from config import settings

from util import timestamp

from common import constant, util, log

import time
from decimal import Decimal

from cex.client import PrivateClient as CexClient
from bitfinex.client import PrivateClient as BfxClient
from bitfinex import config as BfxConfig
from cex import config as CexConfig

from bunch import Bunch

import logging

logger = log.get_logger(log_name='wsl', level=logging.INFO)

bfxClient = BfxClient(settings.BFX_API_KEY, settings.BFX_API_SECRET)
cexClient = CexClient(settings.CEX_USER_ID, settings.CEX_API_KEY, settings.CEX_API_SECRET)

CURRENCY = settings.CURRENCY

D_FORMAT = Decimal('0.00000000')

all_stop = False


def init():
    pass


def cancel_all_orders():
    cancel_success = False
    while cancel_success is False:
        cancel_success = cexClient.cancel_all_orders(get_symbol(constant.EX_CEX, CURRENCY))
        if cancel_success:
            break
        time.sleep(settings.INTERVAL)

    cancel_success = False
    while cancel_success is False:
        cancel_success = bfxClient.cancel_all_orders()
        if cancel_success:
            break
        time.sleep(settings.INTERVAL)


def get_max_amount(list_tmp, index):
    amount = Decimal('0')
    for i in range(5):
        item = list_tmp[i]
        if i == index:
            amount = amount + item.amount
    return amount


def get_symbol(ex_name, currency):
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
    depth_cex = cexClient.depth(get_symbol(constant.EX_CEX, CURRENCY))
    if depth_cex is None:
        state.exception = 'cex深度信息获取失败'
        return
    end = Decimal(timestamp.get_current_time())
    delay_cex = end - start
    state.cex.depth = depth_cex

    delay = max(delay_cex, delay_bfx)
    state.delay = delay

    # make ticker bfx, 这里主要是开空单，走吃单模式， index = 1
    depth_index_bfx = 1
    price_sell_bfx = depth_bfx.asks[depth_index_bfx].price
    price_buy_bfx = depth_bfx.bids[depth_index_bfx].price

    amount_sell_bfx = get_max_amount(depth_bfx.asks, depth_index_bfx)
    amount_buy_bfx = get_max_amount(depth_bfx.bids, depth_index_bfx)

    state.bfx.ticker = Bunch({
        'buy': Bunch({
            'price': price_buy_bfx,
            'max_amount': amount_buy_bfx
        }),
        'sell': Bunch({
            'price': price_sell_bfx,
            'max_amount': amount_sell_bfx
        })
    })

    # cex make ticker dict, 这里主要是走挂单， index = 0
    depth_index_cex = 0
    price_sell_cex = depth_cex.asks[depth_index_cex].price
    price_buy_cex = depth_cex.bids[depth_index_cex].price
    amount_sell_cex = get_max_amount(depth_cex.asks, depth_index_cex)
    amount_buy_cex = get_max_amount(depth_cex.bids, depth_index_cex)

    state.cex.ticker = Bunch({
        'buy': Bunch({
            'price': price_buy_cex,
            'max_amount': amount_buy_cex
        }),
        'sell': Bunch({
            'price': price_sell_cex,
            'max_amount': amount_sell_cex
        })
    })

    # bfx卖 cex买，所以bfx-cex
    if state.cex.is_maker:
        state.diff = price_buy_bfx - price_buy_cex
        state.diff_percent = (state.diff / price_buy_cex * Decimal('100')).quantize(D_FORMAT)
    else:
        state.diff = price_buy_bfx - price_sell_cex
        state.diff_percent = (state.diff / price_sell_cex * Decimal('100')).quantize(D_FORMAT)


def get_state():
    while True:
        account_bfx = bfxClient.balance()
        if account_bfx is None:
            time.sleep(settings.INTERVAL)
            continue
        break

    while True:
        account_cex = cexClient.balance()
        if account_cex is None:
            time.sleep(settings.INTERVAL)
            continue
        break

    bfx_dict = Bunch()
    bfx_dict.account = account_bfx
    bfx_dict.is_maker = False
    bfx_dict.fee = BfxConfig.FEE_MAKER if bfx_dict.is_maker else BfxConfig.FEE_TAKER

    cex_dict = Bunch()
    cex_dict.account = account_cex
    cex_dict.is_maker = False
    cex_dict.fee = CexConfig.FEE_MAKER if cex_dict.is_maker else CexConfig.FEE_TAKER

    state = Bunch({
        'bfx': bfx_dict,
        'cex': cex_dict
    })
    return state


def get_deal_amount(ex_name, order_id):
    """
    获取订单的成交量
    :param ex_name: cex or bitfinex
    :param order_id: order id
    :return: deal amount , type is Decimal
    """
    if ex_name == constant.EX_CEX:
        while True:
            order_r, error = cexClient.get_order(order_id)
            if (order_r is None) or (error is not None):
                time.sleep(settings.INTERVAL)
                continue
            break
    else:
        while True:
            order_r, error = bfxClient.get_order(order_id)
            if (order_r is None) or (error is not None):
                time.sleep(settings.INTERVAL)
                continue
            break

    if order_r.is_pending():
        logger.info("订单%s未完成,  已完成%s, 初始%s" %
                    (str(order_r.order_id), str(order_r.deal_amount), str(order_r.amount)))
        if ex_name == constant.EX_CEX:
            cexClient.cancel_order(order_id)
        else:
            bfxClient.cancel_order(order_id)
        time.sleep(settings.TICK_INTERVAL)
        return get_deal_amount(ex_name, order_id)
    else:
        if order_r.is_canceled():
            logger.info("订单%s已取消,  已完成%s, 初始%s" %
                        (str(order_r.order_id), str(order_r.deal_amount), str(order_r.amount)))
        if order_r.is_closed():
            logger.info("订单%s已完成,  已完成%s, 初始%s" %
                        (str(order_r.order_id), str(order_r.deal_amount), str(order_r.amount)))
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
    流程如下
        1,判断是否满足买的条件，btc余额
        2,委托买单
        3,超时或者部分成交则取消买单
    条件因素:
        1,手续费
        2,是否走maker
        3,total计算并判断, liqui最低btc total限度为0.0001
    """

    btc_cex = None
    for i in state.cex.account:
        if i.currency == u'btc':
            btc_cex = i

    if btc_cex is None:
        raise ValueError('cex账户不存在btc')

    balance_btc_cex = Decimal(str(btc_cex.balance))
    if state.cex.is_maker:
        max_amount_cex = state.cex.ticker.buy.max_amount
        buy_price_cex = state.cex.ticker.buy.price
    else:
        max_amount_cex = state.cex.ticker.sell.max_amount
        buy_price_cex = state.cex.ticker.sell.price

    buy_price_real = buy_price_cex + settings.SLIDE_PRICE
    buy_price_and_fee = buy_price_real * (state.cex.fee / Decimal('100') + Decimal('1'))
    can_buy = (balance_btc_cex - settings.AMOUNT_RETAIN) / buy_price_and_fee
    buy_order_amount = min(max_amount_cex, can_buy)
    buy_order_price_total = (buy_order_amount * buy_price_and_fee).quantize(D_FORMAT)

    balance_enough_cex = (buy_order_amount >= settings.AMOUNT_ONCE) and (buy_order_amount >= CexConfig.MIN_STOCK)
    total_enough_cex = buy_order_price_total > CexConfig.MIN_PRICE
    if balance_enough_cex and total_enough_cex:
        state.cex.can_buy = buy_order_amount
    else:
        state.cex.can_buy = Decimal('0')

    # 判断bfx margin账户的余额是否足够，这里不做判断，bfx放很多余额，所以一定够？ 这个逻辑可能不对，先这样
    # bfx始终走taker, 所以取buy属性
    # 计算出bfx最大能卖的ltc数量

    """
    1,计算出bfx最大能卖的ltc数量?margin账户的余额是否足够，这里不做判断，bfx放很多余额，所以一定够？ 这个逻辑可能不对，先这样
    2,bfx始终走taker, 所以取buy属性
    """
    max_amount_bfx = state.bfx.ticker.buy.max_amount
    sell_order_amount = max_amount_bfx / settings.AMOUNT_RATE
    balance_enough_bfx = (sell_order_amount >= BfxConfig.MIN_STOCK) and (sell_order_amount >= settings.AMOUNT_ONCE)
    if balance_enough_bfx:
        state.bfx.can_sell = sell_order_amount
    else:
        state.bfx.can_sell = 0

    if state.cex.can_buy <= 0:
        logger.info("当前差价满足但是cex的btc数量%s不足，或者买单数量%s不满足AmountOnce要求, 循环退出" %
                    (balance_btc_cex, buy_order_amount))
        return
    if state.bfx.can_sell <= 0:
        logger.info("当前差价满足但是bfx的卖单数量%s不足, 循环退出" % sell_order_amount)
        return

    logger.info("当前最多能买%s, 最能能卖%s" % (state.cex.can_buy, state.bfx.can_sell))

    """
    这里是先在cex买进现货，然后在bfx开同等数量的空单
    计算买卖交易的最大amount
    """
    buy_amount = min(settings.AMOUNT_ONCE, state.cex.can_buy, state.bfx.can_sell)
    buy_amount_fee = buy_amount * (state.cex.fee / Decimal('100'))
    buy_amount_real = buy_amount + buy_amount_fee
    buy_order_total = buy_amount_real * buy_price_real
    if buy_order_total < CexConfig.MIN_PRICE:
        logger.info("当前订单cex的btc total %s小于0.0001, 循环退出" % str(state.cex.fee))
        return
    # cex下买单
    logger.info("当前cex 委买单======> 价格: %s, 数量: %s" % (str(buy_price_real), str(buy_amount_real)))
    buy_order, error = cexClient.buy(symbol=get_symbol(constant.EX_CEX, CURRENCY), price=buy_price_real,
                                     amount=buy_amount_real)
    if buy_order is None:
        logger.info("当前cex委买单失败, 退出循环")
        return
    if error is not None:
        logger.info("cex 委买单失败, 原因: %s, 循环退出" % str(error.message))
        return

    logger.info("当前cex 委买单成功, 订单id: %s" % str(buy_order.order_id))

    """
    cex 下单如果order_id返回0那么表示已成交
    """
    if buy_order.is_closed():
        """buy_amount是不带手续费"""
        logger.info("当前cex买单的成交量%s, 订单id: %s" % (str(buy_amount_real), str(buy_order.order_id)))
        buy_deal_amount = buy_amount
    else:
        """没有马上完全成交，则查询order的成交数量"""
        time.sleep(settings.TICK_INTERVAL)
        buy_deal_amount = get_deal_amount(constant.EX_CEX, buy_order.order_id)
        logger.info("当前cex买单的成交量%s, 订单id: %s" % (str(buy_deal_amount), str(buy_order.order_id)))
        """这里需要增加限制，如果已经成交的部分不满足bfx的下单要求，则直接return, 也就是说成交量太小了直接结束本次交易"""
        """目前还不知道bfx最低交易限制，所以先用cex的MIN_STOCK来判断, 这个地方需要优化"""
        if buy_deal_amount < CexConfig.MIN_STOCK:
            logger.info('当前cex买单成交量%s小于最低限制%s, 循环退出' % (buy_deal_amount, CexConfig.MIN_STOCK))
            return
        """这里如果成交了部分，需要减去手续费"""
        buy_deal_amount = Decimal(str(buy_deal_amount) - Decimal(str(buy_amount_fee)))
        buy_deal_amount = buy_deal_amount.quantize(D_FORMAT)

    # bfx期货准备开空单, 数量和cex买单成交的量相同
    sell_amount = buy_deal_amount
    sell_price = state.bfx.ticker.buy.price - settings.SLIDE_PRICE
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
        sell_order, error = bfxClient.margin_sell(get_symbol(constant.EX_BFX, CURRENCY), sell_amount, sell_price)
        if sell_order is None or sell_order.order_id is None:
            """开空单直接失败，继续循环开空单"""
            error_message = "未知" if error is not None else error.message
            logger.info("当前bitfinex开空单失败, 0.5秒后重试, 原因是%s" % error_message)
            time.sleep(settings.INTERVAL)
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
                time.sleep(settings.INTERVAL)
                sell_deal_amount = get_deal_amount(constant.EX_BFX, sell_order.order_id)
                logger.info("当前bitfinex卖单的成交量: %s, 订单id: %s" % (str(sell_deal_amount), str(sell_order.order_id)))

                diff_amount = Decimal(str(sell_amount)) - Decimal(str(sell_deal_amount))
                """Bitfinex的最小交易数量目前设置成0.01, 可能是错误的，需要优化"""
                if diff_amount < BfxConfig.MIN_STOCK:
                    """all_stop只是调试用，仅成交一个循环"""
                    global all_stop
                    all_stop = True
                    logger.info('当前cex和bitfinex交易循环完成')
                    break
                """更新数量"""
                sell_amount = diff_amount
        """
        更新bfx 的价格，以最新的ticker来开空单，此过程大概率亏损
        """
        time.sleep(settings.INTERVAL)
        bfx_ticker = get_bfx_ticker()
        sell_price = bfx_ticker.buy - settings.SLIDE_PRICE


def on_action_ticker(state):
    if state.diff_percent >= settings.TRIGGER_DIFF_PERCENT:
        if state.delay > settings.MAX_DELAY:
            # 延迟超过设定的值，放弃这次机会
            logger.info("差价触发, 但是延迟超过%s, 放弃机会%s" % (state.delay, state.diff_percent))
            return
        logger.info('差价触发,准备交易========>diff_percent: ' + str(state.diff_percent))
        on_action_trade(state)


def on_tick():
    cancel_all_orders()

    state = get_state()
    update_state(state)
    if 'exception' in state.keys() and state.exception is not None:
        logger.debug(str(state.exception))
        return
    buy_price = state.cex.ticker.buy.price if state.cex.is_maker else state.cex.ticker.sell.price
    logger.info("\n\n当前价差========>{buy: " + str(buy_price) +
                ", sell: " + str(state.bfx.ticker.buy.price) +
                ", diff_percent: " + str(state.diff_percent) +
                "}")

    on_action_ticker(state)


def main():
    init()
    while True:
        if all_stop:
            break
        time.sleep(settings.TICK_INTERVAL)
        on_tick()


if __name__ == '__main__':
    main()
