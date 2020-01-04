from django.http import HttpResponse


def index(request):
    return HttpResponse("<h1>WELCOME TO MY ECOM WEBSITE</h1>Go to my <a href='blog/index'>Blog</a><br />Go to my <a href='shop/index'>Shop</a><br />")