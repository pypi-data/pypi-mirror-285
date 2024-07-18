from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from api.models import user_info, config
from django.middleware.csrf import get_token
import json
# Create your views here.

def save_data(request):
    if request.method == 'POST':
        try:
            # Content-Type: application/json 时或者表头数据的方法
            json_data = request.body.decode('utf-8')
            data = json.loads(json_data)
            user_info.objects.create(**data)
            result = {"status": 'ok'}
        except UnicodeDecodeError:
            result = {"status": 'error', "msg": 'Invalid request data'}
        return JsonResponse(result)

def get_data(request):
    if request.method == 'GET':
        data_list = user_info.objects.all()
        serialized_data = serializers.serialize('json', data_list)
        deserialized_data = list(serializers.deserialize('json', serialized_data))
        data = [{'name': item.object.name, 'age': item.object.age} for item in deserialized_data]
        return JsonResponse(data, safe=False)

# 前端的接口的请求头中必须包含csrd
def get_csrf_token(request):
    token = get_token(request)
    response = HttpResponse(token)
    response['X-CSRFToken'] = token
    return response

# fetch获取get方法
def get_list(request):
    result = {"status": 'ok'}
    keys = ['a','b','c']
    new_dict = dict.fromkeys(keys)
    return JsonResponse(result)