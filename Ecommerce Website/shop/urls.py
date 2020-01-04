from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('login', views.login, name='login'),
    path('product', views.product, name='product'),
    path('register', views.register, name='register'),
    path('checkout', views.checkout, name='checkout'),
    path('logout', views.logout, name='logout')
]