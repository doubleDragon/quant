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
from common import util, constant, log

TICK_INTERVAL = 2
INTERVAL = 0.8

currency = 'eth'

client_sell = None
client_buy = None

# 交易所字符串
exchange_buy = None
exchange_sell = None

diff_count = 0

logger = log.get_logger(log_name='record', level=logging.DEBUG)


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

    price_sell = depth_sell.bids[0].price
    price_buy = depth_buy.asks[0].price

    diff = price_sell - price_buy
    diff_percent = diff / price_buy * Decimal('100')
    diff_percent = diff_percent.quantize(Decimal('0.00000000'))
    if diff_percent > settings.TRIGGER_DIFF_PERCENT:
        global diff_count
        diff_count += 1
    logger.info("%s 买价: %s，    %s 卖价: %s" % (exchange_buy, price_buy, exchange_sell, price_sell))
    logger.info("%s %s 的差价:%s,    差价百分比: %s,   频率: %s" %
                (exchange_sell, exchange_buy, diff, diff_percent, diff_count))


def start():
    init()
    while True:
        time.sleep(TICK_INTERVAL)
        on_tick()


def main(argv):
    side_buy = None
    side_sell = constant.EX_BFX
    try:
        opts, args = getopt.getopt(argv, "hlb:s:", ['buy=', 'sell=', 'list'])
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
    print("exchange buy  is: %s" % side_buy)
    print("exchange sell is: %s" % side_sell)
    if side_sell not in (constant.EX_BFX, constant.EX_CEX):
        print "exchange sell only support bitfinex and cex now"
        sys.exit()
    if side_buy is None:
        print "exchange buy not found"
        sys.exit()
    if side_buy not in constant.EX_SET:
        print "exchange buy %s not support" % side_buy
        sys.exit()
    global exchange_buy
    global exchange_sell
    exchange_buy = side_buy
    exchange_sell = side_sell
    start()


if __name__ == '__main__':
    main(sys.argv[1:])
