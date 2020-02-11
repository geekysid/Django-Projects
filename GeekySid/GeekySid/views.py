from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import smtplib, emoji
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def index (request):
    return render(request, 'index.html')


def email_2(request):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        msg = "test"
        smtp.login('siddhant.shah.86@gmail.com', 'Admin @35024')
        smtp.sentmail('siddhant.shah.86@gmail.com', 'siddhant.shah.1986@gmail.com'. msg)


def emailer (request):
    if request.method == "POST":
        contact_name = request.POST.get('contact_name', '')
        print(contact_name)
        contact_email = request.POST.get('contact_email', '')
        contact_msg = request.POST.get('contact_msg', '')
        self_email = 'siddhant.shah.1986@gmail.com'
        email_signature = settings.EMAIL_SIGNATURE

        # information fetcheed from settings.py to connect to smtp
        smtp_user = settings.EMAIL_USER
        smtp_pass = settings.EMAIL_PASS
        smtp_address = settings.EMAIL_HOST
        smtp_port = settings.EMAIL_PORT
        
        # message setting for self mail
        msg_self = MIMEMultipart()
        msg_self['To'] = self_email
        msg_self['From'] = contact_email
        msg_self['Subject'] = contact_name + ' : Sent you Message from GeekySid. ' + emoji.emojize(":sign_of_the_horns:")
        body = contact_name + ' made an enquiry through website.<p> His message is: <br />' + contact_msg + '<p>His email address is: <br />' + contact_email
        msg_self.attach(MIMEText(body, 'html'))

        # message setting for user mail
        msg_user = MIMEMultipart()
        msg_user['To'] = contact_email
        msg_user['From'] = self_email
        msg_user['Subject'] = 'Siddhant Shah - Python and Django Developer ' + emoji.emojize(":sign_of_the_horns:")
        
        body = 'Dear ' + contact_name + ',<p>Thankyou for contact me through my website http://www.geekysid.com. I really appreciate that you took time to go through my website.'
        body += '<p>Just to remind you again, I am a Python and Django Developer with good understanding of python modules like Requests, BeautifulSoup, Pandas, numPy and few more.'
        body += '<p>Let\'s talk on my below number and see how can we work together in near future.'
        body += '<p><br /><span style="">--<br />'+ email_signature
        
        msg_user.attach(MIMEText(body, 'html'))

        with smtplib.SMTP_SSL(smtp_address, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_pass)
            try:
                smtp.sendmail(contact_email, self_email, msg_self.as_string())
            except Exception as e:
                pass
            try:
                smtp.sendmail(self_email, contact_email, msg_user.as_string())
            except Exception as e:
                pass

    return HttpResponse('')