from __future__ import print_function

import hashlib
import time
from decimal import Decimal

import requests

PROTOCOL = "https"
HOST = "www.okcoin.cn/api"
VERSION = "v1"

# HTTP request timeout in seconds
TIMEOUT = 5.0


class PublicClient(object):
    """
    Client for the okcoin.cn API.

    See https://www.okcoin.cn/rest_api.html for API documentation.
    """

    def __init__(self):
        pass

    def server(self):
        return u"{0:s}://{1:s}/{2:s}".format(PROTOCOL, HOST, VERSION)

    def _build_parameters(self, parameters):
        # sort the keys so we can test easily in Python 3.3 (dicts are not
        # ordered)
        keys = list(parameters.keys())
        keys.sort()

        return '&'.join(["%s=%s" % (k, parameters[k]) for k in keys])

    def url_for(self, path, path_arg=None, parameters=None):

        # build the basic url
        url = "%s/%s" % (self.server(), path)

        # If there is a path_arh, interpolate it into the URL.
        # In this case the path that was provided will need to have string
        # interpolation characters in it, such as PATH_TICKER
        if path_arg:
            url = url % (path_arg)

        # Append any parameters to the URL.
        if parameters:
            url = "%s?%s" % (url, self._build_parameters(parameters))

        return url

    def _get(self, url):
        # return requests.get(url, timeout=TIMEOUT)
        try:
            response = requests.get(url, timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            print('OKCoin get' + url + ' failed: ' + str(e))
        else:
            if response.status_code == requests.codes.ok:
                return response.json()

    def ticker(self, symbol):
        symbol = symbol.upper()
        path = 'ticker.do'
        parameters = {
            'symbol': symbol
        }
        return self._get(self.url_for(path=path, parameters=parameters))

    def depth(self, symbol):
        symbol = symbol.upper()
        path = 'depth.do'
        parameters = {
            'symbol': symbol
        }
        return self._get(self.url_for(path=path, parameters=parameters))


class PrivateClient(PublicClient):
    """
    The private api for okcoin user
    """

    def __init__(self, apk_key, apk_secret):
        PublicClient.__init__(self)
        self.api_key = apk_key
        self.apk_secret = apk_secret

    @property
    def _nonce(self):
        return int(time.time() * 1000000)

    def _sign(self, params):
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) + '&'

        sign_bytes = (sign + 'secret_key=' + self.apk_secret).encode('utf-8')
        return hashlib.md5(sign_bytes).hexdigest().upper()

    def _post(self, url, params=None):
        """
        params: dict of the data
        """
        params['api_key'] = self.api_key
        sign = self._sign(params)
        params['sign'] = sign

        headers = {
            "Content-type": "application/x-www-form-urlencoded",
        }
        resp = requests.post(url=url, data=params, headers=headers)
        if resp.status_code == requests.codes.ok:
            return resp.json()

    def account(self):
        url = self.url_for('userinfo.do')
        params = {}
        return self._post(url, params)

    def balance(self, symbol):
        resp = self.account()
        if resp is not None:
            free_item = resp[u'info'][u'funds'][u'free']
            freezed_item = resp[u'info'][u'funds'][u'freezed']

            balance = Decimal(0)
            available_balance = Decimal(0)
            frozen_balance = Decimal(0)

            stocks = Decimal(free_item[symbol])
            frozen_stocks = Decimal(freezed_item[symbol])
            available_stocks = stocks - frozen_stocks

            return {
                u'balance': balance,
                u'available_balance': available_balance,
                u'frozen_balance': frozen_balance,
                u'stocks': stocks,
                u'available_stocks': available_stocks,
                u'frozen_stocks': frozen_stocks
            }

    def place_order(self, symbol, order_type, price, amount):
        url = self.url_for('trade.do')
        params = {
            u'symbol': str(symbol),
            u'type': str(order_type),
            u'price': str(price),
            u'amount': str(amount)
        }
        resp = self._post(url=url, params=params)
        if resp is not None:
            return resp[u'order_id']

    def buy(self, symbol, price, amount):
        return self.place_order(symbol=symbol, order_type='buy', price=price, amount=amount)

    def sell(self, symbol, price, amount):
        return self.place_order(symbol=symbol, order_type='sell', price=price, amount=amount)
