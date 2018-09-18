from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def slack(request):
    print(request)
