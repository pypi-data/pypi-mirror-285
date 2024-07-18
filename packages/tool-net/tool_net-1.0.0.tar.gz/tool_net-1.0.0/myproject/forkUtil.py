# -*- coding: utf-8 -*-
from multiprocessing import Process, Pool, Queue
from .logging_config import logger
import os, time, random, threading, argparse, itertools, hashlib, hmac
from collections import Counter
from urllib import request, parse
from html.parser import HTMLParser
from html.entities import name2codepoint

local_school = threading.local()
def run_proc(name):
    print(f'运行的子进程{name}, 父进程{os.getpid()}')

def long_time_task(name):
    print(f'运行的进程{name}, 父进程{os.getpid()}')
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print(f'开始时间{start}, - 结束时间{end}, {name}运行%0.2f 秒' % (end-start))

def write(q):
    print(f'运行进程id{os.getpid()}')
    for value in ['A', 'B', 'C']:
        q.put(value)
        time.sleep(random.random())

def read(q):
    print(f'运行进程id{os.getpid()}')
    while True:
        value = q.get(True)
        print(f'获取到的value值{value}')

# 线程创建
def loop():
    print(f'运行的线程{threading.current_thread().name}')
    n = 0
    while n < 5:
        n += 1
        print(f'线程{threading.current_thread().name}, n是{n}')
        time.sleep(1)

# 危险操作会爆线程
def danger_warn():
    x = 0
    print(f'pid:{os.getpid()}')
    while True:
        x += 1

def process_student():
    std = local_school.student
    print(f'你好，我是{std}, {threading.current_thread().name}')

def process_thread(name):
    local_school.student = name
    process_student()

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user')
    parser.add_argument('-c', '--color')
    namespace = parser.parse_args()
    command_line_args = { k: v for k, v in vars(namespace).items() if v }
    print(command_line_args)

def get_counter():
    c = Counter()
    for ch in 'pradaradnaksidnaniwjeniqwen':
        c[ch] += 1
    print(c)
    c.update('qweasdifauwejwqe')
    print(c)

def get_cmd():
    parser = argparse.ArgumentParser(
        prog='backup',
        description='tjd',
        epilog='@2024'
    )
    parser.add_argument('outfile')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--prot', default='3306', type=int)
    parser.add_argument('-u', '--user', required=True)
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('-gz', '--gzcompress', required=False, action='store_true', help='是否压缩备份文件')
    args = parser.parse_args()
    command_line_args = {k: v for k, v in vars(args).items()}
    print(command_line_args)

def get_md5():
    md5 = hashlib.md5()
    md5.update('我是摘要的内容'.encode('utf-8'))
    print(md5.hexdigest())

def get_sha1():
    sha1 = hashlib.sha1()
    sha1.update('我是摘要的内容'.encode('utf-8'))
    print(sha1.hexdigest())

def get_hmac():
    msg = '我是需要加密的内容'
    key = b'qwer'
    msg_bytes = msg.encode()
    h = hmac.new(key, msg_bytes, digestmod='MD5')
    print(h.hexdigest())

def get_itertools():
    natuals = itertools.count(1)
    ns = itertools.takewhile(lambda x: x <= 10, natuals)
    print(list(ns))
    cs = itertools.repeat('ABC', 3)
    for c in cs:
        print(c)
    for a in itertools.chain('abc', 'xyz'):
        print(a)
    for key, group in itertools.groupby('AaaBCBDANFaOJAUDBUWIDB', lambda x: x.upper()):
        print(key, list(group))

def get_test():
    with request.urlopen('http://192.168.7.192:18201') as f:
        data = f.read()
        for k, v in f.getheaders():
            print(f'{k}: {v}')
        print('data', data.decode('utf-8'))
def get_request():
    req = request.Request('http://192.168.7.192:18201/api/system/up/list')
    # req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
    with request.urlopen(req) as f:
        for k, v in f.getheaders():
            print(f'{k}: {v}')
        response_content = f.read().decode('utf-8')
        print(response_content)
def post_request():
    req_url = 'http://192.168.7.192:18201/api/auth/sso-server/doLogin'
    password = 'QYxipR+j3zP06uC1mdkO8sn1NeqTf+Il4VTB+oBT76Q='
    username = 'QyZy0MikLfQBMO4otWtsxA=='
    login_data = parse.urlencode({
        'username': username,
        'password': password
    }).encode('utf-8')

    req = request.Request(req_url, data=login_data, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        with request.urlopen(req) as f:
            response_content = f.read().decode('utf-8')
            print(response_content)
    except request.HTTPError as e:
        print(f'HTTPError: {e.code} {e.reason}')
    except request.URLError as e:
        print(f'URLError: {e.reason}')
    except Exception as e:
        print(f'Error: {e}')

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        print('<%s>----' % tag)

    def handle_endtag(self, tag):
        print('</%s>!!!!!' % tag)

    def handle_startendtag(self, tag, attrs):
        print('<%s/>' % tag)

    def handle_data(self, data):
        print(data)

    def handle_comment(self, data):
        print('<!--', data, '-->')

    def handle_entityref(self, name):
        print('&%s;' % name)

    def handle_charref(self, name):
        print('&#%s;' % name)


def run_util():
    # get_cmd()
    try:
        # p = Process(target=run_proc, args=('der',))
        # p.start()
        # p.join()
        #######
        # p = Pool(5)
        # for i in range(5):
        #     p.apply_async(long_time_task, args=(i,))
        # p.close()
        # p.join()
        #######
        # q = Queue()
        # pw = Process(target=write, args=(q,))
        # pr = Process(target=read, args=(q,))
        # pw.start()
        # pr.start()
        # pw.join()
        # pr.terminate()
        ##########
        # print('运行的线程 %s ' % threading.current_thread().name)
        # t = threading.Thread(target=loop, name='LoopThread')
        # t.start()
        # t.join()
        # print('结束的线程 %s ' % threading.current_thread().name)
        #######
        # for i in range(multiprocessing.cpu_count()):
        #     t = threading.Thread(target=danger_warn)
        #     t.start()
        #######
        # for i in range(multiprocessing.cpu_count()):
        #     t = multiprocessing.Process(target=danger_warn)
        #     t.start()
        #######
        # t1 = threading.Thread(target=process_thread, args=('job',), name="one")
        # t2 = threading.Thread(target=process_thread, args=('bou',), name="two")
        # t1.start()
        # t2.start()
        # t1.join()
        # t2.join()
        # get_parser()
        # get_counter()
        # get_md5()
        # get_sha1()
        # get_hmac()
        # get_itertools()
        # get_test()
        # get_request()
        # post_request()
        # parser = MyHTMLParser()
        # parser.feed('''<html>
        # <head></head>
        # <body>
        # <!-- test html parser -->
        #     <p>Some <a href=\"#\">html</a> HTML&nbsp;tutorial...<br>END</p>
        # </body></html>''')
        pass
    except Exception as e:
        logger.exception(e)