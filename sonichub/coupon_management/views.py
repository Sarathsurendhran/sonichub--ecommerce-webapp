from django.shortcuts import render, redirect
from django.http import JsonResponse
import random
import string
from coupon_management.models import Coupon, Users_Coupon
from cart_management.models import Cart
from datetime import datetime
from datetime import date   

#admin side...


def edit_coupon(request,id):
    today_date = date.today().isoformat()
    if request.method == "POST":
        minimumamount = request.POST.get("minimumamount")
        discount = request.POST.get("discount")
        expirydate = request.POST.get("expirydate")
        coupon = request.POST.get("couponCode")

        data = Coupon.objects.get(id=id)
        data.minimum_amount=minimumamount
        data.discount=discount
        data.expiry_date=expirydate
        data.Coupon_code=coupon
        data.is_active=True
        data.save()
        return redirect("coupon:view-coupon")

    content={
        "coupon":Coupon.objects.get(id=id),
        "today_date":today_date
    }
    return render(request,"admin_side/edit-coupon.html",content)



def delete_coupon(request,coupon_id):
    data = Coupon.objects.get(id=coupon_id)
    data.delete()
    return redirect("coupon:view-coupon")


def view_coupon(request):

    current_date_time = datetime.now()
    current_date = current_date_time.date()
    print(current_date)

    coupons = Coupon.objects.filter(expiry_date__lt=current_date)
    for coupon in coupons:
            coupon.is_active = False
            coupon.save()
    
    content={
        "coupons":Coupon.objects.all(),
        "current_date":current_date
    }
    return render(request,"admin_side/view-coupon.html",content)



def generate_coupon(request):
    try:
        character = string.ascii_letters + string.digits
        random_data = "".join(random.choice(character) for _ in range(8))
        print(random_data)
        return JsonResponse({"data": random_data.upper()})
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400}, status=400)


def add_coupon(request):

    today_date = date.today().isoformat()
    
    if request.method == "POST":
        minimumamount = request.POST.get("minimumamount")
        discount = request.POST.get("discount")
        expirydate = request.POST.get("expirydate")
        coupon = request.POST.get("couponCode")
        

        Coupon.objects.create(
            minimum_amount=minimumamount,
            discount=discount,
            expiry_date=expirydate,
            Coupon_code=coupon,
        )
        return redirect("coupon:view-coupon")

    return render(request, "admin_side/add-coupon.html",{"today_date":today_date})
