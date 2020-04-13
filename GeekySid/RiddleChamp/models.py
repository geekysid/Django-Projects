from django.db import models
from django.contrib.auth.models import User
from Account.models import UserProfile
import hashlib
from time import time


# generating hash of current time
def invitation_code_generator():
    return int(hashlib.sha256(str(time()).encode('utf-8')).hexdigest(), 16) % 10**8


# Riddle_Category Model - Category of Riddles
class RiddleCategory(models.Model):
    cat_id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=20)
    desc = models.TextField(max_length=100)

    def __str__(self):
        return self.name


# Riddle_Level Model - Level of Riddles
class RiddleLevel(models.Model):
    level_id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=20)
    short_name = models.CharField(max_length=10)
    desc = models.TextField(max_length=100)
    kills = models.FloatField(editable=True, default=50.0)
    positive_score_percent = models.FloatField(editable=True, default=1.0)
    negetive_score_percent = models.FloatField(editable=True, default=0.1)
    time = models.IntegerField(editable=True, default=30)

    def __str__(self):
        return self.name


# Riddle_Type Model - Type of Riddles (Audio/Image/Video/Text)
class RiddleType(models.Model):
    type_id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


# Riddle Model - Actual riddles that will be asked in Den
class Riddle(models.Model):
    riddle_id = models.AutoField(primary_key=True, unique=True)
    category  = models.ForeignKey(RiddleCategory, on_delete=models.CASCADE)
    riddle_level = models.ForeignKey(RiddleLevel, on_delete=models.CASCADE)
    type_riddle = models.ForeignKey(RiddleType, on_delete=models.CASCADE)
    media = models.ImageField(upload_to="image/riddle/", blank=True)
    question = models.CharField(max_length=1000)
    max_calls = models.IntegerField(editable=True, default=10)
    answer_1 = models.CharField(max_length=1000)
    answer_2 = models.CharField(max_length=200, blank=True)
    answer_3 = models.CharField(max_length=200, blank=True)
    answer_4 = models.CharField(max_length=200, blank=True)
    answer_5 = models.CharField(max_length=200, blank=True)
    answer_6 = models.CharField(max_length=200, blank=True)
    answer_7 = models.CharField(max_length=200, blank=True)
    answer_8 = models.CharField(max_length=200, blank=True)
    answer_9 = models.CharField(max_length=200, blank=True)
    point = models.FloatField(default=100, blank=True)
    hint = models.CharField(max_length=500, blank=True)
    answer_format = models.CharField(max_length=50, blank=True)
    uin_code = models.CharField(max_length=10, editable=True, blank=True)

    def __str__(self):
        return f"{self.category} - {self.type_riddle} - {self.riddle_id}"


# Den Model - Can be considered as league
class Den(models.Model):
    den_id = models.AutoField(primary_key=True, unique=True)
    admin  = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    desc = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to="image/den/", blank=True)
    score = models.FloatField(editable=False, default=0.0)
    is_active = models.BooleanField(default=True, blank=True)
    riddle_start_time = models.TimeField(editable=True, blank=True)
    riddles_per_day = models.IntegerField(default=2, editable=True, blank=True)
    time_bw_riddle = models.IntegerField(default=6, editable=True, blank=True)
    started_at = models.DateTimeField(auto_now=True, editable=False)
    ended_at = models.DateField(blank=True, null=True)
    next_riddle_on = models.DateField(blank=True, null=True)
    invitation_code = models.CharField(max_length=10, editable=False, blank=True)
    uin_code = models.CharField(max_length=10,  editable=True, blank=True)

    def __str__(self):
        return self.name


# Hunter_Den_Mapping Model - Users mapped to Hunting Den
class Hunter_Den_Mapping(models.Model):
    map_id = models.AutoField(primary_key=True, unique=True)
    hunter = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    den = models.ForeignKey(Den, on_delete=models.CASCADE)
    invitation_code = models.CharField(max_length=100, default='NR', null=True, blank=True)
    member_since = models.DateTimeField(blank=True, null=True)
    member_status = models.BooleanField(default=False, blank=True)


# Hunter_Den_Mapping Model - Users mapped to Hunting Den
class DenInvitee(models.Model):
    invitee = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    den = models.ForeignKey(Den, on_delete=models.CASCADE)
    email_to = models.CharField(max_length=50)
    invite_code = models.CharField(max_length=50)
    sent_on = models.DateTimeField(blank=True)
    accepted_on = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.invitee.name} - {self.den.name} - {self.email_to}"



# Den_Riddle Model -  Holds mapping of riddles to each den
class DenRiddle(models.Model):
    den_riddle_id = models.AutoField(primary_key=True, unique=True)
    den = models.ForeignKey(Den, on_delete=models.CASCADE)
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now=True, editable=True, blank=True)
    started_at = models.DateTimeField(editable=True)
    ending_at = models.DateTimeField()
    is_pending = models.BooleanField(default=True, blank=True)
    is_active = models.BooleanField(default=False, blank=True)
    uin_code = models.CharField(max_length=10,  editable=True, blank=True)
    has_expired = models.BooleanField(default=False, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['den', 'riddle'], name='den_riddle_conposite')
        ]

    def __str__(self):
        return f"{self.den} - {self.riddle}"


#  Response Model - Holds Response to Users
class Response(models.Model):
    response_id = models.AutoField(primary_key=True, unique=True)
    den_riddle = models.ForeignKey(DenRiddle, on_delete=models.CASCADE)
    hunter = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    image = models.ImageField(upload_to="image/response/", blank=True, null=True)
    is_correct = models.BooleanField(default=False, blank=True)
    score = models.FloatField(editable=True, default=0.0)
    response_at = models.DateTimeField(auto_now=True, editable=False)
    response_time = models.FloatField(editable=True, default=0.0)

    def __str__(self):
        return f"{self.response_id}"


#  Response Model - Holds Response to Users
class ResponseImage(models.Model):
    image_id = models.AutoField(primary_key=True, unique=True)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image/response/", blank=True)
