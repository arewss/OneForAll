# coding=utf-8
import random
import time

from common.search import Search


class Exalead(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = "ExaleadSearch"
        self.addr = "http://www.exalead.com/search/web/results/"
        self.per_page_num = 30

    def search(self, domain, filtered_subdomain='', full_search=False):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        :param bool full_search: 全量搜索
        """
        self.page_num = 0
        while True:
            self.delay = random.randint(1, 5)
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            query = 'site:' + domain + filtered_subdomain
            params = {'q': query, 'elements_per_page': '30', "start_index": self.page_num}
            resp = self.get(url=self.addr, params=params)
            if not resp:
                return
            subdomain_find = self.match(domain, resp.text)
            if not subdomain_find:
                break
            if not full_search:
                if subdomain_find.issubset(self.subdomains):
                    break
            self.subdomains = self.subdomains.union(subdomain_find)
            self.page_num += self.per_page_num
            if self.page_num > 1999:
                break
            if 'title="Go to the next page"' not in resp.text:
                break

    def run(self):
        """
        类执行入口
        """
        self.begin()

        self.search(self.domain, full_search=True)

        # 排除同一子域搜索结果过多的子域以发现新的子域
        for statement in self.filter(self.domain, self.subdomains):
            statement = statement.replace('-site', 'and -site')
            self.search(self.domain, filtered_subdomain=statement)

        # 递归搜索下一层的子域
        if self.recursive_search:
            for layer_num in range(1, self.recursive_times):  # 从1开始是之前已经做过1层子域搜索了,当前实际递归层数是layer+1
                for subdomain in self.subdomains:
                    if subdomain.count('.') - self.domain.count('.') == layer_num:  # 进行下一层子域搜索的限制条件
                        self.search(subdomain)

        self.save_json()
        self.gen_result()
        self.save_db()

        self.finish()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    search = Exalead(domain)
    search.run()


if __name__ == '__main__':
    do('example.com')
