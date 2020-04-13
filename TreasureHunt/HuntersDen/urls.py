from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('', views.index, name='index'),
    re_path(r'^den/[a-zA-Z0-9]{2,10}$', views.den, name='den'),
]