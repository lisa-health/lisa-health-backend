import csv
from .netease import NetEaseHealthScraper, NetEaseHealth


def _first(iter):
    for i in iter:
        return i


def enum_edit_dist(xs, dis):
    if not dis:
        yield xs
    for i in range(len(xs)):
        for back in enum_edit_dist(xs[i + 1:], dis - 1):
            yield xs[:i] + back


def all_edist_leq(xs, dis):
    for i in range(1 + dis):
        yield from enum_edit_dist(xs, i)


def save_to(fp):
    ne = NetEaseHealthScraper()
    data = ne.db.find()
    with open(fp, 'w', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=[x for x in _first(ne.db.find()).keys() if x != '_id'])
        w.writeheader()
        for dat in data:
            dat.pop('_id')
            w.writerow(dat)


def save_analyse_to(fp):
    ne = NetEaseHealth()
    data = ne.get_disease_by({}, brief=True)
    fields = ['name', 'symptom', 'tSymptoms']
    with open(fp, 'w', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for dat in data:
            dat = {
                k: dat[k] for k in fields
            }
            t_symptoms = dat['tSymptoms']
            for perm in all_edist_leq(t_symptoms, 2):
                w.writerow(dict(dat, tSymptoms=perm))
