from django.db import models

# Create your models here.
import requests
from lxml.html import etree
import json
from urllib import parse


class FirstAid:
    def __init__(self, name):
        self.name = name

    @classmethod
    def get_names(cls):
        url = 'https://www.zk120.com/zs/jj/'
        res = requests.get(url).text
        names = etree.HTML(res).xpath('//li//a/div/text()')  # type:list
        return names

    def get_spider_url(self):
        names = self.get_names()
        spider_url = 'https://www.zk120.com/zs/jj/emergency/' + str(names.index(self.name) + 1) + '.html'
        return spider_url

    def spider(self):
        url = self.get_spider_url()
        res = requests.get(url).text
        return etree.HTML(res)

    def analysis(self):
        tree = self.spider()
        funcs = tree.xpath('//section[1]//p[@class="font_3"]/text()')
        tips = tree.xpath('//section[2]//p[@class="font_3"]/text()')
        return funcs, tips


class Hospital:
    def __init__(self, city_spelling='', search_name='', page_num=1):
        self.page_num = page_num
        self.city_spelling = city_spelling
        if search_name:
            self.search_name = parse.quote(search_name, encoding='gbk')

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.139 Safari/537.36',
        }

    def hospital_by_city_spelling(self):
        """
        根据城市拼写返回结果
        :return:
        """
        url = 'http://wapyyk.39.net/{}/hospitals//c_p{}.json'.format(
            self.city_spelling, self.page_num
        )
        res = requests.get(url, headers=self.headers).json()
        # print(res)
        return res

    def hospital_by_search_name(self):
        """
        根据搜索词返回结果
        :return:
        """
        url = 'http://wapyyk.39.net/hospitalsByPage.json?name={}&pageNo={}'.format(
            self.search_name, self.page_num
        )
        res = requests.get(url, headers=self.headers).json()
        # print(res)
        return res
