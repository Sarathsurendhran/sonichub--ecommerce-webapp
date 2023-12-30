
from django.urls import path
from user_authentication import views

app_name = 'user_side'

urlpatterns = [
    path('',views.index, name = 'index'),
    path('signup', views.signup, name='signup'),
    path('send_otp',views.send_otp,name='send_otp'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
    path('user_login',views.user_login, name='user_login'),
    path('user_profile',views.user_profile,name='user_profile'),
    path('logout_user',views.logout_user,name='logout_user'),

]
