# coding=utf-8


class Ticker(object):
    def __init__(self, buy, sell, last):
        super(Ticker, self).__init__()
        self.buy = buy
        self.sell = sell
        self.last = last


def dict_to_ticker(d):
    """
    通过json.loads来转化成对象
    json.loads(json.dumps(d), object_hook=dict_to_ticker)
    """
    return Ticker(d['buy'], d['sell'], d['last'])
