from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


def home(request):
    return render(request, 'index.html')


def profile(request):
    return render(request, 'index.html')


def riddle(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'index.html')


def logout(request):
    return render(request, 'index.html')