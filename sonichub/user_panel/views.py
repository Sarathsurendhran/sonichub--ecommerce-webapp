from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from product_management.models import Products, Product_Variant, Product_images
from brand_management.models import Brand
from category_management.models import Category
from django.views.decorators.cache import cache_control
from user_authentication.models import UserProfile
from user_panel.models import Address
from django.contrib import messages
from django.http import Http404
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_password(request, id):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        data = UserProfile.objects.get(id=id)

        if data.check_password(current_password):
            password = make_password(new_password)
            data.password = password
            data.save()
            request.session["email"] = data.email
            return redirect('user_panel:update-mail-otp')
        else:
           messages.warning(request, "Current Password is not correct")

    return render(request, "user_side/change-password.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def shop_product(request, id):
    if not request.user.is_authenticated:
        return redirect("user_side:user_login")

    context = {
        "products": Products.objects.get(id=id),
        "variants": Product_Variant.objects.filter(product=id),
        "brands": Brand.objects.all(),
        "categories": Category.objects.all(),
        "images": Product_images.objects.filter(product=id),
    }

    return render(request, "user_side/shop-product.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_profile(request, id):
    if not request.user.is_authenticated:
        return redirect("user_side:user_login")
    content = {
        "users": UserProfile.objects.get(id=id),
    }
    return render(request, "user_side/user_profile.html", content)


def logout_user(request):
    if not request.user.is_authenticated:
        return redirect("user_side:user_login")
    logout(request)
    return redirect("user_side:index")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_address(request, id):
    try:
        user_id = UserProfile.objects.get(id=id)
    except UserProfile.DoesNotExist:
        raise Http404("User profile does not exist")

    if request.method == "POST":
        try:
            name = request.POST.get("name")
            house_name = request.POST.get("house_name")
            street_name = request.POST.get("street_name")
            district = request.POST.get("district")
            state = request.POST.get("state")
            pin_number = request.POST.get("pin_number")
            country = request.POST.get("country")
            phone_number = request.POST.get("phone_number")

            Address.objects.create(
                name=name,
                house_name=house_name,
                street_name=street_name,
                district=district,
                state=state,
                pin_number=pin_number,
                country=country,
                phone_number=phone_number,
                user=user_id,
            )
            messages.success(request, "Address Added Successfully")
            return redirect("user_panel:address-list", id)

        except Exception as e:
            messages.error(request, f"Error adding address: {str(e)}")

    return render(request, "user_side/add-address.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_profile(request, id):
    if not request.user.is_authenticated:
        return redirect("user_side:user_login")
    if request.method == "POST":
        name = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")

        print(name,email,phone_number)

    try:
        if UserProfile.objects.filter(username=name).exclude(id=id).exists():
            messages.warning(request, "Username is Already Taken")
        elif UserProfile.objects.filter(email=email).exclude(id=id).exists():
            messages.warning(request, "Email is Already Taken")
        else:
            data = UserProfile.objects.get(id=id)
            data.username = name
            data.email = email
            data.phone_number = phone_number
            data.save()

            request.session["email"] = email

            return redirect("user_panel:update-mail-otp")
    except Exception as e:
        print(e)

    content = {"users": UserProfile.objects.get(id=id)}
    return render(request, "user_side/edit-profile.html", content)


# wiillnbwbdzphfla
@csrf_exempt
#@login_required(login_url="user_side:user_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_mail_otp(request):

    otp = get_random_string(length=4, allowed_chars="0123456789")

    now = datetime.now().time()
    time_as_string = now.strftime("%H:%M:%S")

    request.session["otp"] = otp
    request.session["otp_time"] = time_as_string

    send_mail("OTP for sign up", f"Hi {request.user} Your OTP is: {otp}", 'sonichubecommerce@outlook.com',[request.session['email']], fail_silently=False)

    timenow = datetime.now()
    expire_time = timenow + timedelta(seconds=60)
    request.session["otp_expiration_time"] = expire_time.strftime("%H:%M:%S")
    print(request.session["email"])

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        response_data = {
            "success": True,
            "message": "OTP sent successfully.",
            "email": request.session.get("email", ""),
        }
        return JsonResponse(response_data)
    else:
        messages.success(request, "OTP sent successfully.")
        return redirect("user_panel:update-mail-verify-otp")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_mail_verify_otp(request):
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

                user = UserProfile.objects.get(email=request.session["email"])

                if current_time <= expiration_time:
                    

                    user.is_active = True
                    user.save()

                    del request.session["otp"]
                    del request.session["otp_expiration_time"]

                    messages.success(request, "Updated successfully.")
                    return redirect("user_panel:user-profile", user.id)
                else:
                    messages.error(
                        request, "OTP has expired. Please request a new one."
                    )
            else:
                messages.error(request, "OTP doesn't match.")
        else:
            messages.error(request, "OTP verification failed. Please try again.")

    return render(request, "user_side/email-update-otp.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def address_list(request, id):
    content = {"address": Address.objects.filter(user_id=id)}

    return render(request, "user_side/address-list.html", content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_address(request, id):
    user_id = request.user.id

    if request.method == "POST":
        try:
            address_instance = Address.objects.get(id=id)

            address_instance.name = request.POST.get("name")
            address_instance.house_name = request.POST.get("house_name")
            address_instance.street_name = request.POST.get("street_name")
            address_instance.district = request.POST.get("district")
            address_instance.state = request.POST.get("state")
            address_instance.pin_number = request.POST.get("pin_number")
            address_instance.country = request.POST.get("country")
            address_instance.phone_number = request.POST.get("phone_number")

            address_instance.save()

            messages.success(request, "Address Updated Successfully")
            return redirect("user_panel:address-list", user_id)

        except Exception as e:
            messages.error(request, f"Error adding address: {str(e)}")

    content = {"address": Address.objects.get(id=id)}

    return render(request, "user_side/edit-address.html", content)


def address_status_change(request, id):
    user_id = request.user.id
    print(user_id)
    id = Address.objects.get(id=id)
    id.status = False
    id.save()
    return redirect("user_panel:address-list", user_id)
