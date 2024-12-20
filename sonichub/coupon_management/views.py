from django.shortcuts import render, redirect
from django.http import JsonResponse
import random
import string
from coupon_management.models import Coupon,Users_Coupon
from cart_management.models import Cart
from datetime import datetime
from datetime import date  
from sonichub.decorators import superuser_required 

#admin side...


@superuser_required
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
        data.status=True
        data.save()
        return redirect("coupon:view-coupon")

    content={
        "coupon":Coupon.objects.get(id=id),
        "today_date":today_date
    }
    return render(request,"admin_side/edit-coupon.html",content)



@superuser_required
def coupon_status_change(request,coupon_id):
    data = Coupon.objects.get(id=coupon_id)
    if data.status:
        data.status = False
        data.save()
    else:
        data.status = True
        data.save()
    return redirect("coupon:view-coupon")


@superuser_required
def view_coupon(request):

    current_date_time = datetime.now()
    current_date = current_date_time.date()

    coupons = Coupon.objects.filter(expiry_date__lt=current_date)
    for coupon in coupons:
            coupon.status = False
            coupon.save()
    
    content={
        "coupons":Coupon.objects.all().order_by('id').reverse(),
        "current_date":current_date
    }
    return render(request,"admin_side/view-coupon.html",content)



@superuser_required
def generate_coupon(request):
    try:
        while True:
            character = string.ascii_letters + string.digits
            random_data = "".join(random.choice(character) for _ in range(8))
            if not Coupon.objects.filter(Coupon_code=random_data.upper()):
                return JsonResponse({"data": random_data.upper()})
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400}, status=400)


@superuser_required
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
