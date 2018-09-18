from django.http import HttpResponse
from django.utils.http import unquote
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    return render(request, 'home.html')


@csrf_exempt
def slack(request):
    print(request.body)
    body_decoded = request.body.decode('utf-8')
    print(body_decoded)
    parsed_response = {}
    for keyvalue in body_decoded.split('&'):
        key, value = keyvalue.split('=')
        parsed_response[key] = unquote(value)
    print(parsed_response)
    response_data = {}
    response_data['text'] = 'Walk up successfully recorded'
    return HttpResponse(
        json.dumps(response_data),
        content_type='application/json')
