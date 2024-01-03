from django.urls import path
from user_panel import views

app_name = 'user_panel'

urlpatterns = [
  path('shop-product/<int:id>',views.shop_product,name='shop-product'),
  path('user-profile/<int:id>',views.user_profile,name='user-profile'),
  path('logout_user',views.logout_user,name='logout_user'),

]