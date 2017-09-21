#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from decimal import Decimal


"""单次交易的最小BTC价值，类似于lq的total"""
MIN_PRICE_BCH = Decimal('0.005')
MIN_PRICE_DASH = Decimal('0.005')
"""单次交易的最小币数量"""
MIN_STOCK_BCH = Decimal('0.1')
MIN_STOCK_DASH = Decimal('0.01')

MIN_PRICE = MIN_PRICE_DASH
MIN_STOCK = MIN_STOCK_DASH

FEE_MAKER = Decimal('0')
FEE_TAKER = Decimal('0.2')
