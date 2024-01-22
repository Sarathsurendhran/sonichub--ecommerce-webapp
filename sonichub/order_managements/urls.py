from django.urls import path
from .import views

app_name="order"

urlpatterns = [
    path('confirm-order/<int:id>',views.confirm_order,name='confirm-order'),
    path('checkout/<int:id>',views.checkout,name='checkout'),
    path('current-order-details/<str:order_id>',views.current_order_details,name='current-order-details'),
    path('order-list/<int:id>',views.order_list,name='order-list'),
    path('order-details/<int:id>',views.order_details,name='order-details'),
    path('cancel-order/<str:order_id>/<int:user_id>',views.cancel_order,name='cancel-order'),
    path('online-payment/<str:order_id>/<str:coupon_code>',views.online_payment,name='online-payment'),
    path('payment-success/<str:order_id>',views.payment_success,name='payment-success'),
    path('order-return',views.order_return,name="order-return"),
    path('generate-pdf/<str:order_id>',views.generate_pdf, name='generate-pdf')
    
    
      
    
    
]