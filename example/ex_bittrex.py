#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from bittrex.client import Bittrex


def main():
    client = Bittrex('', '')
    resp = client.depth("BTC-ZEC")
    print(str(resp))


if __name__ == '__main__':
    main()
