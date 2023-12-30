from django.db import models
from user_authentication.models import UserProfile
from product_management.models import Product_Variant


class Cart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)

    def __str__(self):
        return self.cart_id
