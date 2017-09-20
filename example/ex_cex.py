#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from cex.client import PrivateClient as CexClient
from common import util, constant
from config import settings


def main():
    client = CexClient(settings.CEX_USER_ID, settings.CEX_API_KEY, settings.CEX_API_SECRET)
    # balance
    # print(client.balance())

    # depth
    # print(client.depth("ETH/BTC"))

    # place order
    # currency = 'bch'
    # symbol = util.get_symbol_btc(constant.EX_CEX, currency)
    # price = '0.10209'
    # amount = '0.1'
    # order, error = client.buy(symbol=symbol, price=price, amount=amount)
    # if error is not None or order is None or order.order_id is None:
    #     print (error.message)
    # else:
    #     print(order.order_id)

    # order status
    # order, error = client.get_order('4412711710')
    # if error is not None or order is None or order.order_id is None:
    #     print (error.message)
    # else:
    #     print(order)

    # cancel order
    # print(client.cancel_order('4412711710'))

    # cancel all orders
    # if client.cancel_all_orders('BCH/BTC') is True:
    #     print("cancel all orders success")


if __name__ == '__main__':
    main()
