from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    return render(request, 'home.html')


@csrf_exempt
def slack(request):
    body = json.loads(request.body)
    print(body)
    response_data = {}
    response_data['text'] = 'Walk up successfully recorded'
    return HttpResponse(
        json.dumps(response_data),
        content_type='application/json')
