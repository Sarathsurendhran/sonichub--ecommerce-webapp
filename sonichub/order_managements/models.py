from django.db import models
from user_authentication.models import UserProfile
from user_panel.models import Address
from product_management.models import Product_Variant, Products


class Order_Main_data(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    total_amount = models.FloatField(null=False)
    date = models.DateField(auto_now_add=True)
    order_status = models.CharField(max_length=100, default="Order Placed")
    payment_option = models.CharField(max_length=100, default="cash_on_delivary")
    order_id = models.CharField(max_length=100, default=1)


class Order_Sub_data(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    main_order = models.ForeignKey(Order_Main_data, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, default=0)
