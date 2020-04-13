from django.contrib import admin
from .models import UserProfile, PasswordRecovery


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'gender', 'email', 'mobile', 'city', 'country','avatar', 'activation_code', 'is_active')
    list_filter = ('name', 'gender', 'email', 'mobile', 'city', 'country', 'is_active')
    ordering = ('user', 'name', 'gender', 'email', 'mobile', 'city', 'country',)
    search_fields = ('name', 'gender', 'email', 'mobile', 'city', 'country', 'is_active')

class PasswordRecoveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'email', 'generated_on', 'expired_on')
    list_filter = ('user', 'email')
    ordering = ('user', 'email', 'generated_on', 'expired_on')
    search_fields = ('user', 'email', 'token')


# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(PasswordRecovery, PasswordRecoveryAdmin)



   