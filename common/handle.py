# coding=utf-8
from common import constant


def get_status(ex_name, origin_status):
    """
    根据交易所的订单状态进行转换
    """
    if ex_name == constant.EX_OKEX:
        return convert_ok_status(origin_status)
    if ex_name == constant.EX_BFX:
        return origin_status


def convert_ok_status(status):
    if status == 2:
        return constant.ORDER_STATE_CLOSED
    if (status == 0) or (status == 1) or (status == 4):
        return constant.ORDER_STATE_PENDING
    if status == -1:
        return constant.ORDER_STATE_CANCELED

    raise ValueError('okex 未知的status')
