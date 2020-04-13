from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
# from django.contrib.auth import authenticate, login
from Account.models import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib, time, smtplib, emoji, zlib
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from random import choice



# method that returns url params
def get_ParamsFromUrl(url):
    url_path = url.split('/')
    status = url_path[len(url_path)-2]
    code = url_path[len(url_path)-1]
    return (status, code)


# method that returns data to show alert depending on url like index/s/8768
def get_AlertDataFromUrl(url):
    (status, code) = get_ParamsFromUrl(url)
    type_ = 'success' if status == 's' else ('error' if status == 'e' else None)
    if type_ is not None:
        error_obj = ErrorCode.objects.filter(hash_code=code, Type=type_)
        if len(error_obj) == 1:
            print(error_obj[0])
            return (error_obj[0])
        else:
            return (None)
    else:
        return (None)


# function called when user visits login page
def login(request):
    url = request.META.get('PATH_INFO')

    if request.user.is_authenticated:

        if UserProfile.objects.get(user=request.user.id).is_active: 
            (type_, code) = get_ParamsFromUrl(url)

            if type_ == 's' or type_ == 'e':
                redirect_link = '/riddlechamp/index/'+type_+'/'+code
            else:
                redirect_link = '/riddlechamp/index/e/d963'

            return redirect(redirect_link)
        else:
            alertData = get_AlertDataFromUrl('/account/login/e/7f95')
            return render(request, 'account/login.html', {'alertData': alertData})


    if (request.method == 'GET') and ('email' in request.GET):
        if 'base' in request.GET:
            return render(request, 'account/login.html', {'email': request.GET.get("email", ""), 'acc': request.GET.get("acc", ""), 'Flag': 'Login'})
        else:
            return render(request, 'account/login.html', {'email': request.GET.get("email", ""), 'Flag': 'Register'})

    if (request.method == 'GET') and ('mailsent' in request.GET):
        if request.GET.get("mailSent", "") == "True":
            return render(request, 'login.html', {'mailSent': True})

    alertData = get_AlertDataFromUrl(url)
    return render(request, 'account/login.html', {'alertData': alertData})


def register(request):
    if request.user.is_authenticated:
        return redirect('/riddlechamp/index/e/d823')
    else:
        url = request.META.get('PATH_INFO')
        alertData = get_AlertDataFromUrl(url)
        return render(request, 'account/register.html', {'alertData': alertData})


def logout(request):
    auth.logout(request)
    return redirect('/account/login')


# Page called by user to make changes in profle
def profile(request):
    if request.user.is_authenticated:
        userpro_obj = UserProfile.objects.get(user=request.user.id)
        params = {
            'email': userpro_obj.email,
            'name': userpro_obj.name,
            'gender': userpro_obj.gender,
            'city': userpro_obj.city,
            'country': userpro_obj.country,
            'contact': userpro_obj.mobile,
            'avatar': userpro_obj.avatar
        }

        return render(request, 'account/profile.html', params)

    return redirect('/account/login')


# Page called by user when he access the link sent to him for resetting password.
def reset_password(request):
    if request.user.is_authenticated:
        return redirect('/riddlechamp/index')
    else:
        if request.method=="GET" and 'token' in request.GET and 'email' in request.GET:
            token = request.GET.get("token", '')
            email = request.GET.get("email", '')

            if len(email)>0 and len(token)>0:
                try:
                    pr_obj = PasswordRecovery.objects.get(email=email, token=token)
                    
                    if pr_obj.expired_on > time.time():
                        return render(request, 'account/reset_password.html')
                    else:
                        return render(request, 'account/reset_password.html', {'Flag': 'RP_ERRROR', 'error': 'Token Exprired'})
                except:
                    return render(request, 'account/reset_password.html', {'Flag': 'RP_ERRROR', 'error': 'Invaid email/token combination.'})
            else:
                return render(request, 'account/reset_password.html', {'Flag': 'RP_ERRROR', 'error': "Some data is missing"})
        else:
            return render(request, 'account/reset_password.html', {'Flag': 'RP_ERRROR', 'error': "Not a valid request to reset password buddy"})


# function called by ajax to update profile data in database
def profile_update(request):
    if request.is_ajax() and request.method == 'POST':
        try:
            name = request.POST['name']
            city = request.POST['city']
            country = request.POST['country']
            gender = request.POST['gender']
            mobile = request.POST['contact']
            
            current_time_epoch = int(datetime.now().strftime('%s'))


            request.user.first_name = name
            request.user.save()

            userProfile_obj = UserProfile.objects.get(user = request.user.id)

            # File Handeling
            extenstion = (request.FILES['avatar'].name).split('.')[len(request.FILES['avatar'].name.split('.'))-1]
            pic_name = str(userProfile_obj.user.id) + '_' + str(current_time_epoch) + '.' + extenstion
            fs = FileSystemStorage(location='media/image/profile_photo/')
            filename = fs.save(pic_name, request.FILES['avatar'])
            fs.base_url = 'image/profile_photo/'
            uploaded_file_url = fs.url(filename)
            
            userProfile_obj.name = name
            userProfile_obj.city = city
            userProfile_obj.country = country
            userProfile_obj.gender = gender
            userProfile_obj.mobile = mobile
            userProfile_obj.avatar = uploaded_file_url

            userProfile_obj.save()

            return JsonResponse({"successFlag": True, "error": "Success"})
        
        except Exception as e:
            print(str(e))
            return JsonResponse({"successFlag": False, "error": "Exception"})
        
    else:
        return JsonResponse({"successFlag": False, "error": "Invalid Request"})


# function called by ajax to check if username exist in database or not
def username_validity(request):
    
    # executing code only if request is made by Post Method
    if request.method == "POST":
        username = request.POST.get('username', None);

        if not(username == None):
            # checking if there is atleast one username un Userr object
            if User.objects.filter(username=username):
                return JsonResponse({'success': False, 'text': "username taken"})
            else:
                return JsonResponse({'success': True, 'text': "Username not taken"})
        else:
            return JsonResponse({'success': False, 'text': "Username not provided"})

    else:
        return JsonResponse({'success': False, 'text': "Request not from POST"})


# function called by ajax to check if email exist in database or not
def email_validity(request):
    
    # executing code only if request is made by Post Method
    if request.method == "POST":
        email = request.POST.get('email', None);

        if not(email == None):
            # checking if there is atleast one email in Userr object
            if User.objects.filter(email=email):
                return JsonResponse({'successFlag': False, 'text': "email taken"})
            else:
                return JsonResponse({'successFlag': True, 'text': "email not taken"})
        else:
            return JsonResponse({'successFlag': False, 'text': "email not provided"})

    else:
        return JsonResponse({'successFlag': False, 'text': "Request not from POST"})


# function called by ajax to register new user
def user_registration(request):
    
    # executing code only if request is made by Post Method
    if request.method == "POST":
        email = request.POST.get('email', None);
        name = request.POST.get('name', None);
        password = request.POST.get('password', None);
        username = request.POST.get('username', None);

        if ((email is not None) and (password is not None) and (name is not None) and (username is not None)):
            # checking if there is atleast one email in Userr object

            if User.objects.filter(email=email):
                return JsonResponse({'successFlag': False, 'error': "Email IN USE", 'message': "Email is already taken. Please try again with another email"})
            else:
                if User.objects.filter(username=username):
                    print("============0============")
                    return JsonResponse({'successFlag': False, "error":"Username Taken", 'message': "Username is already taken. Please try again with another username"})
                else:
                    try:

                        password = hashlib.sha256(password.strip().encode()).hexdigest()

                        user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
                        user.save()

                        # if user object is not null, i.e., user is successfully created
                        if user:
                            # generating activiation code using sha256 to current epoch time
                            activation_code = hashlib.sha256(str(time.time()).encode()).hexdigest()[:10]

                            # generating UNI code using crc32 to current epoch time
                            uniqueString = str(user.id) + '-' + str(time.time())
                            uin_code = zlib.crc32(str(hashlib.sha256((uniqueString).encode()).hexdigest()).encode())

                            # trying to create user ptofile object
                            user_profile = UserProfile(user=user, name=name, gender="Male", email=email, activation_code=activation_code, is_active=False, uin_code=uin_code)
                            user_profile.save()

                            # if user is added to user profile
                            if user_profile:
                                
                                link = "http://127.0.0.1:8000/account/account_activate?email="+email+"&act_link="+activation_code
            
                                # message setting for self mail
                                msg = MIMEMultipart()
                                msg['To'] = email
                                msg['Subject'] = "riddlechampz Den - Activate your Account " + emoji.emojize(":sign_of_the_horns:")

                                body = "Thankyou for making account with us. Please <a href="+link+">click here</a> to activate your account."

                                msg.attach(MIMEText(body, 'html'))

                                send_mail(email, msg)

                                params = {'email': email}
                                return JsonResponse({'successFlag': True, 'msg': params})
                        
                    except Exception as e:
                        print(str(e))
                        return JsonResponse({'successFlag': False, 'error': "Exception", 'message': 'There was an issue creating an account for you. Please contact customer support. Exception: '+str(e)})
        else:
            return JsonResponse({'successFlag': False, "error":"Data Missing", 'message': "It seems you have not provided all data required to create account. In case of any difficulty, please contact customer support"})

    else:
        return JsonResponse({'successFlag': False, 'error': "Invalid Request", "message": "This is not a Valid Request"})


# function called by user  click 'sign in' button on login page
def user_login(request):

    # executing code only if request is made by Post Method
    if request.method == "POST" and 'password' in request.POST and 'username' in request.POST:
        password = request.POST.get('password', None);
        username = request.POST.get('username', None);
        if ((password is not None) and (username is not None)):

            # checking if there is atleast one email in Userr object
            user_test = User.objects.filter(username=username)

            if len(user_test) > 0:
                try:
                    password = hashlib.sha256(password.strip().encode()).hexdigest()
                    # user = User.objects.get(username=username, password=password)
                    user = auth.authenticate(username=username, password=password)

                    if not user:
                        return JsonResponse({'successFlag': False, 'error': 'Invalid Credentials', 'message': 'Username and Password do not match Buddy'})
                    else:
                        userProfile_obj = UserProfile.objects.get(user=user)
                        userProfile_obj = userProfile_obj
                        if not userProfile_obj.is_active:
                            return JsonResponse({'successFlag': 'False', 'error': 'Inactive Account', 'message': 'The account you are trying to access is not active. Please find activation link in your mail - '+ userProfile_obj.email, 'email': userProfile_obj.email, 'ac_code':userProfile_obj.activation_code})
                        else:
                            auth.login(request, user)
                            return JsonResponse({'successFlag': True})

                except Exception as e:
                    return JsonResponse({'successFlag': False, 'message': 'There was an exception raised while trying to log you in. Pleace contact System Admin. Exception => '+str(e), 'error': 'Exception'})
            else:
                return JsonResponse({'successFlag': False, 'error': 'Invalid Credentials', 'message': 'No Account with this username found'})
        else:
            return JsonResponse({'successFlag': False, 'error': 'Invalid Data', 'message': 'Username or Password not provided' })
    else:
        return JsonResponse({'successFlag': False, 'error': 'Invalid Request', "message": 'This is not a valid request. Please try again.'})


# Page called by user to activate the account
def account_activate(request):
    if request.user.is_authenticated:
        auth.logout(request)

    if request.method == 'GET' and 'email' in request.GET and 'act_link' in request.GET:
        email = request.GET.get('email', '')
        act_link = request.GET.get('act_link', '')
        print(email)
        if len(email)>0 and len(act_link) > 0:
            try:
                user_profile = UserProfile.objects.get(email=email)
 
                if user_profile:
                    if user_profile.is_active == True:
                        return redirect('/account/login/s/1b22')
                    
                    else:
                        if user_profile.activation_code == act_link:
                            try:
                                UserProfile.objects.filter(email=email).update(is_active = True)
                                return redirect('/account/login/s/dbe3')
                            except Exception as e:
                                return redirect('/account/login/e/1a62')
                        else:
                            return redirect('/account/login/e/daa3')
                else:
                    return redirect('/account/login/e/18e2')
            except Exception as e:
                return redirect('/account/login/e/18e2')
        else:
            return redirect('/account/login/e/18e2')
    else:
        return redirect('/account/login/e/18e2')


# Page called by user who needs to reset password
def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('/riddlechamp/index/e/19a2')
    else:
        return render(request, 'account/forgotpassword.html')


# Function called by ajax to generate link for restting password and mailing to the user
def forgot_password_link(request):
    if request.user.is_authenticated:
        return redirect('/riddlechamp/index/e/19a2')
    else:
        if request.method == 'POST' and 'email' in request.POST:
            email = request.POST.get('email', '')
            if len(email)>0:
                try:
                    user_obj = User.objects.filter(email=email)
    
                    if len(user_obj) > 0:
                        try:
                            print(user_obj)
                            token = hashlib.sha512(str(time.time()).encode()).hexdigest()
                            pr_obj = PasswordRecovery(user=user_obj[0], token=token, email=email, generated_on=time.time(), expired_on=(time.time()+1800))
                            pr_obj.save()

                            if pr_obj:
                                link = "http://127.0.0.1:8000/account/reset_password?email="+email+"&token="+token
                
                                # message setting for self mail
                                msg = MIMEMultipart()
                                msg['To'] = email
                                msg['Subject'] = "riddlechampz Den - Rest your Password " + emoji.emojize(":sign_of_the_horns:")

                                body = "Please click on <a href="+link+">click here</a> to reset your password. Please note the link will expire in 30 mins"

                                msg.attach(MIMEText(body, 'html'))
                                try:
                                    send_mail(email, msg)
                                    return JsonResponse({'successFlag': True})
                                except Exception as e:
                                    return JsonResponse({'successFlag': False, 'error': 'Exception', 'message': 'An Exception occured while sending mail. Please contact System Admin. Exception => '+ str(e)})
                            else:
                                return JsonResponse({'successFlag': False, 'error': 'Error', 'message': 'We were unable to generate the link. Please try after sometime.'})

                        except Exception as e:
                            return JsonResponse({'successFlag': False, 'error': 'Exception', 'message': 'An Exception occured. Please contact System Admin. Exception => '+ str(e)})
                    
                    else:
                        return JsonResponse({'successFlag': False, 'error': 'Incorrect Email', 'message': 'No Account found in our system with this email'})
                except Exception as e:
                    return JsonResponse({'successFlag': False, 'error': 'Exception', 'message': 'An Exception occured while fetching data. Please contact System Admin. Exception => '+ str(e)})
            else:
                return JsonResponse({'successFlag': False, 'error': 'Some Data Missing', 'message': 'Some Data Missing'})

        else:
                return JsonResponse({'successFlag': False, 'error': 'Invalid Request'})


# Function called by ajax that changes password in database
def set_new_password(request):

    if request.is_ajax() and request.method=="POST":
        password = request.POST.get("password", '')
        token = request.POST.get("token", '')
        email = request.POST.get("email", '')

        if len(password)>0 and len(token)>0 and len(email)>0:
            try:
                pr_obj = PasswordRecovery.objects.get(email=email, token=token)
                password = hashlib.sha256(password.strip().encode()).hexdigest()
                user_obj = User.objects.get(email=email)
                user_obj.set_password(password)
                user_obj.save()

                return JsonResponse({'successFlag': True})
            except Exception as e:
                return JsonResponse({'successFlag': False, 'error': 'Invalid Token', 'message': 'The Token seems to  be invalid. Please regenerate new link to reset password.'})
        else:
            return JsonResponse({'successFlag': False, 'error': 'Some Data Missing', 'message': 'Unable to change Password. Some data missing. Please regenerate new link to reset password.'})
    else:
        return JsonResponse({'successFlag': False, 'error':'Invalid Request', 'message': 'This is an invalid request'})


# Function called by ajax to resent activation mail
def resent_activation_mail(request):
    if request.is_ajax():

        if request.method == 'GET' and 'email' in request.GET and 'act_link' in request.GET:
            email = request.GET.get('email', '')
            act_code = request.GET.get('act_link', '')

            link = "http://127.0.0.1:8000/account/account_activate?email="+email+"&act_link="+act_code
            
            # message setting for self mail
            msg = MIMEMultipart()
            msg['To'] = email
            msg['Subject'] = "riddlechampz Den - Activate your Account " + emoji.emojize(":sign_of_the_horns:")

            body = "Thankyou for making account with us. Please <a href="+link+">click here</a> to activate your account."

            msg.attach(MIMEText(body, 'html'))

            send_mail(email, msg)

            return JsonResponse({'successFlag': True, 'message': 'Activation mail successfully sent to email address'+email, 'email': email})
        else:
            return JsonResponse({'successFlag': False, 'error': 'Data Missing', "message": "We couldn't sent you activation mail as some data were missing. Please contact System Admin"})
    else:
        return JsonResponse({'successFlag': False, 'error': 'Invalid Request'})


# function that connects to smtp and send mail
def send_mail(email, msg):
    
    # information fetcheed from settings.py to connect to smtp
    smtp_user = ''
    smtp_pass = ''
    smtp_address = "smtp.gmail.com"
    smtp_port = 465

    msg['From'] = smtp_user

    with smtplib.SMTP_SSL(smtp_address, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        try:
            smtp.sendmail(smtp_user, email, msg.as_string())
        except Exception as e:
            print("Exception: ", str(e))