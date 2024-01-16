from django.urls import path
from user_panel import views

app_name = 'user_panel'

urlpatterns = [
  path('shop-product/<int:id>',views.shop_product,name='shop-product'),
  path('user-profile/<int:id>',views.user_profile,name='user-profile'),
  path('logout_user',views.logout_user,name='logout_user'),
  path('add-address/<int:id>',views.add_address,name='add-address'),
  path('edit-profile/<int:id>',views.edit_profile,name='edit-profile'),
  path('update-mail-otp',views.update_mail_otp,name='update-mail-otp'),
  path('update-mail-verify-otp',views.update_mail_verify_otp,name='update-mail-verify-otp'),
  path('address-list/<int:id>',views.address_list,name='address-list'),
  path('edit-address/<int:id>',views.edit_address,name='edit-address'),
  path('address-status-change/<int:id>',views.address_status_change,name='address-status-change'),
  path('change-password/<int:id>',views.change_password,name='change-password'),
  path('user-wallet/<int:user_id>',views.user_wallet,name='user-wallet'),
  path('wallet-payment/<str:order_id>/<int:id>',views.wallet_payment,name='wallet-payment')
  

]