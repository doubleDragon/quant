#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
from decimal import Decimal

from bitfinex.client import PublicClient as BfxClient
from binance.client import PublicClient as BnClient

from common import constant, util, log

import logging

logger = log.get_logger(log_name='diff', level=logging.DEBUG)

INTERVAL = 3

# btc
CURRENCY_LTC = u'ltc'
CURRENCY_ETH = u'eth'
CURRENCY_BCC = u'bcc'
CURRENCY_NEO = u'neo'
CURRENCY_OMG = u'omg'
CURRENCY_IOTA = u'iota'
# eth
CURRENCY_EOS = u'eos'

# TRIGGER_LIST = [Decimal('0.00043'), Decimal('0.000095'), Decimal('0.000095'), Decimal('0.000095')]

# DIFF_TRIGGER = Decimal('0.000095')

bfxClient = BfxClient()
bnClient = BnClient()

DEPTH_INDEX_BFX = 1
DEPTH_INDEX_BINANCE = 0

TRIGGER_PERCENT = Decimal('1.0')

CURRENCIES = [CURRENCY_ETH, CURRENCY_LTC, CURRENCY_BCC, CURRENCY_NEO, CURRENCY_OMG, CURRENCY_IOTA]
trigger_count = {
    CURRENCY_ETH: 0,
    CURRENCY_LTC: 0,
    CURRENCY_BCC: 0,
    CURRENCY_NEO: 0,
    CURRENCY_OMG: 0,
    CURRENCY_IOTA: 0,
}
is_maker = False
is_eth = False

D_FORMAT = Decimal('0.00000000')


def get_symbol(ex_name, currency):
    if is_eth is True:
        return util.get_symbol_eth(ex_name, currency)
    else:
        return util.get_symbol_btc(ex_name, currency)


def on_tick():
    for i in range(len(CURRENCIES)):
        currency = CURRENCIES[i]

        depth_bn = bnClient.depth(get_symbol(constant.EX_BINANCE, currency))
        if depth_bn is None:
            return
        depth_bfx = bfxClient.depth(get_symbol(constant.EX_BFX, currency))
        if depth_bfx is None:
            return
        sell_price_bn = depth_bn.asks[DEPTH_INDEX_BINANCE].price
        buy_price_bn = depth_bn.asks[DEPTH_INDEX_BINANCE].price
        buy_price_bfx = depth_bfx.bids[DEPTH_INDEX_BFX].price

        if is_maker:
            diff = buy_price_bfx - buy_price_bn
            diff_percent = diff / buy_price_bn * Decimal('100')
        else:
            diff = buy_price_bfx - sell_price_bn
            diff_percent = diff / sell_price_bn * Decimal('100')
        diff_percent = diff_percent.quantize(D_FORMAT)

        global trigger_count
        logger.debug(str(currency) + '===========>差价:' + str(diff) + "---百分比: " + str(diff_percent) +
                     "---计数: " + str(trigger_count[currency]))

        # trigger = TRIGGER_LIST[i]
        if diff_percent >= TRIGGER_PERCENT:
            trigger_count[currency] += 1


def main():
    while True:
        time.sleep(INTERVAL)
        on_tick()


if __name__ == '__main__':
    main()
