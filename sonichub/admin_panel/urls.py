from django.urls import path
from admin_panel import views

app_name = 'admin_panel'

urlpatterns = [

  path('',views.admin_login, name='admin_login'),
  path('admin_dashboard',views.admin_dashboard, name='admin_dashboard'),
  path('users_list',views.users_list,name='users_list'),
  path('block_unblock_user/<int:id>/',views.block_unblock_user, name= 'block_unblock_user'),
  path('order-list',views.order_list,name='order-list'),
  path('order-status-change',views.order_status_change,name='order-status-change')


]