from django.db import models
from user_authentication.models import UserProfile
from product_management.models import Product_Variant,Products


class Cart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.product_name  

   