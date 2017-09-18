# coding=utf-8
import logging


def get_logger(log_name, level=logging.INFO):
    """
    日志的疯转
    :param level: 日志级别
    :param log_name: 日志对象名
    :return: 日志对象名
    """
    logger = logging.getLogger(log_name)

    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler("%s.log" % log_name)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
