from django.shortcuts import render
from diagnosis.utils import to_json, with_code
from .models import *


# Create your views here.


@to_json
@with_code
def disease_info(request):
    args = request.GET.dict()
    limit = args.pop('limit', "0")
    page = args.pop('page', "0")
    brief = args.pop('brief', False)
    brief = True if brief == "true" or brief == '1' else False

    if not health_wiki.sub_keys(args.keys()) or not limit.isdigit() or not page.isdigit():
        return 102, "参数格式错误"
    limit = int(limit)
    page = int(page)
    data = health_wiki.get_disease_by(args, limit, page, brief)
    total = len(data)
    pages = total // limit + ((total % limit) > 0) if limit else 1
    return 0, {
        'data': data,
        'pages': pages,
        'total': total
    }


@to_json
@with_code
def search_disease(request):
    args = request.GET.dict()
    limit = args.pop('limit', "0")
    page = args.pop('page', "0")
    brief = args.pop('brief', False)
    brief = True if brief == "true" or brief == '1' else False

    if not health_wiki.sub_keys(args.keys()) or not limit.isdigit() or not page.isdigit():
        return 102, "参数格式错误"
    limit = int(limit)
    page = int(page)
    data = health_wiki.search_by(args, limit, page, brief)
    total = len(data)
    pages = total // limit + ((total % limit) > 0) if limit else 1
    return 0, {
        'data': data,
        'pages': pages,
        'total': total
    }
