#
# GDAX/PublicClient.py
# Daniel Paquin
#
# For public requests to the GDAX exchange
from decimal import Decimal

import requests

from common import depth

BASE_URL = 'https://api.gdax.com'

# HTTP request timeout in seconds
TIMEOUT = 5.0


class PublicClient(object):
    """GDAX public client API.

    All requests default to the `product_id` specified at object
    creation if not otherwise specified.

    Attributes:
        url (Optional[str]): API URL. Defaults to GDAX API.

    """

    def __init__(self):
        """Create GDAX API public client.

        Args:
            api_url (Optional[str]): API URL. Defaults to GDAX API.

        """
        self.url = BASE_URL

    def _get(self, url, params=None):
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            print('gdax get' + url + ' failed: ' + str(e))
        else:
            if response.status_code == requests.codes.ok:
                return response.json()

    def get_products(self):
        """Get a list of available currency pairs for trading.

        Returns:
            list: Info about all currency pairs. Example::
                [
                    {
                        "id": "BTC-USD",
                        "display_name": "BTC/USD",
                        "base_currency": "BTC",
                        "quote_currency": "USD",
                        "base_min_size": "0.01",
                        "base_max_size": "10000.00",
                        "quote_increment": "0.01"
                    }
                ]

        """
        url = self.url + '/products'
        return self._get(url=url)

    def depth(self, product_id, level=2):
        """Get a list of open orders for a product.

        The amount of detail shown can be customized with the `level`
        parameter:
        * 1: Only the best bid and ask
        * 2: Top 50 bids and asks (aggregated)
        * 3: Full order book (non aggregated)

        Level 1 and Level 2 are recommended for polling. For the most
        up-to-date data, consider using the websocket stream.

        **Caution**: Level 3 is only recommended for users wishing to
        maintain a full real-time order book using the websocket
        stream. Abuse of Level 3 via polling will cause your access to
        be limited or blocked.

        Args:
            product_id (str): Product
            level (Optional[int]): Order book level (1, 2, or 3).
                Default is 1.

        Returns:
            dict: Order book. Example for level 1::
                {
                    "sequence": "3",
                    "bids": [
                        [ price, size, num-orders ],
                    ],
                    "asks": [
                        [ price, size, num-orders ],
                    ]
                }

        """
        params = {'level': level}
        url = self.url + '/products/{}/book'.format(product_id)

        resp = self._get(url, params)
        if resp is not None:
            data = {
                u'bids': [],
                u'asks': []
            }
            tmp = [u'price', u'amount']

            def fn(x):
                return Decimal(str(x))

            asks = resp[u'asks']
            bids = resp[u'bids']

            for i in range(5):
                # bid is a array
                bid_dict = dict(zip(tmp, bids[i]))
                bid_dict = dict(zip(bid_dict.keys(), map(fn, bid_dict.values())))

                ask_dict = dict(zip(tmp, asks[i]))
                ask_dict = dict(zip(ask_dict.keys(), map(fn, ask_dict.values())))

                data[u'bids'].append(bid_dict)
                data[u'asks'].append(ask_dict)

            return depth.dict_to_depth(data)

    def ticker(self, product_id):
        """Snapshot about the last trade (tick), best bid/ask and 24h volume.

        **Caution**: Polling is discouraged in favor of connecting via
        the websocket stream and listening for match messages.

        Args:
            product_id (str): Product

        Returns:
            dict: Ticker info. Example::
                {
                  "trade_id": 4729088,
                  "price": "333.99",
                  "size": "0.193",
                  "bid": "333.98",
                  "ask": "333.99",
                  "volume": "5957.11914015",
                  "time": "2015-11-14T20:46:03.511254Z"
                }

        """
        url = self.url + '/products/{}/ticker'.format(product_id)
        return self._get(url=url)

    def get_product_trades(self, product_id):
        """List the latest trades for a product.

        Args:
            product_id (str): Product

        Returns:
            list: Latest trades. Example::
                [{
                    "time": "2014-11-07T22:19:28.578544Z",
                    "trade_id": 74,
                    "price": "10.00000000",
                    "size": "0.01000000",
                    "side": "buy"
                }, {
                    "time": "2014-11-07T01:08:43.642366Z",
                    "trade_id": 73,
                    "price": "100.00000000",
                    "size": "0.01000000",
                    "side": "sell"
                }]

        """
        r = requests.get(self.url + '/products/{}/trades'.format(product_id), timeout=30)
        # r.raise_for_status()
        return r.json()

    def get_product_historic_rates(self, product_id, start=None, end=None,
                                   granularity=None):
        """Historic rates for a product.

        Rates are returned in grouped buckets based on requested
        `granularity`. If start, end, and granularity aren't provided,
        the exchange will assume some (currently unknown) default values.

        Historical rate data may be incomplete. No data is published for
        intervals where there are no ticks.

        **Caution**: Historical rates should not be polled frequently.
        If you need real-time information, use the trade and book
        endpoints along with the websocket feed.

        The maximum number of data points for a single request is 200
        candles. If your selection of start/end time and granularity
        will result in more than 200 data points, your request will be
        rejected. If you wish to retrieve fine granularity data over a
        larger time range, you will need to make multiple requests with
        new start/end ranges.

        Args:
            product_id (str): Product
            start (Optional[str]): Start time in ISO 8601
            end (Optional[str]): End time in ISO 8601
            granularity (Optional[str]): Desired time slice in seconds

        Returns:
            list: Historic candle data. Example::
                [
                    [ time, low, high, open, close, volume ],
                    [ 1415398768, 0.32, 4.2, 0.35, 4.2, 12.3 ],
                    ...
                ]

        """
        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        if granularity is not None:
            params['granularity'] = granularity
        r = requests.get(self.url + '/products/{}/candles'
                         .format(product_id), params=params, timeout=30)
        # r.raise_for_status()
        return r.json()

    def get_product_24hr_stats(self, product_id):
        """Get 24 hr stats for the product.

        Args:
            product_id (str): Product

        Returns:
            dict: 24 hour stats. Volume is in base currency units.
                Open, high, low are in quote currency units. Example::
                    {
                        "open": "34.19000000",
                        "high": "95.70000000",
                        "low": "7.06000000",
                        "volume": "2.41000000"
                    }

        """
        r = requests.get(self.url + '/products/{}/stats'.format(product_id), timeout=30)
        # r.raise_for_status()
        return r.json()

    def get_currencies(self):
        """List known currencies.

        Returns:
            list: List of currencies. Example::
                [{
                    "id": "BTC",
                    "name": "Bitcoin",
                    "min_size": "0.00000001"
                }, {
                    "id": "USD",
                    "name": "United States Dollar",
                    "min_size": "0.01000000"
                }]

        """
        r = requests.get(self.url + '/currencies', timeout=30)
        # r.raise_for_status()
        return r.json()

    def get_time(self):
        """Get the API server time.

        Returns:
            dict: Server time in ISO and epoch format (decimal seconds
                since Unix epoch). Example::
                    {
                        "iso": "2015-01-07T23:47:25.201Z",
                        "epoch": 1420674445.201
                    }

        """
        r = requests.get(self.url + '/time', timeout=30)
        # r.raise_for_status()
        return r.json()
