from django.db import models
from user_authentication.models import UserProfile
from user_panel.models import Address
from product_management.models import Product_Variant

class Order_Main(models.Model):
  user = models.ForeignKey(UserProfile,on_delete = models.CASCADE)
  address = models.ForeignKey(Address, on_delete=models.CASCADE)
  price = models.IntegerField(null=False)
  date = models.DateTimeField(auto_now_add=True)
  order_status = models.BooleanField(default=True)


class Order_Sub(models.Model):
  user = models.ForeignKey(UserProfile,on_delete = models.CASCADE)
  variant = models.ForeignKey(Product_Variant,on_delete=models.CASCADE)
  quantity = models.IntegerField(null=False)
