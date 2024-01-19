from django.db import models
from user_authentication.models import UserProfile
from product_management.models import Product_Variant


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


class Transaction(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=1)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)


class Wishlist(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
