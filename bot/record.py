#!/usr/bin/python
# -*- coding: UTF-8 -*-
import getopt
from decimal import Decimal

import sys

import time

import logging

from binance.client import PublicClient as BnClient
from bitfinex.client import PublicClient as BfxClient
from config import settings
from liqui.client import PublicClient as LqClient
from cex.client import PublicClient as CexClient
from gdax.client import PublicClient as GdaxClient
from exmo.client import PublicClient as ExmoClient
from poloniex.client import Client as PoloClient
from bittrex.client import Bittrex as BittrexClient
from common import util, constant, log

TICK_INTERVAL = 2
INTERVAL = 0.8

currency = None

client_sell = None
client_buy = None

# 交易所字符串
exchange_buy = None
exchange_sell = None

diff_count_forward = 0
diff_count_reverse = 0

logger = log.get_logger(log_name='record', level=logging.DEBUG)

"""
python -m bot.record -bbinance -sbitfinex -ceth
"""


def get_symbol(ex_name):
    return util.get_symbol_btc(ex_name, currency)


def get_client(name):
    if name == constant.EX_LQ:
        return LqClient()
    if name == constant.EX_BFX:
        return BfxClient()
    if name == constant.EX_BINANCE:
        return BnClient()
    if name == constant.EX_CEX:
        return CexClient()
    if name == constant.EX_GDAX:
        return GdaxClient()
    if name == constant.EX_EXMO:
        return ExmoClient()
    if name == constant.EX_POLONIEX:
        return PoloClient()
    if name == constant.EX_BITTREX:
        return BittrexClient('', '')
    return None


def init():
    global client_sell
    global client_buy
    client_sell = get_client(str(exchange_sell))
    client_buy = get_client(str(exchange_buy))
    if not client_buy or not client_sell:
        raise Exception('exchange not exists')


def on_tick():
    depth_sell = client_sell.depth(get_symbol(exchange_sell))
    if depth_sell is None:
        return

    depth_buy = client_buy.depth(get_symbol(exchange_buy))
    if depth_buy is None:
        return

    # forward
    price_sell_forward = depth_sell.bids[0].price
    price_buy_forward = depth_buy.asks[0].price

    diff_forward = price_sell_forward - price_buy_forward
    diff_percent_forward = diff_forward / price_buy_forward * Decimal('100')
    diff_percent_forward = diff_percent_forward.quantize(Decimal('0.00000000'))
    if diff_percent_forward > settings.TRIGGER_DIFF_PERCENT:
        global diff_count_forward
        diff_count_forward += 1
    logger.info("forward======>%s  买价: %s， 卖价: %s" %
                (currency, price_buy_forward, price_sell_forward))
    logger.info("forward======>%s %s %s 的差价:%s,    差价百分比: %s,   频率: %s" %
                (currency, exchange_sell, exchange_buy, diff_forward, diff_percent_forward, diff_count_forward))

    price_sell_reverse = depth_buy.bids[0].price
    price_buy_reverse = depth_sell.asks[0].price
    diff_reverse = price_sell_reverse - price_buy_reverse
    diff_percent_reverse = diff_reverse / price_buy_reverse * Decimal('100')
    diff_percent_reverse = diff_percent_reverse.quantize(Decimal('0.00000000'))
    if diff_percent_reverse > settings.TRIGGER_DIFF_PERCENT:
        global diff_count_reverse
        diff_count_reverse += 1
    logger.info("reverse======>%s 买价: %s，  卖价: %s" %
                (currency, price_sell_reverse, price_buy_reverse))
    logger.info("reverse======>%s %s %s 的差价:%s,    差价百分比: %s,   频率: %s" %
                (currency, exchange_sell, exchange_buy, diff_reverse, diff_percent_reverse, diff_count_reverse))


def start():
    init()
    while True:
        time.sleep(TICK_INTERVAL)
        on_tick()


def main(argv):
    side_buy = None
    side_sell = None
    c = None
    try:
        opts, args = getopt.getopt(argv, "hlb:s:c:", ['buy=', 'sell=', 'currency=', 'list'])
    except getopt.GetoptError as e:
        print str(e)
        sys.exit()
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'record.py -b <buy> -sell <sell>'
            sys.exit()
        elif opt in ('-l', '--list'):
            print(str(constant.EX_SET))
            sys.exit()
        elif opt in ("-b", "--buy"):
            side_buy = arg
        elif opt in ("-s", "--sell"):
            side_sell = arg
        elif opt in ("-c", "--currency"):
            c = arg

    if side_sell is None:
        print "exchange sell not found"
        sys.exit()
    if side_sell not in constant.EX_SET:
        print "exchange sell %s not support" % side_sell
        sys.exit()
    if side_buy is None:
        print "exchange buy not found"
        sys.exit()
    if side_buy not in constant.EX_SET:
        print "exchange buy %s not support" % side_buy
        sys.exit()

    if not c:
        print "exchange currencynot exists"
        sys.exit()
    global exchange_buy
    global exchange_sell
    global currency
    exchange_buy = side_buy
    exchange_sell = side_sell
    currency = c

    print("exchange buy  is: %s" % side_buy)
    print("exchange sell is: %s" % side_sell)
    print("exchange currency is: %s" % c)
    start()


if __name__ == '__main__':
    main(sys.argv[1:])
