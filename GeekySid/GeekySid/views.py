from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from . import cvEmailer     # file holing emailers


def index (request):
    return render(request, 'index.html')


def emailer (request):
    if request.method == "POST":
        name = request.POST.get('contact_name', '')
        email = request.POST.get('contact_email', '')
        msg = request.POST.get('contact_msg', '')

        # calling contactPage_mail function from cvMailer file to sent mail to self and user
        cvEmailer.contactPage_mail(name, email, msg)

    return HttpResponse('')