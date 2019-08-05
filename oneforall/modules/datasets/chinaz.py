# coding=utf-8
import time

from common.query import Query


class Chinaz(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'ChinazQuery'
        self.addr = 'https://alexa.chinaz.com/'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        time.sleep(self.delay)
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        self.addr = self.addr + self.domain
        resp = self.get(self.addr)
        if not resp:
            return
        subdomains_find = self.match(self.domain, resp.text)
        self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.query()
        self.save_json()
        self.gen_result()
        self.save_db()
        self.finish()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = Chinaz(domain)
    query.run()


if __name__ == '__main__':

    do('example.com')
