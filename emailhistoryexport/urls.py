from django.urls import path

from . import views


app_name = 'emailhistoryexport'
urlpatterns = [
    path('', views.form, name='form'),
]
