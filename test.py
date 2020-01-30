import sys
import os

sys.path.extend(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DiseasePedia'))
from DiseasePedia.netease import NetEaseHealth, NetEaseHealthScraper
from DiseasePedia import csv as cv
import json


def main():
    h = NetEaseHealthScraper()
    dep = h.get_departments()
    print(json.dumps(dep, indent=2, ensure_ascii=False))
    ls = h.work_by_chain()
    # st = json.dumps(ls, indent=2, ensure_ascii=False)
    # print(st)


if __name__ == '__main__':
    main()
