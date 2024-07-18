import os
from collections.abc import Iterator
from myproject.log import log
from .logging_config import logger
import pdb
import pickle
import json

def getUseInfo():
    list = [d for d in os.listdir('.')]
    for item in list:
        print(item)

def test():
    L = ['Hello',12,'World']
    NL = [x.lower() if isinstance(x, str) else x for x in L]
    print(NL)

def fib(max):
    n, a, b = 0, 0, 1
    while n < max:
        yield b
        a, b = b, a + b
        n += 1
    return 'done'

def sortFuc():
    # pdb.set_trace()
    L = [('Bob', 75), ('Adam', 92), ('Bart', 66), ('Lisa', 88)]
    sorted(L, key=lambda x: x[1], reverse=True)

@log
def inc():
    x = 0
    def fn():
        # 仅读取x的值:
        return x + 1
    return fn

def studentDict(std):
    return {
        'name': std.name,
        'age': std.age,
        'score': std.score
    }

class Student(object):
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

def run_file():
    try:
        # getUseInfo()
        # test()
        # for item in fib(8):
        # print(item)
        # f = inc()
        # print(f.__name__)
        # print(f())
        # print(f())
        # sortFuc()
        # with open('../requirements.txt', 'r', encoding='utf-16', errors='ignore') as f:
        #     print(f.read())
        # with open('./test/dump.txt', 'ab+') as w:
        #     # w.write('我是写入的数据\n')
        #     d = dict(name='job', age=20)
        #     pickle.dump(d, w)
        s = Student('bob', 12, 99)
        # print(s.__dict__)
        print(json.dumps(s, default=lambda obj: obj.__dict__))
    except Exception as e:
        logger.exception(e)

