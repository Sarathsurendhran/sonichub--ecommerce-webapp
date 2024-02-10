from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from product_management.models import Products, Product_Variant, Product_images
from brand_management.models import Brand
from category_management.models import Category
from django.views.decorators.cache import cache_control, never_cache
from user_authentication.models import UserProfile
from user_panel.models import Address, Transaction, Wishlist
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseBadRequest,
)
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import transaction
from order_managements.models import Order_Main_data
from cart_management.models import Cart
from category_management.models import Category
from django.db.models import Q
from django.core.serializers import serialize
import json
from django.contrib.auth.decorators import login_required
from coupon_management.models import Coupon, Users_Coupon



# wiillnbwbdzphfla
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_password_otp(request):

    # try:
    #     request.session['email'] = request.POST.get('email')
        
    # except:
    #     pass

    otp = get_random_string(length=4, allowed_chars="0123456789")

    now = datetime.now().time()
    time_as_string = now.strftime("%H:%M:%S")

    request.session["otp"] = otp
    request.session["otp_time"] = time_as_string

    print("in send otp")
    for key, value in request.session.items():
                print(f"{key}: {value}")


    site_name = "Sonichub"
    subject = f"OTP for Change Password on {site_name}"
    message = f"Hi {request.user},\n\nThanks for updating your data on {site_name}.\n\nYour OTP for the update is: {otp}\n\nPlease use this OTP to change your password.\n\nBest regards,\nThe {site_name} Team"
    email = request.session.get("email")

    send_mail(
        subject,
        message,
        "sonichubecommerce@outlook.com",
        [email],
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
        return redirect("user_panel:update-password-verify-otp")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_password_verify_otp(request):
    if request.method == "POST":
        otp1 = request.POST.get("otp1")
        otp2 = request.POST.get("otp2")
        otp3 = request.POST.get("otp3")
        otp4 = request.POST.get("otp4")
        otp_entered = otp1 + otp2 + otp3 + otp4

        print("session in verify otp")
        for key, value in request.session.items():
                     print(f"{key}: {value}")
        
        if "otp" in request.session:
            print("entered inside otp section")
            stored_otp = request.session["otp"]
            otp_expiration_time = request.session["otp_expiration_time"]
            expiration_time = datetime.strptime(otp_expiration_time, "%H:%M:%S").time()

            if otp_entered == stored_otp:
                current_time = datetime.now().time()

                user = UserProfile.objects.get(id=request.user.id)

                if current_time <= expiration_time:
                    user.is_active = True
                    user.save()

                    del request.session["otp"]
                    del request.session["otp_expiration_time"]

                    request.session["otp-status"] = 'otp-verified'

                    return redirect("user_panel:change-password") 
                    
                else:
                    messages.error(
                        request, "OTP has expired. Please request a new one."
                    )
            else:
                messages.error(request, "OTP doesn't match.")
        else:
            messages.error(request, "OTP verification failed. Please try again.")

    return render(request, "user_side/change_password_otp.html")


def add_new(request):
    if request.method == "GET":
        selected_values = request.GET.getlist('brand')
        if selected_values:
            print(selected_values)

    content ={
        "data":Brand.objects.all(),
        "category":Category.objects.all()
    }
    return render(request, 'user_side/new-file.html',content)


def update_mail(request):
    try:
        email = request.session['email']
        data = UserProfile.objects.get(id=request.user.id)
        data.email = email
        data.save()
        messages.success(request, 'Email updated successfully')
        
    except Exception as e:
        print(e)
        messages.warning(request, 'Something went wrong!')
    
    return redirect("user_panel:user-profile",request.user.id)


def category_show(request, id):
    try:
        products = Products.objects.filter(product_category=id)
        print(products)
    except:
        pass

    return render(request,"user_side/index.html",{"products":products})


def brows_categories(request):
    try:
        categories = Category.objects.filter(is_available=True)
        serialized_data = serialize('json', categories)

        # Convert the serialized data to a list
        categories_list = json.loads(serialized_data)
      

    except Exception as e:
        print(e)
        categories_list = []
       
    return JsonResponse({"data": categories_list})
    

@login_required(login_url='user_side:user_login')
def add_to_wishlist(request):
    if request.method == "POST":
        try:
            product = request.POST.get("product")
            user = request.user.id
            user_id = UserProfile.objects.get(id=user)
            product_id = Products.objects.get(id=product)
            variant = Product_Variant.objects.filter(
                product=product_id, variant_status=True
            ).first()

            if not Wishlist.objects.filter(user=user_id, variant=variant):
                Wishlist.objects.create(user=user_id, variant=variant)
                return JsonResponse({"status": "success"}, status=200)
            else:
                return JsonResponse({"status": "Item already in wishlist"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error"}, status=403)


def remove_wishlist(request, id):
    if request.method == "POST":
        data = Wishlist.objects.get(id=id)
        data.delete()
        return redirect("user_panel:wish-list")
    messages.warning(request, "something went wrong!")
    return redirect("user_panel:wish-list")




def wish_list(request):
    user_id = UserProfile.objects.get(id=request.user.id)
    if request.method == "POST":
        variant = request.POST.get("variant_id")
        variant_id = Product_Variant.objects.get(id=variant)
        Wishlist.objects.create(user=user_id, variant=variant_id)
    content = {"wishlist": Wishlist.objects.filter(user=user_id)}
    return render(request, "user_side/wish-list.html", content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_search(request, name):
    try:
        products = Products.objects.filter(
            product_category__category_name__icontains=name
        )
        print(products)
        if products.exists():
            return render(
                request, "user_side/search-result.html", {"products": products}
            )
        else:
            print("not found")
            return render(request, "user_side/search-result.html")
    except Exception as e:
        print(e)
        return render(request, "user_side/search-result.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_names(request):
    if request.method == "POST":
        try:
            query = request.POST.get("search_product")
            products = Products.objects.filter(
                Q(product_category__category_name__icontains=query)
                | Q(product_name__icontains=query)
                | Q(product_brand__brand_name__icontains=query)
            )

            if products.exists():
                return render(
                    request, "user_side/search-result.html", {"products": products}
                )
            else:
                print("not found")
                return render(request, "user_side/search-result.html")
        except Exception as e:
            print(e)
            return render(request, "user_side/search-result.html")
    return redirect("/")


# calculating total wallet amount


def wallet_balence(request, user_id):
    datas = Transaction.objects.filter(user=user_id)
    grand_total = 0
    for data in datas:
        if data.transaction_type == "Credit":
            grand_total += data.amount
        else:
            grand_total -= data.amount
    return grand_total


def wallet_payment(request, order_id, id, coupon_code=None):
    order_main = Order_Main_data.objects.get(order_id=order_id)

    user = UserProfile.objects.get(id=id)
    wallet_amount = wallet_balence(request, id)

    if order_main.total_amount > wallet_amount:
        messages.warning(request, "Insufficient Balence!")
        return redirect("order:checkout", user.id)

    order_main.payment_status = True
    order_main.save()

    if coupon_code is not None and coupon_code != "None":
        coupon = Coupon.objects.get(Coupon_code=coupon_code)
        user = UserProfile.objects.get(id=request.user.id)
        Users_Coupon.objects.create(
            user=user,
            coupon_code=coupon.Coupon_code,
            coupon_discount=coupon.discount,
            order_id=order_main
            
        )

    Transaction.objects.create(
        user=user,
        description="Placed Order  " + order_id,
        amount=order_main.total_amount,
        transaction_type="Debit",
    )

    # clearing the cart after payment
    data = Cart.objects.filter(user=id)
    data.delete()

    return render(request, "user_side/order-success.html", {"order_id": order_id})


def user_wallet(request, user_id):
    total = wallet_balence(request, user_id)

    content = {
        "TransactionHistory": Transaction.objects.filter(user=user_id)
        .order_by("id")
        .reverse(),
        "wallet_total": total,
    }

    return render(request, "user_side/user-wallet.html", content)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_password(request):
    try:
        user = UserProfile.objects.get(id=request.user.id)
        otp_status = request.session.get("otp-status")
        if otp_status == "otp-verified":
            new_password = request.session.get("new_password")
            if new_password:
                password = make_password(new_password)
                user.password = password
                user.save()
                del request.session["new_password"]
            return redirect("user_panel:user-profile", request.user.id)

    except UserProfile.DoesNotExist:
        messages.error(request, "User profile does not exist.")
        return redirect("user_panel:user-profile", request.user.id)
    
    except Exception as e:
        print(e)
        messages.error(request, "An error occurred.")
        return redirect("user_panel:user-profile", request.user.id) 

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password") 
        if user.check_password(current_password):
            request.session["email"] = user.email
            request.session["new_password"] = new_password
            return redirect("user_panel:update-password-otp")
        else:
            messages.warning(request, "Current Password is not correct")

    return render(request, "user_side/change-password.html")



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def shop_product(request, id):
    if not request.user.is_authenticated:
        return redirect("user_side:user_login")
    
    variants = Product_Variant.objects.filter(product=id)
 

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
            name = request.POST.get("name").strip()
            house_name = request.POST.get("house_name").strip()
            street_name = request.POST.get("street_name").strip()
            district = request.POST.get("district").strip()
            state = request.POST.get("state").strip()
            pin_number = request.POST.get("pin_number").strip()
            country = request.POST.get("country").strip()
            phone_number = request.POST.get("phone_number").strip()

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
        #email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")


    try:
        if UserProfile.objects.filter(username=name).exclude(id=id).exists():
            messages.warning(request, "Username is Already Taken")
        # elif UserProfile.objects.filter(email=email).exclude(id=id).exists():
        #     messages.warning(request, "Email is Already Taken")
        else:
            data = UserProfile.objects.get(id=id)
            data.username = name
            data.phone_number = phone_number
            data.save()
            messages.success(request, "Profile updated successfully")
    except Exception as e:
        print(e)

    content = {"users": UserProfile.objects.get(id=id)}
    return render(request, "user_side/edit-profile.html", content)


# wiillnbwbdzphfla
@csrf_exempt
# @login_required(login_url="user_side:user_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_mail_otp(request):

    try:
        request.session['email'] = request.POST.get('email')
        
    except:
        pass

    otp = get_random_string(length=4, allowed_chars="0123456789")

    now = datetime.now().time()
    time_as_string = now.strftime("%H:%M:%S")

    request.session["otp"] = otp
    request.session["otp_time"] = time_as_string

    site_name = "Sonichub"
    subject = f"OTP for Data Update on {site_name}"
    message = f"Hi {request.user},\n\nThanks for updating your data on {site_name}.\n\nYour OTP for the update is: {otp}\n\nPlease use this OTP to confirm the changes.\n\nBest regards,\nThe {site_name} Team"

    send_mail(
        subject,
        message,
        "sonichubecommerce@outlook.com",
        [request.session["email"]],
        fail_silently=False,
    )

    timenow = datetime.now()
    expire_time = timenow + timedelta(seconds=60)
    request.session["otp_expiration_time"] = expire_time.strftime("%H:%M:%S")
    print(request.session["email"])

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        response_data = {
            "success": True,
            "message": "OTP sent successfully.",
           
        }
        messages.success(request, "OTP sent successfully.")
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

                user = UserProfile.objects.get(id=request.user.id)

                if current_time <= expiration_time:
                    user.is_active = True
                    user.save()

                    del request.session["otp"]
                    del request.session["otp_expiration_time"]

                    return redirect("user_panel:update-mail")
                    
                else:
                    messages.error(
                        request, "OTP has expired. Please request a new one."
                    )
            else:
                messages.error(request, "OTP doesn't match.")
        else:
            messages.error(request, "OTP verification failed. Please try again.")

    return render(request, "user_side/otp-for-profile.html")



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
