from django.db import models
from django.contrib.auth.models import User
import random


gender_options = (("Male", "Male"), ("Female", "Female"), ("Others", "Others"))


# User_Profile Model - Profile detail of user
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=gender_options, default="Male")
    email = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=20, default="", blank=True)
    country = models.CharField(max_length=20, default="", blank=True)
    uin_code = models.CharField(max_length=10, blank=True)
    avatar = models.ImageField(upload_to="image/profile_photo/", blank=True)
    activation_code = models.CharField(max_length=20, default="")
    is_active = models.BooleanField(default=False, editable=True, blank=True)

    def __str__(self):
        return self.name


# PasswordRecovery Model - details of password recovery
class PasswordRecovery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    generated_on = models.FloatField(editable=False, default=0.0)
    expired_on = models.FloatField(editable=False, default=0.0)

    def __str__(self):
        return self.email


# ERROR CODES
class ErrorCode(models.Model):
    code = models.CharField(max_length=10)
    Type = models.CharField(max_length=10)
    hash_code = models.CharField(max_length=10)
    title = models.CharField(max_length=20)
    message = models.CharField(max_length=100)