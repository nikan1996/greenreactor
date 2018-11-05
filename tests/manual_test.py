#!/usr/bin/env python
# encoding: utf-8
"""

@author:nikan(859905874@qq.com)🎂

@file: manual_test.py

@time: 2018/11/5 下午1:35
"""
import gevent
import gevent.monkey

"""
Patch 的必要性：
DNS 解析： 使用 gevent 的 getaddrinfo

"""
# gevent.monkey.patch_all()

import requests

import greenreactor
greenreactor.install()



from twisted.internet import reactor

from twisted.web.client import Agent
from twisted.web.http_headers import Headers

agent = Agent(reactor)


def get(url):
    print("request.get")
    # r = requests.get(
    #     'http://wzkj.wenzhou.gov.cn/module/download/downfile.jsp?classid=0&filename=574e4bb2e4584f57bc35692b0a36e38d.pdf')
    r = requests.get(url)
    print(r.text[:10])
    print('response receive with requests')


def request_with_requests():
    print("requests")
    r = gevent.spawn(get, "http://example.com/")
    print('requests end')


def cbResponse(ignored):
    print('Response received with agent')


def request_with_agent():
    print("agent")
    url = b"http://example.com/"
    d = agent.request(b'GET', url, Headers({b'User-Agent': [b'Twisted Web Client Example']}), None)
    d.addCallback(cbResponse)

    d.addBoth(cbShutdown)


def cbShutdown(ignored):
    reactor.stop()


if __name__ == '__main__':
    for i in range(1):
        request_with_agent()
        request_with_requests()
    reactor.run()

