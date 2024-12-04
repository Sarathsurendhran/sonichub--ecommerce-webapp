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
from django.views.decorators.cache import cache_control, never_cache
import json
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from product_management.models import Products, Product_Variant
from brand_management.models import Brand
from category_management.models import Category
import uuid
from django.urls import reverse
from user_panel.models import Transaction
from django.db import transaction
from cart_management.models import Cart
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

def about(request):
    return render(request, 'user_side/about.html')

def contact(request):
    return render(request, 'user_side/contact.html')

def forgot_password(request):
    if request.method == 'POST':
        email_id = request.POST.get('email')

        email_validate = EmailValidator()
        try:
            email_validate(email_id)
        except ValidationError as e:
            messages.warning(request, 'Please enter a valid email!')
            return redirect("user_side:user_login")

        if email_id:
            request.session['email'] = email_id
            request.session['value'] = 'forgotpassword'
            return redirect("user_side:send_otp")

        return redirect("user_side:user_login")




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_password(request):
    if request.method == "POST":
        try:
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm-password")

            if not password or not confirm_password:
                messages.warning(request, 'Password cannot be empty')
                return render(request, 'user_side/forgotpassword.html')
            
            if password != confirm_password:
                messages.warning(request, 'Password doesn\'t match')
                return render(request, 'user_side/forgotpassword.html')

            try:
                data = UserProfile.objects.get(email=request.session['email'])
            except UserProfile.DoesNotExist:
                messages.warning(request, 'User Profile not found')
                return render(request, 'user_side/forgotpassword.html')

            password = make_password(password)
            data.password = password
            data.save()

            del request.session['value']

            messages.success(request, 'Password changed successfully')
            return redirect("user_side:user_login")
        
        except Exception as e:
            messages.warning(request, 'Something went wrong!')
            return render(request, 'user_side/forgotpassword.html')

    return render(request, 'user_side/forgotpassword.html')


    

def referral_bonus(request):
    try:
        referral_code = request.session.get("referral_code")

        if referral_code:
            user = UserProfile.objects.get(id=request.user.id)
            referred_user = UserProfile.objects.get(referral_codes=referral_code)

            with transaction.atomic():
                Transaction.objects.create(
                    user=user,
                    description="Referral Signup",
                    amount="100",
                    transaction_type="Credit",
                )

                Transaction.objects.create(
                    user=referred_user,
                    description="Referral Bonus",
                    amount="301",
                    transaction_type="Credit",
                )

    except UserProfile.DoesNotExist:
        print("User or referred user does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")



def generate_referral_link(request):
    try:
        user_data = UserProfile.objects.get(id=request.user.id)
        signup_url = "https://sarathsurendhran.online/signup"
        referral_link = request.build_absolute_uri(
            signup_url + f"?referral_code={str(user_data.referral_codes)}"
        )
        return JsonResponse({"response": referral_link}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    
    context = {
        "products": Products.objects.all()[:8],
        "variants": Product_Variant.objects.all(),
        "brands": Brand.objects.all(),
        "categories": Category.objects.all(),
        
    }
    return render(request, "user_side/index.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signup(request):
    if request.user.is_authenticated:
        return redirect("user_side:index")

    if request.method != "POST":
        referral_code = request.GET.get("referral_code")
        request.session["referral_code"] = referral_code

        return render(request, "user_side/page-login-register.html")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        referral_code = request.session.get("referral_code")

        if (
            not username.strip()
            or not email.strip()
            or not phone_number.strip()
            or not password.strip()
            or not confirm_password.strip()
        ):
            messages.warning(request, "Avoid Space and Enter Details")
            return render(request, "user_side/page-login-register.html")

        if not re.match(r"^\d+$", phone_number):
            messages.warning(request, "Phone Number Should Only Contain Digits")
            return render(request, "user_side/page-login-register.html")

        if not re.match(r"^[a-zA-Z0-9]+$", username):
            messages.warning(
                request, "Username Should Only Contain AlphaNumeric Values"
            )
            return render(request, "user_side/page-login-register.html")

        try:
            validate_email(email)
        except:
            messages.warning(request, "Please enter a valid email address")
            return render(request, "user_side/page-login-register.html")

        if password != confirm_password:
            messages.warning(request, "Enter a valid e-mail address")

        else:
            try:
                if UserProfile.objects.filter(username=username).exists():
                    messages.warning(request, "Username is Already Taken")
                elif UserProfile.objects.filter(email=email).exists():
                    messages.warning(request, "Email is Already Taken")

                else:
                    myuser = UserProfile.objects.create_user(
                        email=email, phone_number=phone_number, password=password
                    )

                    request.session["email"] = email
                    return redirect("user_side:send_otp")

            except Exception as e:
                messages.error(request, f"An Error Occured: {str(e)}")

            return redirect("user_side:signup")


# wiillnbwbdzphfla
@csrf_exempt
def send_otp(request):
    
    otp = get_random_string(length=4, allowed_chars="0123456789")

    now = datetime.now().time()
    time_as_string = now.strftime("%H:%M:%S")

    request.session["otp"] = '1000'
    request.session["otp_time"] = time_as_string

    if 'value' in request.session:
        if request.session['value'] == 'forgotpassword':

            site_name = "Sonichub"
            subject = f"OTP for forgot password on {site_name}"
            message = f"Hi there!\n\nThanks for signing up on {site_name}.\n\nYour OTP is: {otp}\n\nPlease use this OTP to update your password.\n\nBest regards,\nThe {site_name} Team"

            # send_mail(
            #     subject,
            #     message,
            #     "teamlink904@gmail.com",
            #     [request.session["email"]],
            #     fail_silently=False,
            # )

        
    else:

        site_name = "Sonichub"
        subject = f"OTP for Sign Up on {site_name}"
        message = f"Hi there!\n\nThanks for signing up on {site_name}.\n\nYour OTP is: {otp}\n\nPlease use this OTP to verify your account.\n\nBest regards,\nThe {site_name} Team"

        send_mail(
            subject,
            message,
            "teamlink904@gmail.com",
            [request.session["email"]],
            fail_silently=False,
        )

    timenow = datetime.now()
    expire_time = timenow + timedelta(seconds=60)
    request.session["otp_expiration_time"] = expire_time.strftime("%H:%M:%S")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        response_data = {
            "success": True,
            "message": "OTP sent successfully.",
           
        }
        messages.success(request, "OTP sent successfully.")
        return JsonResponse(response_data)
        
    else:
        messages.success(request, "OTP sent successfully.")
        return redirect("user_side:verify_otp")

   
   

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def verify_otp(request):

    if request.user.is_authenticated:
        return redirect("user_side:index")
    
    if request.method == "POST":
        otp1 = request.POST.get("otp1")
        otp2 = request.POST.get("otp2")
        otp3 = request.POST.get("otp3")
        otp4 = request.POST.get("otp4")

        otp_entered = otp1 + otp2 + otp3 + otp4

        if "otp" in request.session:
            stored_otp = request.session["otp"]
            otp_expiration_time = request.session["otp_expiration_time"]
            expiration_time = datetime.strptime(otp_expiration_time, "%H:%M:%S").time()

            if otp_entered == stored_otp:
                current_time = datetime.now().time()

                
                user = UserProfile.objects.get(email=request.session['email'])

                if current_time <= expiration_time:
                    user.is_active = True
                    user.save()
                    login(request, user)

                    del request.session["otp"]
                    del request.session["otp_expiration_time"]

                    if 'value' in request.session:
                        if request.session['value'] == 'forgotpassword':
                            return redirect("user_side:update-password")
                        
                    
                    referral_bonus(request) #calling referral bonus function

                    messages.success(request, "UserProfile created successfully.")
                    return redirect("user_side:user_login")
                else:
                    messages.error(
                        request, "OTP has expired. Please request a new one."
                    )
            else:
                messages.error(request, "OTP doesn't match.")
        else:
            # Handle the case when OTP session variables are not found
            messages.error(request, "OTP verification failed. Please try again.")

    return render(request, "user_side/otp.html")




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
    if request.user.is_authenticated:
        return redirect("user_side:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email.strip() or not password.strip():
            messages.warning(request, "Avoid Space and Enter Details")
            return redirect("user_side:user_login")

        userprofile = None

        try:
            userprofile = UserProfile.objects.get(email=email)

            if not userprofile.is_active:
                messages.warning(request, "Your UserProfile is blocked")
                return redirect("user_side:user_login")

        except UserProfile.DoesNotExist:
            messages.warning(request, "No user found")
            return redirect("user_side:user_login")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("user_side:index")

        else:
            messages.error(request, "Invalid details")

    return render(request, "user_side/login.html")
