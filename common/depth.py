# coding=utf-8
class Item(object):
    def __init__(self, price, amount):
        super(Item, self).__init__()
        self.price = price
        self.amount = amount

    def __str__(self):
        data = {
            u'price': self.price,
            u'amount': self.amount
        }
        return str(data)

    def __repr__(self):
        data = {
            u'price': self.price,
            u'amount': self.amount
        }
        return str(data)


class Depth(object):
    def __init__(self, bids, asks):
        super(Depth, self).__init__()
        self.bids = bids
        self.asks = asks

    def __str__(self):
        data = {
            'bids': self.bids,
            'asks': self.asks
        }
        return str(str(data))

    def __repr__(self):
        data = {
            'bids': self.bids,
            'asks': self.asks
        }
        return str(str(data))


def dict_to_depth(data):
    """
    默认转换, 特殊情况就再实现
    """
    bids = []
    asks = []
    lle = len(data[u'bids'])
    for i in range(lle):
        price = data[u'bids'][i][u'price']
        amount = data[u'bids'][i][u'amount']
        bids.append(Item(price, amount))
        price = data[u'asks'][i][u'price']
        amount = data[u'asks'][i][u'amount']
        asks.append(Item(price, amount))

    return Depth(bids, bids)
