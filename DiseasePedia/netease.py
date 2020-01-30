from .HTTPFetcher import HTTPFetcher
from .MongoDBSaver import MongoDBSaver
from diagnosis.utils import edit_dist
from DiseasePedia.utils import *
from DiseasePedia.paragraph import ParagraphSplit


def _begin(it):
    for i in it:
        return i


class NetEaseHealthScraper:
    def __init__(self):
        self.db = MongoDBSaver(db_name='netease', collection_name='healthPedia')
        self.fetcher = HTTPFetcher([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'])

    def get_departments(self):
        url = 'http://shiyong.jiankang.163.com/user/disease/api_k_list.html'
        result = self.fetcher.get_json(url).get('data')
        res = {}
        for cls in result:
            if cls['level'] == 1:
                res[cls['id']] = dict(sub=[], **cls)
            else:
                res[cls['parent_id']]['sub'].append(cls)
        return list(res.values())

    def get_department_of(self, first_id=None, second_id=None):
        url = 'http://shiyong.jiankang.163.com/user/disease/list.html'
        result = self.fetcher.get_json(url, {
            'f_id': first_id or '',
            's_id': second_id or '',
            'size': 23333
        }).get('data').get('list')  # type: list[dict]
        return [{
            'id': disease.get('id'),
            'name': disease.get('name'),
            'symptoms': [i.strip() for i in disease.get('symptoms').split('|') if len(i.strip())],
            'tSymptoms': [i for i in disease.get('tSymptoms').split('、') if len(i)],
            'introduction': disease.get('introduce')
        } for disease in result]

    def get_disease(self, did):
        url = 'http://shiyong.jiankang.163.com/user/disease/api_detail_end.html'
        result = self.fetcher.get_json(url, {
            'id': did
        }).get('data')  # type: dict
        for k, v in result.items():
            if isinstance(v, str):
                result[k] = self.fetcher.parse_text(v)
        interests = ["id", "name", "introduce", "symptom", "cause", "prevention", "inspect", "content", "nursing",
                     "complication"]
        return {k: result[k] for k in interests}

    def get_disease_of_department(self, did, first_dep, second_dep):
        return dict(self.get_disease(did), firstDepartment=first_dep, secondDepartment=second_dep)

    def work_by_chain(self, offset=0):
        departments = self.get_departments()
        for dep in departments[offset:]:
            primary = dep.get('name')
            fid = dep.get('id')
            print("Primary department:", primary)
            diseases = self.get_department_of(fid)
            print("Major diseases get.")
            for disease in diseases:
                print("\t\t|>Getting:", disease.get('name'))
                final = dict(self.get_disease_of_department(disease.get('id'), primary, primary), **disease)
                self.db.insert(final)
            for sub in dep.get('sub'):
                second = sub.get('name')
                print("\t>Secondary:", second)
                idx = sub.get('id')
                diseases = self.get_department_of(fid, idx)
                for disease in diseases:
                    disease_id = disease.get('id')
                    if self.db.find({'id': disease_id}).count():
                        self.db.collection.update({'id': disease_id}, {'$set': {'secondDepartment': second}})
                        continue
                    final = dict(self.get_disease_of_department(disease.get('id'), primary, second), **disease)
                    self.db.insert(final)


class NetEaseHealth:
    def __init__(self):
        self.db = MongoDBSaver(db_name='netease', collection_name='healthPedia')
        self.keys = list(_begin(self.db.find({}, {"_id": 0})).keys())
        self.brief_keys = ["id", "name"]  # , "introduce", "symptom", "tSymptoms"]
        self.brief_filter = {k: 1 for k in self.brief_keys}

    process_chain = map_list(apply_func_to_keys(
        ['content', 'nursing', 'symptom', 'complication', 'inspect', 'introduce', 'introduction', 'prevention',
         'cause'], ParagraphSplit.try_indent))

    process_chain = lambda fn: fn

    @process_chain
    def get_disease_by(self, cond, limit=0, page=1, brief=False):
        if page < 1:
            page = 1
        show_filter = self.brief_filter if brief else {}
        res = self.db.find_dumps_safe(cond, show_filter).limit(limit).skip(limit * page - limit)
        return list(res)

    @process_chain
    def search_by(self, cond, limit=1, page=1, brief=False):
        page = max(1, page)
        show_filter = self.brief_filter if brief else {}
        return list(self.db.find_dumps_safe({k: {"$regex": v} for k, v in cond.items()}, show_filter).limit(limit).skip(
            limit * page - limit))

    def best_relate(self, by, val):
        result = self.search_by({by: val})
        if not result:
            return None
        return min(result, key=lambda x: edit_dist(val, x.get(by)) / len(val))

    def sub_keys(self, ks):
        return all(k in self.keys for k in ks)
