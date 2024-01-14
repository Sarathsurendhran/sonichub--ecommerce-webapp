from django.db import models
from user_authentication.models import UserProfile


class Coupon(models.Model):
  minimum_amount = models.IntegerField(null=False)
  discount = models.IntegerField(null=False)
  expiry_date = models.DateField(null=False)
  Coupon_code = models.CharField(max_length=50,null=False)
  is_active =models.BooleanField(default=True)


class Users_Coupon(models.Model):
  coupon = models.ForeignKey(Coupon,on_delete = models.CASCADE)
  user =models.ForeignKey(UserProfile, on_delete=models.CASCADE)




