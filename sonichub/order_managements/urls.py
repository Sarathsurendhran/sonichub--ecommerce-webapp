from django.urls import path
from .import views

app_name="order"

urlpatterns = [
    path('confirm-order/<int:id>',views.confirm_order,name='confirm-order'),
    path('checkout/<int:id>',views.checkout,name='checkout'),
    path('current-order-details/<str:order_id>',views.current_order_details,name='current-order-details'),
    path('order-list/<int:id>',views.order_list,name='order-list'),
    path('order-details/<int:id>',views.order_details,name='order-details')
    
    
]