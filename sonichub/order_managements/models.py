from django.db import models
from user_authentication.models import UserProfile
from user_panel.models import Address
from product_management.models import Product_Variant, Products


class Order_Main_data(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    total_amount = models.FloatField(null=False)
    date = models.DateField(auto_now_add=True)
    order_status = models.CharField(max_length=100, default="Order Placed")
    payment_option = models.CharField(max_length=100, default="cash_on_delivary")
    order_id = models.CharField(max_length=100, default=1)
    is_active = models.BooleanField(default=True)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=50,default=1)
    coupon_discount = models.IntegerField(null=True) 

    name = models.CharField(max_length=50, null=False, default="sarath")
    house_name = models.CharField(max_length=400, null=False,  default="null")
    street_name = models.CharField(max_length=300, null=False,  default="null")
    pin_number = models.IntegerField(null=False,  default=1)
    district = models.CharField(max_length=200, null=False, default="null" )
    state = models.CharField(max_length=200, null=False, default="null")
    country = models.CharField(max_length=200, null=False, default="null")
    phone_number = models.CharField(max_length=40, null=False, default="null")



class Order_Sub_data(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    main_order = models.ForeignKey(Order_Main_data, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, default=0)
    is_active = models.BooleanField(default=True)

    def total_cost_coupon(self):
        unit_price = self.variant.product.offer_price * self.quantity
        if self.variant.product.product_category.discount:
            price = self.variant.product.price
            category_discount = int(self.variant.product.product_category.discount)
            total_discount = float(price) * (category_discount / 100)
            unit_price = float(unit_price) - total_discount

            return unit_price

    
    def total_cost(self):
         return self.quantity * self.variant.product.offer_price
    
   

