from django.urls import path
from .import views

app_name="order"

urlpatterns = [
    path('order/<int:id>',views.order,name='order'),
    path('checkout/<int:id>',views.checkout,name='checkout')

]