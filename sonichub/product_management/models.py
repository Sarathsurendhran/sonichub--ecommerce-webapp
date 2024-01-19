from django.db import models
from category_management.models import Category
from brand_management.models import Brand
from user_authentication.models import UserProfile

class Products(models.Model):
  product_name = models.CharField(max_length = 100, null = False)
  product_description = models.TextField(max_length = 5000, null = False)
  product_category = models.ForeignKey(Category, on_delete = models.SET_NULL, null = True)
  product_brand = models.ForeignKey(Brand, on_delete = models.SET_NULL, null = True)
  price = models.DecimalField(max_digits = 8, decimal_places = 2)
  offer_price = models.DecimalField(max_digits = 8, decimal_places = 2)
  thumbnail = models.ImageField(upload_to='thumbnail_images', null=True)

  
  is_active = models.BooleanField(default = False)
  created_at = models.DateTimeField(auto_now_add = True)
  updated_at = models.DateTimeField(auto_now_add = True)


    
  def __str__(self):
      return f"{self.product_brand.brand_name}-{self.product_name}"


class Product_Variant(models.Model):
  product = models.ForeignKey(Products, on_delete = models.CASCADE)
  colour_name = models.CharField(null = False)
  variant_stock = models.IntegerField(null = False)
  variant_status = models.BooleanField(default = True)
  colour_code= models.CharField(null = False)
  
 

class Product_images(models.Model):
   product = models.ForeignKey(Products,on_delete = models.CASCADE)
   images = models.ImageField(upload_to='product_images', default=r'C:\Users\sarat\Documents\ noimage.jpg' )
   def __str__(self):
      return f"Image for {self.product.product_name}" 
   
