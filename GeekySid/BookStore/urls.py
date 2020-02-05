from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('product', views.product, name='product'),
    path('checkout', views.checkout, name='checkout'),
    path('orders', views.orders, name='orders')
]