from django.urls import path
from . import views

app_name ='cart'

urlpatterns = [
  path('product-cart',views.product_cart,name='product-cart'),

]