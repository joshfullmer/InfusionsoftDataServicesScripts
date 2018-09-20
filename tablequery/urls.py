from django.urls import path

from . import views


app_name = 'tablequery'
urlpatterns = [
    path('', views.query, name='query'),
]
