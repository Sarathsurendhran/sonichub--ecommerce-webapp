from django.db import models
from user_authentication.models import UserProfile


class Address(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, default="sarath")
    house_name = models.CharField(max_length=400, null=False)
    street_name = models.CharField(max_length=300, null=False)
    pin_number = models.IntegerField(null=False)
    district = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    country = models.CharField(max_length=200, null=False, default="null")
    phone_number = models.CharField(max_length=40, null=False)
    status = models.BooleanField(default=True)
