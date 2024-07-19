# -*- coding: utf-8 -*-
# -*- author: Jiangtao -*-

"""Func timer
count func time with decorator

Usage:
    @do_time()
    def do_test():
        sleep(0.01)

    class A(object):
        @do_time(func=False)
        def do_test(self):
            sleep(0.01)
"""


from logging import warning
from functools import wraps
from time import time, sleep


def format_time(spend):
    """format the given time"""
    spend = float(spend)
    if spend < 0:
        raise ValueError('time must > 0')
    elif spend < 1000:
        result = spend, 'ms'
    elif spend < 1000 * 60:
        result = spend / 1000, 's'
    elif spend < 1000 * 60 * 60:
        result = spend / 1000 / 60, 'min'
    elif spend < 1000 * 60 * 60 * 24:
        result = spend / 1000 / 60 / 60, 'h'
    else:
        result = spend / 1000 / 60 / 60 / 24, 'd'
    result = '{:.3f} {}'.format(*result)

    return result


def do_class_time(method):
    """Get the given class function time"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        start_time = time()
        try:
            return method(self, *args, **kwargs)
        finally:
            spend = round(1000 * (time() - start_time), 3)
            warning('方法: {_class}.{func}, 消耗: {spend} ms'.format(
                    _class=self.__class__.__name__, func=method.__name__, spend=spend))

    return wrapper


def do_func_time(method):
    """Get the given function time"""
    @wraps(method)
    def wrapper(*args, **kwargs):
        start_time = time()
        try:
            return method(*args, **kwargs)
        finally:
            spend = round(1000 * (time() - start_time), 3)
            warning('方法: {func}, 消耗: {spend} ms'.format(
                    func=method.__name__, spend=spend))

    return wrapper


def do_time(func=True):
    """Default to get function time
    otherwise if func is False then get the class function time.
    :param func: if the method is a class function or a normal function
    """
    return do_func_time if func else do_class_time


@do_time()
def do_test():
    sleep(0.01)


class A(object):
    @do_time(func=False)
    def do_test(self):
        sleep(0.01)


if __name__ == '__main__':
    do_test()
    a = A()
    a.do_test()


__all__ = ['do_time']
