#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bitfinex.client import PrivateClient as BfxClient2

from config import settings


def func():
    client2 = BfxClient2(settings.BFX_API_KEY, settings.BFX_API_SECRET)
    # depth
    print(client2.depth('eosusd'))
    # ticker
    print(client2.ticker('eosusd'))

    # balance
    print(client2.balances())

    # trade


if __name__ == '__main__':
    func()
