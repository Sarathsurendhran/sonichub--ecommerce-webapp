from django.urls import path
from .import views

app_name='coupon'

urlpatterns=[
  path('add-coupon',views.add_coupon,name='add-coupon'),
  path('generate-coupon',views.generate_coupon,name="generate-coupon"),
  path('view-coupon',views.view_coupon,name='view-coupon'),
  path('coupon-status-change/<int:coupon_id>',views.coupon_status_change,name="coupon-status-change"),
  path('edit-coupon/<int:id>',views.edit_coupon,name="edit-coupon"),
  path('add-coupon/<int:id>',views.add_coupon,name="add-coupon") 

]