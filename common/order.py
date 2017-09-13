# coding=utf-8
from common import constant


class Order(object):
    """
    {
        u'order_id': resp[u'id'],
        u'price': resp[u'price'],
        u'status': order_status,
        u'type': resp[u'type'],
        u'amount': origin_amount,
        u'deal_amount': executed_amount,
        u'was_forced': resp[u'was_forced']
    }
    price Decimal
    amount Decimal
    deal_amount Decimal

    """

    def __init__(self, order_id, price, status, order_type, amount, deal_amount):
        super(Order, self).__init__()
        self.order_id = order_id
        self.price = price
        self.status = status
        self.order_type = order_type
        self.amount = amount
        self.deal_amount = deal_amount
        print('init========>' + str(type(status)) + '----value: ' + str(status))

    def __repr__(self):
        data = {
            u'order_id': self.order_id,
            u'price': self.price,
            u'status': self.status,
            u'order_type': self.order_type,
            u'amount': self.amount,
            u'deal_amount': self.deal_amount,
        }
        return str(data)

    def __str__(self):
        data = {
            u'order_id': self.order_id,
            u'price': self.price,
            u'status': self.status,
            u'order_type': self.order_type,
            u'amount': self.amount,
            u'deal_amount': self.deal_amount,
        }
        return str(data)

    def is_closed(self):
        return self.status == constant.ORDER_STATE_CLOSED

    def is_canceled(self):
        return self.status == constant.ORDER_STATE_CANCELED


class OrderResult(object):
    """
    liqui:
        fail==>
            {u'code': 832, u'success': 0, u'error': u'Not enougth LTC to create sell order.'}
            {u'code': 831, u'success': 0, u'error': u'Not enougth BTC to create buy order.'}
        success=>
            {u'success': 1, u'return': {u'order_id: xxx}}
    """

    def __init__(self, order_id=None, code=None, error=None):
        super(OrderResult, self).__init__()
        self.order_id = order_id
        self.code = code
        self.error = error


def get_status(ex_name, origin_status):
    """
    根据交易所的订单状态进行转换
    """
    if ex_name == constant.EX_OKEX:
        return convert_ok_status(origin_status)
    if ex_name == constant.EX_BFX:
        return origin_status
    if ex_name == constant.EX_LQ:
        return convert_lq_status(origin_status)


def convert_ok_status(status):
    if status == 2:
        return constant.ORDER_STATE_CLOSED
    if (status == 0) or (status == 1) or (status == 4):
        return constant.ORDER_STATE_PENDING
    if status == -1:
        return constant.ORDER_STATE_CANCELED

    raise ValueError('okex 未知的status')


def convert_lq_status(status):
    if status == 1:
        return constant.ORDER_STATE_CLOSED
    if status == 0:
        return constant.ORDER_STATE_PENDING
    if (status == 2) or (status == 3):
        # 3 canceled buy partially executed.
        return constant.ORDER_STATE_CANCELED

    raise ValueError('liqui 未知的status')
