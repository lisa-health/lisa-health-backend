from django.shortcuts import render
from .models import FirstAid, Hospital
from diagnosis.utils import to_json, with_code, catch_exception


# Create your views here.
@to_json
@with_code
@catch_exception
def get_aid_tips(request):
    args = request.GET.dict()
    name = args.get('name')
    if not name:
        return 400, "缺少参数"
    func, tips = FirstAid(name).analysis()
    return 0, {"result": {
        "funcs": '\n'.join(func),
        'tips': '\n'.join(tips)
    }}


@to_json
@with_code
# @catch_exception
def get_hospital(request):
    args = request.GET.dict()
    city_spelling = args.get('city_spelling')
    page_num = int(args.get('page_num', '1'))
    search_name = args.get('search_name')
    print(city_spelling, search_name)
    hospital = Hospital(city_spelling, search_name, page_num)
    if city_spelling:
        return 0, {"result": hospital.hospital_by_city_spelling()}
    return 0, {"result": hospital.hospital_by_search_name()}


@to_json
@with_code
@catch_exception
def get_names(request):
    return 0, {
        'result': FirstAid.get_names()
    }