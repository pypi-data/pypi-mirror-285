# -*- coding: utf-8 -*-
from .logging_config import logger
from email.mime.text import MIMEText
import smtplib, random, asyncio, threading

def send_email():
    msg = MIMEText('hello, 我是一封测试邮件', 'plain', 'utf-8')
    from_addr = '账户'
    password = '密码'
    to_addr = '958999498@qq.com'
    smtp_server = 'smtp.163.com'
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()
def get_1000():
    # 初始化有向图
    graph = {
        'A': [],
        'B': [],
        'C': [],
        'D': [],
        'E': [],
        'F': [],
        'G': [],
        'H': [],
        'I': [],
        'J': [],
        'K': [],
        'L': [],
        'M': [],
        'N': [],
        'O': [],
        'P': [],
        'Q': [],
        'R': [],
        'S': [],
        'T': [],
        'U': [],
        'V': [],
        'W': [],
        'X': [],
        'Y': [],
        'Z': []
    }

    total_edges = 700
    nodes = list(graph.keys())

    # 添加边，确保每个节点的邻居列表长度总和为1000
    edges_added = 0
    while edges_added < total_edges:
        from_node = random.choice(nodes)
        to_node = random.choice(nodes)
        if from_node != to_node and to_node not in graph[from_node]:
            graph[from_node].append(to_node)
            edges_added += 1

    print(graph)

def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print(f'consumer运行{n}')
        r = '200 ok'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n += 1
        print(f'n的值{n}')
        r = c.send(n)
        print(f'consumer返回值{r}')
    c.close()

async def hello():
    print(f'你好,开始{threading.currentThread()}')
    r = await asyncio.sleep(1)
    print(f'你好,结束{threading.currentThread()}')

async def gather():
    await asyncio.gather(hello(),hello())

def run_email_test():
    try:
        # send_email()
        # get_1000()
        # c = consumer()
        # produce(c)
        asyncio.run(gather())
    except Exception as e:
        logger.exception(e)