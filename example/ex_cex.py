#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from cex.client import PublicClient as CexClient

if __name__ == '__main__':
    client = CexClient()
    print(client.depth("ETH/BTC"))
