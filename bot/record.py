#!/usr/bin/python
# -*- coding: UTF-8 -*-
import getopt
from decimal import Decimal

import sys

from binance.client import PublicClient as BnClient
from bitfinex.client import PublicClient as BfxClient
from common import util

clint0 = None
clint1 = None

currency = 'eth'


def get_symbol(ex_name):
    return util.get_symbol_btc(ex_name, currency)


def fun0():
    global clint0
    global clint1
    clint0 = BnClient()
    clint1 = BfxClient()


def fun1():
    # bfx平台
    depth0 = clint0.depth(get_symbol())
    if depth0 is None:
        return
    depth1 = clint1.depth()
    if depth1 is None:
        return
    price_sell = depth0.bids[0].price
    price_buy = depth1.asks[0].price

    diff = (price_sell - price_buy) / price_buy * Decimal('100')
    print("差价百分比: %s" % diff)


def main(argv):
    side_buy = ''
    side_sell = ''
    try:
        opts, args = getopt.getopt(argv, "hb:s:", ["buy=", "sell="])
    except getopt.GetoptError:
        print 'record.py -b <buy> -s <sell>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'record.py -b <buy> -sell <sell>'
            sys.exit()
        elif opt in ("-b", "--buy"):
            side_buy = arg
        elif opt in ("-s", "--sell"):
            side_sell = arg
    print("exchange buy  is: %s" % side_buy)
    print("exchange sell is: %s" % side_sell)


if __name__ == '__main__':
    main(sys.argv[1:])
    # fun0()
    # fun1()
