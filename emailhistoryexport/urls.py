from django.urls import path

from . import views


app_name = 'emailhistoryexport'
urlpatterns = [
    path('<instance_name>', views.instance_form, name='instance_form'),
    path('', views.form, name='form'),
]
