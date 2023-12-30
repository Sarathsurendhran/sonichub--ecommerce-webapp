from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate, logout
from product_management.models import Products,Product_Variant,Product_images
from brand_management.models import Brand
from category_management.models import Category
from django.views.decorators.cache import cache_control



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def shop_product(request,id):
  if not request.user.is_authenticated:
      return redirect('user_side:user_login')
  
  context = {
     'products':Products.objects.get(id = id),
     'variant_images':Product_Variant.objects.filter(product = id),
     'brands':Brand.objects.all(),
     'categories':Category.objects.all(),
     'images':Product_images.objects.filter(product = id)
  }
  
  return render(request, 'user_side/shop-product.html',context)
