from django.urls import path
from user_panel import views

app_name = 'user_panel'

urlpatterns = [
  path('shop-product/<int:id>',views.shop_product,name='shop-product')

]