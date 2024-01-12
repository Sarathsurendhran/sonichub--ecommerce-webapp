from django.shortcuts import render, redirect,get_object_or_404
from user_panel.models import Address
from cart_management.models import Cart
from order_managements.models import Order_Main_data, Order_Sub_data
from user_panel.models import Address
from user_authentication.models import UserProfile
from django.utils import timezone
from product_management.models import Product_Variant
from django.views.decorators.cache import cache_control
from django.utils.crypto import get_random_string
from collections import defaultdict
from django.db.models import Prefetch
from django.http import HttpResponse
import razorpay
from django.conf import settings


def payment_success(request,order_id):
    order_id = '#'+ order_id
    main_order_obj = Order_Main_data.objects.get(order_id=order_id)
    main_order_obj.payment_status = True
    main_order_obj.save()
    return render(request,'user_side/order-success.html',{"order_id": order_id})


def online_payment(request,order_id):
    order_instance = get_object_or_404(Order_Main_data, order_id=order_id)
    if order_instance.payment_status:
        return redirect("order:current-order-details",order_id)
    context ={
        "order_data":Order_Main_data.objects.get(order_id=order_id),
        "order_sub_data":Order_Sub_data.objects.filter(main_order_id=order_instance.id)
    } 
    return render(request,"user_side/online-payment-summary.html",context)



def cancel_order(request, order_id, user_id):
    if request.method == "POST":
        data = Order_Main_data.objects.get(order_id=order_id)
        data.order_status = "Cancelled"
        data.save()
        return redirect("order:order-list", user_id)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_details(request, id):
    content = {
        "order_main": Order_Main_data.objects.get(id=id),
        "order_sub_data": Order_Sub_data.objects.filter(main_order_id=id),
    }
    return render(request, "user_side/order-details.html", content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_list(request, id):
    print(id)

    order_main_data = Order_Main_data.objects.filter(user_id=id)

    grouped_data = defaultdict(list)

    for data in order_main_data:
        order_sub_data = data.order_sub_data_set.all()
        grouped_data[data.order_id] = order_sub_data

    context = {"grouped_order_data": dict(grouped_data)}
    return render(request, "user_side/order-list.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def current_order_details(request, order_id):
    order_main = Order_Main_data.objects.get(order_id=order_id)
    content = {
        "order_main": Order_Main_data.objects.get(order_id=order_id),
        "order_sub": Order_Sub_data.objects.filter(main_order_id=order_main.id),
    }
    return render(request, "user_side/current-order-details.html", content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def confirm_order(request, id):
    if request.method == "POST":
        user = request.user.id
        data = Cart.objects.filter(user=id)
        if not data:
            return redirect("cart:product-cart")

        order_status = request.POST.get("order_status")
        address = request.POST.get("addressId")
        payment_option = request.POST.get("payment_option")
        current_date = timezone.now().date()
        formatted_date = current_date.strftime("%Y%m%d")
        r_string = get_random_string(length=2)
        address_id = Address.objects.get(id=address)
        user_id = UserProfile.objects.get(id=id)
        order_id = "#" + str(formatted_date) + str(user) + r_string.upper()
        total_price = 0

        for i in data:
            if i.variant.variant_status:
                total_price += i.quantity * i.product.offer_price

        main_order = Order_Main_data.objects.create(
            total_amount=total_price,
            order_status=order_status,
            address=address_id,
            user=user_id,
            payment_option=payment_option,
            order_id=order_id,
        )

        main_order_id = Order_Main_data.objects.get(id=main_order.id)

        for product in data:
            Order_Sub_data.objects.create(
                quantity=product.quantity,
                main_order=main_order_id,
                user=user_id,
                variant=product.variant,
            )
        data.delete()

        total_price_float = float(total_price)

        client =razorpay.Client(auth=(settings.RAZORPAY_KEY,settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({
            'amount':int(total_price_float * 100), 'currency': 'INR', 'payment_capture': 1})
        main_order_id.payment_id = payment['id']
        main_order_id.save()

        if payment_option == 'online payment':
            return redirect('order:online-payment',order_id)
        

        context = {"order_id": order_id, "address": address_id}

        return render(request, "user_side/order-success.html", context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkout(request, id):
    data = Cart.objects.filter(user=id)
    total_price = 0
    for i in data:
        if i.variant.variant_status:
            total_price += i.quantity * i.product.offer_price

    content = {
        "address": Address.objects.filter(user=id, status=True),
        "products": data,
        "total_price": total_price,
    }
    return render(request, "user_side/checkout.html", content)


