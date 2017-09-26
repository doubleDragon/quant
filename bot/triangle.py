#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse
import time

from decimal import Decimal

from common import util, constant
from config import settings
from bitfinex.client import PublicClient as BfxClient
from liqui.client import PublicClient as LqClient

DECIMAL_FORMAT = Decimal('0.00000000')


class Triangle(object):
    def __init__(self):
        super(Triangle, self).__init__()
        self.base_cur = 'bch'
        self.quote_cur = 'btc'
        self.mid_cur = 'usd'
        self.client_bfx = BfxClient()
        self.client_lq = LqClient()

    def on_tick(self):
        # get ticker for all cur
        symbol1 = util.get_symbol(constant.EX_BFX, self.quote_cur, self.mid_cur)
        symbol2 = util.get_symbol(constant.EX_BFX, self.base_cur, self.mid_cur)
        symbol3 = util.get_symbol_eth(constant.EX_LQ, self.base_cur)

        depth1 = self.client_bfx.depth(symbol1)
        depth2 = self.client_bfx.depth(symbol2)
        depth3 = self.client_lq.depth(symbol3)
        if not depth1 or not depth2 or not depth3:
            return

        # 正循环套利空间
        p1 = depth1.asks[0].price
        p2 = depth2.bids[0].price
        p3 = depth3.asks[0].price
        positive_diff = (p2 / p1 - p3).quantize(DECIMAL_FORMAT)
        positive_diff_percent = (positive_diff / p3 * Decimal('100')).quantize(DECIMAL_FORMAT)

        # 逆循环套利空间
        p1 = depth1.bids[0].price
        p2 = depth2.asks[0].price
        p3 = depth3.bids[0].price
        negative_diff = (p3 - p2 / p1).quantize(DECIMAL_FORMAT)
        negative_diff_percent = (negative_diff / (p2 / p1)).quantize(DECIMAL_FORMAT)

        print ("%s==>正循环套利空间: %s  %s,  逆循环套利空间: %s  %s" %
               (self.base_cur, positive_diff, positive_diff_percent, negative_diff, negative_diff_percent))

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--markets", type=str,
                            help="markets, example: -mBitfinexCNY,Bitstamp")


if __name__ == '__main__':
    triangle = Triangle()
    while True:
        triangle.on_tick()
        time.sleep(settings.TICK_INTERVAL)
