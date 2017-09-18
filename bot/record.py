#!/usr/bin/python
# -*- coding: UTF-8 -*-
import getopt
from decimal import Decimal

import sys

from binance.client import PublicClient as BnClient
from bitfinex.client import PublicClient as BfxClient
from common import util, constant

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
    if side_sell != constant.EX_BFX:
        print "exchange sell only support bitfinex now"
        sys.exit()
    if side_buy is None:
        print "exchange buy not found"
        sys.exit()
    if side_buy not in constant.EX_SET:
        print "exchange buy %s not support" % side_buy
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
