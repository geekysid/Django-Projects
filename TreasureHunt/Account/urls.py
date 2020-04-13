from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('username_validity', views.username_validity, name='username_validity'),
    path('email_validity', views.email_validity, name='email_validity'),
    path('user_registration', views.user_registration, name='user_registration'),
    path('user_login', views.user_login, name='user_login'),
    path('account_activate', views.account_activate, name='account_activate'),
    path('resent_activation_mail', views.resent_activation_mail, name='resent_activation_mail'),
    path('forgotpassword', views.forgot_password, name='forgot_password'),
    path('forgot_password_link', views.forgot_password_link, name='forgot_password_link'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('reset_password_call', views.reset_password_call, name='reset_password_call')
    # path('profile.html', views.profile, 'profile')
]