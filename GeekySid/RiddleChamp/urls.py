from django.urls import path, include, re_path
from . import views

urlpatterns = [
    re_path(r'^index[/]{0,1}$', views.index, name='index'),
    path('', views.index, name='index'),
    re_path(r'^index/[se]/[a-z0-9]{1,10}$', views.index, name='index'),
    re_path(r'^den/[a-zA-Z0-9]{2,10}$', views.den, name='den'),
    re_path(r'^den/[a-zA-Z0-9]{2,10}/[se]/[a-z0-9]{1,10}$', views.den, name='den'),
    path('den/join/', views.joinDen, name='join'),
    re_path(r'^den/riddle/[a-zA-Z0-9]{2,10}', views.denRiddle, name='riddle'),
    path('den/riddle/user_response_handler', views.user_response_handler, name='user_response_handler'),
    path('den/sent_den_invites', views.sent_den_invites, name='sent_den_invites'),
    path('den/invite/guest', views.accept_den_invite, name='invite'),
    path('den/new/', views.denCreate, name='newDen')
]