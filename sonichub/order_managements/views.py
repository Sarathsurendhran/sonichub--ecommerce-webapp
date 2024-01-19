from django.shortcuts import render, redirect, get_object_or_404
from user_panel.models import Address, Transaction
from cart_management.models import Cart
from order_managements.models import Order_Main_data, Order_Sub_data
from user_panel.models import Address, Transaction
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
from coupon_management.models import Coupon, Users_Coupon
from django.contrib import messages
from django.db.models import Sum
from user_panel.views import wallet_balence


def order_return(request):
    if request.method == "POST":
        id = request.user.id
        amount = request.POST.get("total_amount")
        order_id = request.POST.get("order_id")
        main_order = Order_Main_data.objects.get(order_id=order_id)
        user_id = UserProfile.objects.get(id=id)
        main_order.order_status = "Returned"
        main_order.save()

        Transaction.objects.create(
            description="Returned Order " + order_id,
            amount=amount,
            transaction_type="Credit",
            user=user_id,
        )

    return redirect("order:order-list", id)


# payment success function for online order
def payment_success(request, order_id):
    order_id = "#" + order_id
    main_order_obj = Order_Main_data.objects.get(order_id=order_id)
    main_order_obj.payment_status = True
    main_order_obj.save()

    id = request.user.id
    # clearing the cart after payment
    data = Cart.objects.filter(user=id)
    data.delete()

    return render(request, "user_side/order-success.html", {"order_id": order_id})


def online_payment(request, order_id):
    order_instance = get_object_or_404(Order_Main_data, order_id=order_id)
    if order_instance.payment_status:
        return redirect("order:current-order-details", order_id)
    context = {
        "order_data": Order_Main_data.objects.get(order_id=order_id),
        "order_sub_data": Order_Sub_data.objects.filter(
            main_order_id=order_instance.id
        ),
    }
    return render(request, "user_side/online-payment-summary.html", context)


def cancel_order(request, order_id, user_id):
    if request.method == "POST":
        data = Order_Main_data.objects.get(order_id=order_id)
        data.order_status = "Cancelled"
        data.save()

        if (
            data.payment_option == "online payment"
            or data.payment_option == "wallet payment"
        ):
            amount = request.POST.get("total_amount")
            user = UserProfile.objects.get(id=user_id)

            transaction_data = Transaction.objects.create(
                user=user,
                description="Cancelled Order " + order_id,
                amount=amount,
                transaction_type="Credit",
            )

       
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

    order_main_data = (
        Order_Main_data.objects.filter(user_id=id).order_by("id").reverse()
    )

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

        # finding total
        sub_total = 0

        for i in data:
            if i.variant.variant_status:
                sub_total += i.quantity * i.product.offer_price

        order_status = request.POST.get("order_status")
        address = request.POST.get("addressId")
        payment_option = request.POST.get("payment_option")
        total_price = request.POST.get("total_price")
        coupon_code = request.POST.get("coupon_code")

        # coupon recheck...
        if coupon_code is not None and coupon_code != "None":
            try:
                coupon = Coupon.objects.get(
                    Coupon_code=coupon_code,
                    is_active=True,
                    expiry_date__gte=timezone.now().date(),
                    minimum_amount__lt=sub_total,
                )

                if sub_total > coupon.minimum_amount:
                    discount = float(coupon.discount)
                    amount = float(total_price) * (discount / 100)
                    total_price = round(float(total_price) - amount, 2)

                else:
                    messages.warning(request, "Invalid coupon")
                    return redirect("order:checkout", user)

            except Exception as e:
                print(e)
                messages.warning(request, "Enter valid coupon")
                return redirect("order:checkout", user)
            

        wallet_amount = wallet_balence(request, id)  
        
        if payment_option == "wallet payment":  
            if total_price > wallet_amount:
                messages.warning(request, "Insufficient Balence!")
                return redirect("order:checkout",id)

        current_date = timezone.now().date()
        formatted_date = current_date.strftime("%Y%m%d")
        r_string = get_random_string(length=2)
        address_id = Address.objects.get(id=address)
        user_id = UserProfile.objects.get(id=id)

        main_order = Order_Main_data.objects.create(
            total_amount=total_price,
            order_status=order_status,
            address=address_id,
            user=user_id,
            payment_option=payment_option,
        )
        order_id = "#" + str(formatted_date) + str(user) + str(main_order.id)
        main_order.order_id = order_id
        main_order.save()

        main_order_id = Order_Main_data.objects.get(id=main_order.id)

        for product in data:
            Order_Sub_data.objects.create(
                quantity=product.quantity,
                main_order=main_order_id,
                user=user_id,
                variant=product.variant,
            )

        if payment_option == "online payment":
            return redirect("order:online-payment", order_id)

        if payment_option == "wallet payment":
            return redirect("user_panel:wallet-payment", order_id, id)

        # clearing the cart
        data.delete()

        # changing coupon status
        if coupon_code is not None and coupon_code != "None":
            coupon = Coupon.objects.get(Coupon_code=coupon_code)
            coupon.is_active = False
            coupon.save()

        # creating razorpay object

        total_price_float = float(total_price)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_KEY_SECRET)
        )
        payment = client.order.create(
            {
                "amount": int(total_price_float * 100),
                "currency": "INR",
                "payment_capture": 1,
            }
        )
        main_order_id.payment_id = payment["id"]
        main_order_id.save()

        main_order_id.payment_status = True
        main_order_id.save()

        context = {"order_id": order_id, "address": address_id, "subtotal": sub_total}

        return render(request, "user_side/order-success.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkout(request, id):
    data = Cart.objects.filter(user=id)
    total_price = 0
    sub_total = 0
    coupon_code = None
    for i in data:
        if i.variant.variant_status:
            total_price += i.quantity * i.product.offer_price
            sub_total = total_price

    if request.method == "POST":
        try:
            coupon_code = request.POST.get("coupon code")

            coupon = Coupon.objects.get(
                Coupon_code=coupon_code,
                is_active=True,
                expiry_date__gte=timezone.now().date(),
            )

            if total_price > coupon.minimum_amount:
                discount = float(coupon.discount)
                amount = float(total_price) * (discount / 100)
                total_price = round(float(total_price) - amount, 2)
                coupon_id = coupon.id

            else:
                messages.warning(request, "Invalid coupon")

        except Exception as e:
            print(e)
            messages.warning(request, "Enter valid coupon")

    content = {
        "address": Address.objects.filter(user=id, status=True),
        "products": data,
        "total_price": total_price,
        "coupon_code": coupon_code,
        "subtotal": sub_total,
    }
    return render(request, "user_side/checkout.html", content)
