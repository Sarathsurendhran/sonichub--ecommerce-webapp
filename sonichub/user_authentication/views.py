from django.shortcuts import render, redirect
from django.contrib import messages
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserProfile 
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.cache import cache_control,never_cache
import json
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from product_management.models import Products,Product_Variant
from brand_management.models import Brand
from category_management.models import Category

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
  context = {
     'products':Products.objects.all(),
     'variants':Product_Variant.objects.all(),
     'brands':Brand.objects.all(),
     'categories':Category.objects.all(),
  }
  return render(request, 'user_side/index.html',context)

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signup(request):

  if request.user.is_authenticated:
    return redirect('user_side:index')
  
  if request.method != "POST":
      return render(request, 'user_side/page-login-register.html')
  
  if request.method == 'POST':
    username = request.POST.get('username')
    email = request.POST.get('email')
    phone_number = request.POST.get('phone_number')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    if not username.strip() or not email.strip() or not phone_number.strip() or not password.strip() or not confirm_password.strip():
      messages.warning(request, 'Avoid Space and Enter Details')
      return render(request, 'user_side/page-login-register.html' )
    
    if not re.match(r'^\d+$', phone_number):
      messages.warning(request, 'Phone Number Should Only Contain Digits')
      return render(request, 'user_side/page-login-register.html')
    
    if not re.match(r'^[a-zA-Z0-9]+$', username):
      messages.warning(request, 'Username Should Only Contain AlphaNumeric Values')
      return render(request, 'user_side/page-login-register.html')
    
    try:
      validate_email(email)
    except:
      messages.warning(request, 'Please enter a valid email address')
      return render(request, 'user_side/page-login-register.html')
    
    if password != confirm_password:
      messages.warning(request,'Enter a valid e-mail address')

    else:

      try:

        if UserProfile.objects.filter(username = username).exists():
          messages.warning(request, 'Username is Already Taken')
        elif UserProfile.objects.filter(email = email).exists():
          messages.warning(request, 'Email is Already Taken')
        else:
          myuser = UserProfile.objects.create_user(email = email, phone_number = phone_number, password = password)

          request.session['email'] = email
          return redirect("user_side:send_otp")

      except Exception as e:
        messages.error(request, f"An Error Occured: {str(e)}")

      return redirect("user_side:signup")

      
 
      

@never_cache
# wiillnbwbdzphfla
@csrf_exempt
def send_otp(request):
        
        otp = get_random_string(length=4, allowed_chars='0123456789')

        now = datetime.now().time()
        time_as_string = now.strftime("%H:%M:%S")
        
        request.session["otp"] = otp
        request.session["otp_time"] = time_as_string

        send_mail("OTP for sign up", f"Hi Your OTP is: {otp}", 'sonichubecommerce@outlook.com',[request.session['email']], fail_silently=False)

        timenow = datetime.now()
        expire_time = timenow + timedelta(seconds=60)
        request.session["otp_expiration_time"] = expire_time.strftime("%H:%M:%S")

        messages.success(request, "OTP sent successfully.")
        JsonResponse({'success': 'OTP sent successfully'}, status = 200)

        return redirect("user_side:verify_otp")

   
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def verify_otp(request):

    if request.method == 'POST':
        otp_entered = request.POST.get("otp")

        if "otp" in request.session:
            stored_otp = request.session["otp"]
            otp_expiration_time = request.session["otp_expiration_time"]
            expiration_time = datetime.strptime(otp_expiration_time , "%H:%M:%S").time()

            if otp_entered == stored_otp:
                current_time = datetime.now().time()

                user = UserProfile.objects.get(email=request.session["email"])

                if current_time <=  expiration_time:
                    
                    user.is_active = True
                    user.save()
                    login(request, user)
                   
                    del request.session["otp"]
                    del request.session["otp_expiration_time"]

                    messages.success(request, "UserProfile created successfully.")
                    return redirect('user_side:user_login')
                else:
                    messages.error(request, "OTP has expired. Please request a new one.")
            else:
                messages.error(request, "OTP doesn't match.")
        else:
            # Handle the case when OTP session variables are not found
            messages.error(request, "OTP verification failed. Please try again.")
        
    return render(request, 'user_side/otp.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
    
    if request.user.is_authenticated:
       return redirect('user_side:index')
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email.strip() or not password.strip() :
              messages.warning(request, 'Avoid Space and Enter Details')
              return redirect('user_side:user_login')

        userprofile=None

        try:
            userprofile = UserProfile.objects.get(email=email)

            if not userprofile.is_active:
                messages.warning(request, "Your UserProfile is blocked")
                return redirect("user_side:user_login")
            
        except userprofile.DoesNotExist:
            messages.warning(request, "No user found")
            return redirect("user_side:user_login")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("user_side:index")
            
        else:
            messages.error(request, "Invalid details")

    return render(request, "user_side/login.html")



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_profile(request):
   if not request.user.is_authenticated:
          return redirect('user_side:user_login')
   return render(request, 'user_side/user_profile.html')


def logout_user(request):
    if not request.user.is_authenticated:
          return redirect('user_side:user_login')
    logout(request)
    return redirect("user_side:index")


