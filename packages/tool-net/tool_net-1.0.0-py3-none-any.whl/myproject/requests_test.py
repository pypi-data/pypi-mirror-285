# -*- coding: utf-8 -*-
from .logging_config import logger
import requests, chardet, psutil, socket

def get_request():
    params = {'q': 1, 'p': 2}
    r = requests.get('http://192.168.7.192:18201/api/system/up/list', params=params)
    print(r.json())
    print(r.encoding)
def chardet_text():
    str = '最新の主要ニュース'.encode('euc-jp')
    print(chardet.detect(str))

def cpu_info():
    print(f'cpu逻辑数{psutil.cpu_count()}')
    print(f'cpu物理核心{psutil.cpu_count(logical=False)}')
    print(f'cpu空闲时间{psutil.cpu_times()}')
    for item in range(10):
        print(f'cpu使用率{psutil.cpu_percent(interval=1, percpu=True)}')
def storage_info():
    print(f'虚拟内存使用情况{psutil.virtual_memory()}')
    print(f'交换内存使用情况{psutil.swap_memory()}')
def disk_info():
    print(f'磁盘分区情况{psutil.disk_partitions()}')
    print(f'磁盘使用情况{psutil.disk_usage("/")}')
    print(f'磁盘IO{psutil.disk_io_counters()}')

def net_info():
    print(f'网络情况{psutil.net_io_counters()}')
    print(f'进程情况{psutil.pids()}')
    if 223 in psutil.pids():
        print('包含')
    else:
        print('不包含')
    p = psutil.Process(744)
    print(p.exe())
    print(psutil.test())

def socket_link():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('www.baidu.com', 80))
    s.send(b'GET / HTTP/1.1\r\nHost: www.baidu.com\r\nConnection: close\r\n\r\n')

def run_requests_test():
    try:
        # get_request()
        # chardet_text()
        # cpu_info()
        # storage_info()
        # disk_info()
        # net_info()
        socket_link()
    except Exception as e:
        logger.exception(e)