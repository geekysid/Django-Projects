from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('', views.index, name='index'),
    path('scorecard', views.scorecard, name='scorecard')
]