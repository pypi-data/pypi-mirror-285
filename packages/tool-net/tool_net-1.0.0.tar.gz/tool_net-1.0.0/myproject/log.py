# -*- coding: utf-8 -*-
# coding = utf-8
def log(func):
    def wrapper(*args, **kw):
        print('调用方法：(%s)' % func.__name__)
        return func(*args, **kw)
    return wrapper