from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
# from django.contrib.auth import authenticate, login
from Account.models import UserProfile, PasswordRecovery
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib, time, smtplib, emoji, zlib

# Create your views here.
def login(request):
    if (request.method == 'GET') and ('email' in request.GET):
        if 'base' in request.GET:
            return render(request, 'login.html', {'email': request.GET.get("email", ""), 'acc': request.GET.get("acc", ""), 'Flag': 'Login'})
        else:
            return render(request, 'login.html', {'email': request.GET.get("email", ""), 'Flag': 'Register'})
    
    if (request.method == 'GET') and ('mailsent' in request.GET):
        if request.GET.get("mailSent", "") == "True":
            return render(request, 'login.html', {'mailSent': True})

    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('login')


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


def email_validity(request):
    
    # executing code only if request is made by Post Method
    if request.method == "POST":
        email = request.POST.get('email', None);

        if not(email == None):
            # checking if there is atleast one email in Userr object
            if User.objects.filter(email=email):
                return JsonResponse({'success': False, 'text': "email taken"})
            else:
                return JsonResponse({'success': True, 'text': "email not taken"})
        else:
            return JsonResponse({'success': False, 'text': "email not provided"})

    else:
        return JsonResponse({'success': False, 'text': "Request not from POST"})


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
                return JsonResponse({'success': False, 'text': "Email is already taken. Please try again with another email"})
            else:
                if User.objects.filter(username=username):
                    return JsonResponse({'success': False, 'text': "Username is already taken. Please try again with another username"})
                else:
                    try:
                        password = hashlib.sha256(password.strip().encode()).hexdigest()

                        user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
                        user.save()

                        # if user object is not null, i.e., user is successfully created
                        if user:
                            # generating activiation code using sha256 to current epoch time
                            activation_code = hashlib.sha256(str(time.time()).encode()).hexdigest()[:10]
                            # generating randome number
                            random_number = random.choice([x for x in range(0,100)])
                            # generating UNI code using crc32 to current epoch time
                            uin_code = zlib.crc32(str(hashlib.sha256((str(time.time())+str(random_number)+str(user.id)).encode()).hexdigest()).encode())

                            # trying to create user ptofile object
                            user_profile = UserProfile(user=user, name=name, gender="Male", email=email, activation_code=activation_code, is_active=False, uin_code=uin_code)
                            user_profile.save()

                            # if user is added to user profile
                            if user_profile:

                                link = "http://127.0.0.1:8000/account/account_activate?email="+email+"&act_link="+activation_code
            
                                # message setting for self mail
                                msg = MIMEMultipart()
                                msg['To'] = email
                                msg['Subject'] = "Hunterz Den - Activate your Account " + emoji.emojize(":sign_of_the_horns:")

                                body = "Thankyou for making account with us. Please <a href="+link+">click here</a> to activate your account."

                                msg.attach(MIMEText(body, 'html'))

                                
                                send_mail(email, msg)

                                params = {'email': email}
                                return JsonResponse({'success': True, 'msg': params})
                        
                    except Exception as e:
                        return JsonResponse({'success': False, 'exception': str(e), 'error': 'There was an issue creating an account for you. Please contact customer support'})

                    return JsonResponse({'success': True, 'text': "email not taken"})
        else:
            return JsonResponse({'success': False, 'error': "It seems you have not ptovided all data required to create account. In case of any difficulty, please contact customer support"})

    else:
        return JsonResponse({'success': False, 'text': "Invalid Request"})


def user_login(request):

    # executing code only if request is made by Post Method
    if request.method == "POST":
        password = request.POST.get('password', None);
        username = request.POST.get('username', None);
        if ((password is not None) and (username is not None)):
            # checking if there is atleast one email in Userr object

            user_test = User.objects.get(username=username)
            try:
                password = hashlib.sha256(password.strip().encode()).hexdigest()
                # user = User.objects.get(username=username, password=password)
                user = auth.authenticate(username=username, password=password)

                if not user:
                    return JsonResponse({'success': False, 'error': 'Username and Password do not match'})
                else:
                    userProfile_obj = UserProfile.objects.get(user=user)
                    userProfile_obj = userProfile_obj
                    if not userProfile_obj.is_active:
                        return JsonResponse({'success': 'inactive', 'error': 'inactive', 'email': userProfile_obj.email, 'activation_code':userProfile_obj.activation_code})
                    else:
                        auth.login(request, user)
                        return JsonResponse({'success': True})

            except Exception as e:
                    return JsonResponse({'success': False, 'exception': str(e), 'error': 'Username and Password do not match.'})
        else:
            return JsonResponse({'success': False, 'error': 'All values not provided'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})


def account_activate(request):
    if request.user.is_authenticated:
        auth.logout(request)
    
    if request.method == 'GET' and 'email' in request.GET and 'act_link' in request.GET:
        email = request.GET.get('email', '')
        act_link = request.GET.get('act_link', '')
        if len(email)>0 and len(act_link) > 0:
            try:
                user_profile = UserProfile.objects.get(email=email)
 
                if user_profile:
                    if user_profile.is_active == True:
                        return render(request, 'login.html', {'Flag': 'Already_Activated', 'email': email})
                    
                    else:
                        if user_profile.activation_code == act_link:
                            try:
                                UserProfile.objects.filter(email=email).update(is_active = True)
                                return render(request, 'login.html', {'Flag': 'Activated', 'email': email})
                            except Exception as e:
                                return render(request, 'login.html', {'Flag': 'Activation_Error', 'error': 'Exception Occured'})
                        else:
                            return render(request, 'login.html', {'Flag': 'Activation_Error', 'error': 'Invalid Activation Code'})
                else:
                    return render(request, 'login.html', {'Flag': 'Activation_Error', 'error': 'Invalid Email'})
            except:
                return render(request, 'login.html', {'Flag': 'Activation_Error', 'error': 'Invalid Email'})
        else:
            return render(request, 'login.html', {'Flag': 'Activation_Error', 'error': 'Some data missing'})

    else:
        return render(request, 'login.html', {'Flag': 'Activation_Error', 'error': 'Invalid Request'})


def forgot_password(request):
    return render(request, 'forgotpassword.html')


def forgot_password_link(request):
    if request.user.is_authenticated:
        auth.logout(request)

    if request.method == 'POST' and 'email' in request.POST:
        email = request.POST.get('email', '')
        if len(email)>0:
            try:
                user_obj = User.objects.get(email=email)
 
                if user_obj:
                    try:
                        token = hashlib.sha512(str(time.time()).encode()).hexdigest()
                        pr_obj = PasswordRecovery(user=user_obj, token=token, email=email, generated_on=time.time(), expired_on=(time.time()+1800))
                        pr_obj.save()

                        if pr_obj:
                            link = "http://127.0.0.1:8000/account/reset_password?email="+email+"&token="+token
            
                            # message setting for self mail
                            msg = MIMEMultipart()
                            msg['To'] = email
                            msg['Subject'] = "Hunterz Den - Rest your Password " + emoji.emojize(":sign_of_the_horns:")

                            body = "Please click on <a href="+link+">click here</a> to reset your password."

                            msg.attach(MIMEText(body, 'html'))
                            
                            send_mail(email, msg)

                            
                            return render(request, 'login.html', {'Flag': 'PRL_Success', 'email': email })
                        else:
                            return render(request, 'login.html', {'Flag': 'PRL_Error', 'error': 'Exception Occured' })

                    except Exception as e:
                        return render(request, 'login.html', {'Flag': 'PRL_Error', 'error': 'Exception - '+str(e) })
                else:
                    return render(request, 'forgotpassword.html', {'Flag': 'PRL_Error', 'error': 'Invalid Email' })
            except Exception as e:
                return render(request, 'login.html', {'Flag': 'PRL_Error', 'error': 'Exception - '+str(e)})
        else:
            return render(request, 'login.html', {'Flag': 'PRL_Error', 'error': 'Some data missing'})

    else:
        return render(request, 'login.html', {'Flag': 'PRL_Error', 'error': 'Invalid Request'})


def reset_password(request):
    if request.user.is_authenticated:
        auth.logout(request)

    if request.method=="GET":
        token = request.GET.get("token", '')
        email = request.GET.get("email", '')

        if len(email)>0 and len(token)>0:
            try:
                pr_obj = PasswordRecovery.objects.get(email=email, token=token, expired_on__gte=time.time())
                return render(request, 'reset_password.html')
            except Exception as e:
                return render(request, 'forgotpassword.html', {'Flag': 'RP_ERRROR', 'error': 'Invaid email/Password or Token Expired.'})
        else:
            return render(request, 'forgotpassword.html', {'Flag': 'RP_ERRROR', 'error': "Not a valid request to reset password...."})
    else:
        return render(request, 'forgotpassword.html', {'Flag': 'RP_ERRROR', 'error': "Not a valid request to reset passworddddddd"})


def reset_password_call(request):

    if request.is_ajax and request.method=="POST":
        password = request.POST.get("password", '')
        token = request.POST.get("token", '')
        email = request.POST.get("email", '')

        if len(password)>0 and len(token)>0 and len(email)>0:
            try:
                pr_obj = PasswordRecovery.objects.get(email=email, token=token)
                if pr_obj:
                    if pr_obj.expired_on >= time.time():
                        password = hashlib.sha256(password.strip().encode()).hexdigest()
                        user_obj = User.objects.get(email=email)
                        user_obj.set_password(password)
                        user_obj.save()

                        # return render(request, 'login.html', {'Flag': 'Password_Reset'})
                        return JsonResponse({'success': True, 'error': 'Invalid request'})
                    return render(request, 'forgotpassword.html', {'Flag': 'RP_ERRROR', 'error': 'Token Expired. Please try again.'})
                else:
                    return render(request, 'reset_password.html', {'Flag': 'RP_ERRROR', 'error': "email and token dont match"})
            except Exception as e:
                return render(request, 'reset_password.html', {'Flag': 'RP_ERRROR', 'error': 'Exception: '+str(e)})
        else:
            return render(request, 'reset_password.html', {'Flag': 'RP_ERRROR', 'error': "Some Values Missing"})
    else:
        return render(request, 'reset_password.html')


def resent_activation_mail(request):
    if request.is_ajax:

        if request.method == 'GET' and 'email' in request.GET and 'act_link' in request.GET:
            email = request.GET.get('email', '')
            act_link = request.GET.get('act_link', '')

            link = "http://127.0.0.1:8000/account/account_activate?email="+email+"&act_link="+act_link
            
            # message setting for self mail
            msg = MIMEMultipart()
            msg['To'] = email
            msg['Subject'] = "Hunterz Den - Activate your Account " + emoji.emojize(":sign_of_the_horns:")

            body = "Thankyou for making account with us. Please <a href="+link+">click here</a> to activate your account."

            msg.attach(MIMEText(body, 'html'))

            
            send_mail(email, msg)
            
            return render(request, 'login.html', {'Flag': 'Activation_Mail_Sent', 'email': email})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})


# function that connects to smtp and send mail
def send_mail(email, msg):
    
    # information fetcheed from settings.py to connect to smtp
    smtp_user = 'blah@blah.com'
    smtp_pass = 'blah'
    smtp_address = "smtp.gmail.com"
    smtp_port = 465

    msg['From'] = smtp_user

    with smtplib.SMTP_SSL(smtp_address, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        try:
            smtp.sendmail(smtp_user, email, msg.as_string())
        except Exception as e:
            print("Exception: ", str(e))