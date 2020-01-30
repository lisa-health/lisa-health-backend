from django.shortcuts import render
from .utils import to_json, with_code
from .machine.predict import predictor
from .models import health_wiki


# Create your views here.


# 根据输入的症状描述
# 返回预测的疾病名称
@to_json
@with_code
def predict(request):
    symptom = request.GET.get('symptom')
    if not symptom:
        return 101, "症状未给出。"
    predict_result = predictor.predict(symptom)
    final_result = []
    for disease in predict_result:
        res = health_wiki.best_relate('name', disease.get('name'))
        if res:
            final_result.append(
                dict(disease, alterName=res.get('name'), relateSymptoms=res.get('tSymptoms'),
                     detailSymptom=res.get('symptom')[:70] + "..."))
    if final_result:
        return 0, {
            'disease': final_result
        }
    else:
        return 201, '症状描述不够详细。'


# 根据输入的疾病名称，返回和该疾病最相关的症状及其相关性
@to_json
@with_code
def relate(request):
    disease = request.GET.get('disease')
    if not disease:
        return 101, '疾病未给出'

    result = predictor.relate(disease)
    if result:
        return 0, {
            'symptom': [{
                'name': symptom,
                'probability': round(likelihood, 2)
            } for symptom, likelihood in result]
        }
    return 202, '疾病描述错误。'
