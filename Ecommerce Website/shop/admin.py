from django.contrib import admin
from .models import Products, Order, Ordered_Product, Order_Status
# Register your models here.

admin.site.register(Products)
admin.site.register(Order)
admin.site.register(Ordered_Product)
admin.site.register(Order_Status)

