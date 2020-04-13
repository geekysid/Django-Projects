from django.contrib import admin
from .models import *

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'gender', 'email', 'mobile', 'city', 'country','avatar', 'activation_code', 'uin_code', 'is_active')
    list_filter = ('name', 'gender', 'email', 'mobile', 'city', 'country', 'is_active')
    ordering = ('user', 'name', 'gender', 'email', 'mobile', 'city', 'country',)
    search_fields = ('name', 'gender', 'email', 'mobile', 'city', 'country', 'is_active', 'uin_code')


class PasswordRecoveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'email', 'generated_on', 'expired_on')
    list_filter = ('user', 'email')
    ordering = ('user', 'email', 'generated_on', 'expired_on')
    search_fields = ('user', 'email', 'token')


class ErrorCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'Type', 'hash_code', 'title', 'message')
    list_filter = ('code', 'Type', 'hash_code', 'title')
    ordering = ('code', 'hash_code', 'title')
    search_fields = ('code', 'Type', 'hash_code', 'title', 'message')


# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(PasswordRecovery, PasswordRecoveryAdmin)
admin.site.register(ErrorCode, ErrorCodeAdmin)
