import requests
import random
import re
from Logger import log
from bs4 import BeautifulSoup
from lxml.html import etree
import time


class HTTPFetcher:
    def __init__(self, ua=None):
        self.useragents = ua if ua is not None else ["Mozilla/5.0"]

    def get_response(self, url, params=None):
        useragent = self.useragents[random.randint(0, len(self.useragents) - 1)]
        header = {
            'User-Agent': useragent,
            'Accept': '*'
        }
        rty_cnt = 0
        while rty_cnt < 5:
            try:
                # rep = requests.head(url, headers=header)
                # if not rep.headers.get('content-type', '').lower().startswith('text/html'):
                #    return ""
                response = requests.get(url, params, headers=header)
                return response
            except Exception as e:
                log.e(e)
                rty_cnt += 1
                time.sleep(5)
        return None

    def get_text(self, url, params=None):
        return self.get_response(url, params).text

    def get(self, url, params=None):
        return self.get_response(url, params).content

    def get_etree(self, url, params=None):
        try:
            return etree.HTML(self.get_text(url, params))
        except Exception:
            return None

    def get_json(self, url, params=None):
        return self.get_response(url, params).json()

    @staticmethod
    def parse_text(text):
        return BeautifulSoup(text, 'lxml').get_text()

    @staticmethod
    def get_host(url):
        pattern = re.compile(r'[a-zA-z]+://([^\s]*?)(/|$)')
        host = pattern.search(url)
        if host is None:
            return None
        return host.group(1).split(':')[0]

    def add_host(self, host_url, url):
        url_pattern = re.compile(r'([a-zA-z]+)://[^\s]*')
        if url_pattern.search(url):
            return url
        host = self.get_host(host_url)
        protocol = url_pattern.search(host_url).group(1)
        return "{}://{}{}{}".format(protocol, host, '' if url.startswith('/') else '/', url)

    def filter_href(self, url, href_filter=None):
        if href_filter is None:
            href_filter = lambda x: True
        content = self.get(url)
        if not content:
            return []
        soup = BeautifulSoup(content, 'html.parser')
        raw_links = [link['href'] for link in soup.find_all('a', href=True)]
        return [link for link in map(lambda l: self.add_host(url, l), raw_links) if href_filter(link)]

    def href_in_same_host(self, url):
        host = self.get_host(url)

        def _filter(link):
            res = self.get_host(link)
            if res is None:
                return False
            return res == host

        return self.filter_href(url, _filter)

    def get_soup(self, url):
        content = self.get_text(url)
        if not content:
            return None
        soup = BeautifulSoup(content, 'html.parser')
        return soup


fetcher = HTTPFetcher()


def get_port(url):
    host = HTTPFetcher.get_host(url).split(':')
    if len(host) > 1:
        return int(host[-1])
    return 80
