from django.urls import path

from . import views


app_name = 'freetrialtransfer'
urlpatterns = [
    path('', views.form, name='form'),
    path('thanks', views.thanks, name='thanks')
]
