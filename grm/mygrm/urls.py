from django.http import request
from django.urls import path

from . import views

app_name = 'mygrm'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('showdata/', views.show_data, name='show_data'),

]

