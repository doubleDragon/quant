from decimal import Decimal


class Account(list):
    """
    [
        {
            Item
        }
        ...
    ]
    an item list
    """

    def __init__(self):
        super(Account, self).__init__()

    def __str__(self):
        return super(Account, self).__str__()

    def __repr__(self):
        return super(Account, self).__repr__()


class Item(object):
    """
    {
    'balance': 0,
    'available_balance': 0,
    'frozen_balance': 0,
    }
    type Decimal
    """

    def __init__(self, currency, balance, available_balance=Decimal('0'), frozen_balance=Decimal('0')):
        super(Item, self).__init__()
        self.currency = currency
        self.balance = balance
        self.available_balance = available_balance
        self.frozen_balance = frozen_balance

    def __str__(self):
        data = {
            u'currency': self.currency,
            u'balance': self.balance,
            u'available_balance': self.available_balance,
            u'frozen_balance': self.frozen_balance,
        }
        return str(data)

    def __repr__(self):
        data = {
            u'currency': self.currency,
            u'balance': self.balance,
            u'available_balance': self.available_balance,
            u'frozen_balance': self.frozen_balance,
        }
        return str(data)


if __name__ == '__main__':
    item = Item('btc', 10, 11, 12)
    print(item)
    ac = Account()
    ac.append(item)
    print(ac)
