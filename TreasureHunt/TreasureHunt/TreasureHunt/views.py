from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings


def home(request):
    return redirect('/account/login')


def login(request):
    return redirect('/account/login')


def logout(request):
    return redirect('/account/logout')



# ERROR PAGE
def error(request):
    
    url_path = request.META.get('PATH_INFO')
    error_code = url_path.split('/')[len(url_path.split('/'))-1]
    
    if error_code == 'error':
        message = "This is not a valid request Buddy."
    if error_code == '5379c8a0':
        message = "This is not a valid request Buddy."
    else:
        message = "This is not a valid request Buddy."
    
    params = {
        "code": error_code,
        "msg" : message
    }
    return render(request, 'error.html', params)
