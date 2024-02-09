from django.db import models
from user_authentication.models import UserProfile
from order_managements.models import Order_Main_data


class Coupon(models.Model):
    minimum_amount = models.IntegerField(null=False)
    discount = models.IntegerField(null=False)
    expiry_date = models.DateField(null=False)
    Coupon_code = models.CharField(max_length=50, null=False)
    status = models.BooleanField(default=True)


class Users_Coupon(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=50, null=True)
    coupon_discount = models.IntegerField(null=True)
    order = models.ForeignKey(Order_Main_data, on_delete=models.CASCADE, null=True)
