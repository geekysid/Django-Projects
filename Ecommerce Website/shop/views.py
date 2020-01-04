from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Products
from django.contrib.auth.models import User, auth
import math

# Create your views here.


def index(request):

    # fetching discounted item
    disc_product_list = Products.objects.filter(discount__gt=0.0).order_by(
        "-discount"
    )  # returns list of products that has dicount attribute > 0.0 and the the list is ordered DESC by by column discount
    for prod in disc_product_list:
        prod.discounted_price = (
            prod.price - (prod.discount * prod.price) / 100
        )  # setting a new attribute of the product that holds the discounted price
    slides_discountItems = math.ceil(
        len(disc_product_list) / 4
    )  # calculatimng total number of slides reqruired. here 4 is the number of product per side.
    range_slides_discountItems = range(
        slides_discountItems
    )  # creating a generator and storing in a variable.
    discounted_product = [disc_product_list, range_slides_discountItems]

    # CATEGORY WISE PRODUCTS
    categories = Products.objects.values(
        "category"
    )  # returns list of dictionary as[{'category': 'Programming'}, {'category': 'MBA'}, {'category': 'MBA'}, ...]
    category = {
        cat_dict["category"] for cat_dict in categories
    }  # returns set of category as[Programming', 'MBA', ...]
    all_products = []
    for cat in category:
        product_cat_list = Products.objects.filter(
            category=cat
        )  # returns list of all products with matching category.
        number_slide = len(product_cat_list) // 4 + math.ceil(
            (len(product_cat_list) / 4) - (len(product_cat_list) // 4)
        )  # calculating number of slices required for each category
        all_products.append(
            [product_cat_list, range(number_slide)]
        )  # appending list of list of categorised products along with generator

    # creating a dictioary to pass to the page when it is called.
    product_params = {
        "all_products": all_products,
        "disc_product_list": disc_product_list,
        "range_slides_discountItems": range_slides_discountItems,
    }

    return render(request, "index.html", product_params)


def checkout(request):
    return render(request, "checkout.html")


def product(request):
    if request.method == "GET":
        id = request.GET["id"]
    return HttpResponse("ProductId : " + id)


def login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]

            user = auth.authenticate(username=username, password=password)

            if user:
                auth.login(request, user)
                return redirect("/shop/index")
            else:
                return render(
                    request,
                    "login.html",
                    {"log_error_message": "Username/Password not correct"},
                )
        else:
            return render(
                request, "login.html", {"log_error_message": "Please login here"}
            )
    else:
        return render(request, "index.html")


def register(request):
    if not request.user.is_authenticated:  # checking if user is looged in

        if request.method == "POST":

            # fetching data
            fname = request.POST["fname"]
            lname = request.POST["lname"]
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            conf_pass = request.POST["confirm_password"]

            if password == conf_pass:
                if not User.objects.filter(email=email):
                    if not User.objects.filter(username=username):
                        try:
                            user = User.objects.create_user(
                                first_name=fname,
                                last_name=lname,
                                email=email,
                                username=username,
                                password=password,
                            )
                            user.save()
                        except:
                            return render(
                                request,
                                "login.html",
                                {"reg_error_message": "Exception occured"},
                            )
                        if user:
                            return render(
                                request,
                                "login.html",
                                {
                                    "reg_success_message": "You are registerd successfully. Please confirm your email by clicking link in your email."
                                },
                            )
                        else:
                            return render(
                                request,
                                "login.html",
                                {
                                    "reg_error_message": "There was error in registering you. Please try again."
                                },
                            )
                    else:
                        return render(
                            request,
                            "login.html",
                            {
                                "reg_error_message": "Username already used. Please use anyother username."
                            },
                        )
                else:
                    return render(
                        request,
                        "login.html",
                        {
                            "reg_error_message": "Email account already used. Please use anyother email."
                        },
                    )
            else:
                return render(
                    request,
                    "login.html",
                    {"reg_error_message": "Password didn't matched"},
                )

        else:
            return render(request, "login.html")
    else:
        return render(request, "index.html")


def logout(request):
    auth.logout(request)
    return redirect("/shop/index")

