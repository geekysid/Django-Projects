from django.urls import path, include, re_path
from . import views

urlpatterns = [
    re_path(r'^login[/]{0,1}$', views.login, name='login'),
    re_path(r'^logout[/]{0,1}$', views.logout, name='logout'),
    re_path(r'^register[/]{0,1}$', views.register, name='register'),
    re_path(r'^profile[/]{0,1}$', views.profile, name='profile'),
    re_path(r'^reset_password[/]{0,1}$', views.reset_password, name='reset_password'),
    re_path(r'^forgotpassword[/]{0,1}$', views.forgot_password, name='forgotpassword'),
    re_path(r'^login/[0-9]{3}$', views.login, name='login'),
    re_path(r'^login/[se]/[a-z0-9]{1,10}$', views.login, name='login'),
    re_path(r'^register/[se]/[a-z0-9]{1,10}$', views.register, name='register'),
    path('username_validity', views.username_validity, name='username_validity'),
    path('email_validity', views.email_validity, name='email_validity'),
    path('user_registration', views.user_registration, name='user_registration'),
    path('user_login', views.user_login, name='user_login'),
    path('account_activate', views.account_activate, name='account_activate'),
    path('resent_activation_mail', views.resent_activation_mail, name='resent_activation_mail'),
    path('forgotpassword', views.forgot_password, name='forgotpassword'),
    path('forgot_password_link', views.forgot_password_link, name='forgot_password_link'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('set_new_password', views.set_new_password, name='set_new_password'),
    path('profile_update', views.profile_update, name='profile_update')
]