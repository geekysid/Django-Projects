from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Products, Order, Ordered_Product, Order_Status
from django.contrib.auth.models import User, auth
import math
import ast 
# Create your views here.


def index(request):

    # fetching discounted item
    disc_product_list = Products.objects.filter(discount__gt=0.0).order_by("-discount")  # returns list of products that has dicount attribute > 0.0 and the the list is ordered DESC by by column discount
    
    for prod in disc_product_list:
        prod.discounted_price = (prod.price - (prod.discount * prod.price) / 100)  # setting a new attribute of the product that holds the discounted price
    
    slides_discountItems = math.ceil(len(disc_product_list) / 4)  # calculatimng total number of slides reqruired. here 4 is the number of product per side.
    range_slides_discountItems = range(slides_discountItems)  # creating a generator and storing in a variable.
    discounted_product = [disc_product_list, range_slides_discountItems]

    # CATEGORY WISE PRODUCTS
    categories = Products.objects.values("category")  # returns list of dictionary as[{'category': 'Programming'}, {'category': 'MBA'}, {'category': 'MBA'}, ...]
    category = {cat_dict["category"] for cat_dict in categories}  # returns set of category as[Programming', 'MBA', ...]
    all_products = []
    
    for cat in category:
        product_cat_list = Products.objects.filter(category=cat)  # returns list of all products with matching category.
        number_slide = len(product_cat_list) // 4 + math.ceil((len(product_cat_list) / 4) - (len(product_cat_list) // 4))  # calculating number of slices required for each category
        all_products.append([product_cat_list, range(number_slide)])  # appending list of list of categorised products along with generator

    # creating a dictioary to pass to the page when it is called.
    product_params = {
        "all_products": all_products,
        "disc_product_list": disc_product_list,
        "range_slides_discountItems": range_slides_discountItems,
    }

    return render(request, "index.html", product_params)


def checkout(request):
    if request.method == 'POST':
        name = request.POST.get('inputName', '')
        email = request.POST.get('inputEmail', '')
        phone = request.POST.get('inputPhone', '')
        address = request.POST.get('inputAddress', '')
        landmark = request.POST.get('inputLandmark', '')
        city = request.POST.get('inputCity', '')
        state = request.POST.get('inputState', '')
        zipcode = request.POST.get('inputPinCode', '')
        message = request.POST.get('inputMessage', '')
        paymode = request.POST.get('paymentradio', '')
        cart = request.POST.get('cartitemhidden', '')
        
        # Creating an order in the Order Object
        try:
            order = Order(name=name, email=email, phone=phone, address=address, landmark=landmark, city=city, state=state, zipcode=zipcode, message=message, paymode=paymode)
            order.save()

            if order:
                # cart_dict = json.loads(cart)
                cart_dict = ast.literal_eval(cart)  # used this function to convert string to dictionary as json.loads() was not working for some reason

                # Adding all the proucts in a order to the Ordered_Product object
                #cart_dict Format: {'pr12': [name, qnty, price, discount, image, desc]
                for item in cart_dict:
                    product = Products.objects.get(id=int(item[2:]))    # fetching product object for each item customer wants to save it in order_product table
                    order_product = Ordered_Product(order=order, product=product, quantity=cart_dict[item][1], discount=cart_dict[item][3], price=float(cart_dict[item][2]), image=cart_dict[item][4])
                    order_product.save()

                # Setting status of the order as 'Order Placed' in Order_Status Table
                order_status = Order_Status(order= order, status_desc = "Order successfully placed", remark="We will get back to your via mail about approximate date of delivery. Genarally Arrival time is between 5-8 workind days depending on the location.")
                order_status.save()

                # return render(request, "checkout.html", {'succuessMessage': "success", 'orderid': str(order), 'emailadd': email })
                # return render(request, "orders.html", {'checkoutStatus': 'success', 'orderid': str(order), 'emailadd': email })
                return redirect("orders?orderid="+str(order)+"&emailadd="+email+"&checkoutStatus=success")
                # return render(request, "orders.html?orderid="+str(order)+"&emailadd="+email, {'checkoutStatus': 'success', 'orderid': str(order), 'emailadd': email })
            else:
                return render(request, "checkout.html", {'errorMessage': "There was an error while placing your order. Please try again or contact admin."})

        except Exception as e:
            return render(request, "checkout.html", {'errorMessage': "Exception occured: "+ str(e) +". There was an while placing your order. Please try again or contact admin."})
    else:
        return render(request, "checkout.html")


def product(request):
    if request.method == "GET" and 'id' in request.GET:
        id = request.GET.get("id", '')

        if id.strip().isnumeric:

            try:
                product = Products.objects.get(id=id)
                if product != None:
                    return render(request, 'product.html', {"product": product, "validity": "true"})
                else:
                    return render(request, 'product.html', {"error": "Invaild Product", "validity": "false"})
            except Products.DoesNotExist:
                return render(request, 'product.html', {"error": "Invaild Product", "validity": "false"})

        else:
            return render(request, 'product.html', {"error": "Invaild Product", "validity": "false"})
    else:
        return render(request, 'product.html')


def orders(request):
    if request.method == "GET" and 'orderid' in request.GET and 'emailadd' in request.GET:

        email = request.GET.get("emailadd", "").strip()
        order_id = request.GET.get("orderid", "").strip()

        if email and order_id:
            params = orders_fetchData(order_id, email)

            if 'checkoutStatus' in request.GET:
                params['checkoutStatus'] = 'success'
                params['orderid'] = order_id
                params['emailadd'] = email

            return render(request, "orders.html", params)
        else:
            return render(request, "orders.html")

    elif request.method == "POST":
        email = request.POST.get("emailadd", "").strip()
        order_id = request.POST.get("orderid", "").strip()

        params = orders_fetchData(order_id, email)
        return render(request, "orders.html", params)
    
    else:
        return render(request, "orders.html")
        
        
def orders_fetchData(order_id, email):
    try:
        order_obj = Order.objects.get(email=email, order_id=int(order_id))
    except Order.DoesNotExist:
        order_obj = None

    if order_obj:
        print(order_obj)
        try:
            ord_prod_obj = Ordered_Product.objects.filter(order=order_obj)
        except Ordered_Product.DoesNotExist:
            ord_prod_obj= None
        
        if ord_prod_obj:
            for prod_obj in ord_prod_obj:
                prod_obj.total = (prod_obj.price * prod_obj.quantity) - (prod_obj.price * prod_obj.quantity * prod_obj.discount) / 100
        else:
            prod_details_error = f"Unable to fetch order details. Please contact customer care. Order Number {order_obj.order_id}"
        
        try:    
            ord_stat_obj = Order_Status.objects.filter(order=order_obj)
        except Order_Status.DoesNotExist:
            ord_stat_obj= None

        if not ord_stat_obj:
            ord_status_error = f"Unable to fetch order status. Please contact customer care.  Order Number {order_obj.order_id}"
        
        if ord_stat_obj and ord_prod_obj:
            return {'order_obj': order_obj, 'ord_prod_obj': ord_prod_obj, 'ord_stat_obj': list(ord_stat_obj)}
        
        elif (not ord_stat_obj) and ord_prod_obj:
            return {'order_obj': order_obj, 'ord_status_error': ord_status_error, 'ord_stat_obj': list(ord_stat_obj), 'ord_prod_obj': ord_prod_obj}
        
        elif ord_stat_obj and not ord_prod_obj:
            return {'order_obj': order_obj, 'ord_prod_obj': ord_prod_obj, 'prod_details_error': prod_details_error, 'ord_stat_obj': list(ord_stat_obj)}

        else:
            return {'order_obj': order_obj, 'ord_status_error': ord_status_error, 'prod_details_error': prod_details_error}

    else:
        return {"order_error": "No order with the entered email and order id found. Please check again."}


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


def test(request):
    return render(request, 'test.html')