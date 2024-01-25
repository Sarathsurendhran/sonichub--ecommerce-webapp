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
from django.db.models.signals import post_save
from django.dispatch import receiver
from category_management.models import Category
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from decimal import Decimal
from datetime import date


def cancel_individual_product(request, order_sub_id):
    data = Order_Sub_data.objects.get(id=order_sub_id)
    data.is_active = False
    data.save()

    user_id = UserProfile.objects.get(id=request.user.id)

    order_main = Order_Main_data.objects.get(id=data.main_order.id)

    find_sub_total = Order_Sub_data.objects.filter(main_order=order_main.id)
    sub_total = 0

    
    
    # credit cash on wallet when cancel individual product
    
    if (
            order_main.payment_option == "online payment"
            or order_main.payment_option == "wallet payment"
        ):


        price = data.variant.product.offer_price
        offer_discount = data.variant.product.product_category.discount
        
        if offer_discount:
            discount_total = float(price) * (offer_discount / 100)
            price = float(price) - discount_total

        Transaction.objects.create(
                description="Cancelled Product    " +  data.variant.product.product_name,
                amount=price,
                transaction_type="Credit",
                user=user_id,
            )    

    for i in find_sub_total:
        if not i.is_active:
            continue

        unit_price = i.variant.product.offer_price
        if i.variant.product.product_category.discount:
            category_discount = int(i.variant.product.product_category.discount)
            total_discount = float(unit_price) * (category_discount / 100)
            unit_price = float(unit_price) - total_discount

        if i.variant.variant_status:
            sub_total += float(unit_price)
            
    order_main.total_amount = sub_total
    order_main.save()

    order_sub_data = Order_Sub_data.objects.filter(
        main_order=order_main.id, is_active=False
    ).count()
    order_sub_data_total = Order_Sub_data.objects.filter(
        main_order=order_main.id
    ).count()

    if order_sub_data == order_sub_data_total:
        order_main.order_status = "Cancelled"
        order_main.save()

        return redirect("order:order-details", order_main.id)

    return redirect("order:order-details", order_main.id)




def generate_pdf(request, order_id):
    order_main = Order_Main_data.objects.get(order_id=order_id)
    order_sub_data = Order_Sub_data.objects.filter(main_order_id=order_main.id)

    content = {
        "order_main": order_main,
        "order_sub_data": order_sub_data,
    }

    html_content = render_to_string("user_side/invoice.html", content)
    pdf_response = HttpResponse(content_type="application/pdf")
    pdf_response["Content-Disposition"] = f'filename="{id}_details.pdf"'

    pisa_status = pisa.CreatePDF(html_content, dest=pdf_response)

    if pisa_status.err:
        return HttpResponse("Error creating PDF")

    return pdf_response



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
    try:
        order_id = "#" + order_id
        main_order_obj = Order_Main_data.objects.get(order_id=order_id)
        main_order_obj.payment_status = True
        main_order_obj.save()

        id = request.user.id
        # clearing the cart after payment
        data = Cart.objects.filter(user=id)
        data.delete()
    except Exception as e:
        print(e)

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
        offers_applied = False

        for i in data:
            if i.variant.variant_status:
                sub_total += i.quantity * i.product.offer_price

        order_status = request.POST.get("order_status")
        address = request.POST.get("addressId")
        payment_option = request.POST.get("payment_option")
        total_price = request.POST.get("total_price")
        coupon_code = request.POST.get("coupon_code")

        if float(total_price) < float(sub_total):
            offers_applied = True

        # coupon recheck...
        # if coupon_code is not None and coupon_code != "None":
        #     try:
        #         coupon = Coupon.objects.get(
        #             Coupon_code=coupon_code,
        #             is_active=True,
        #             expiry_date__gte=timezone.now().date(),
        #             minimum_amount__lt=sub_total,
        #         )

        #         if sub_total > coupon.minimum_amount:
        #             discount = float(coupon.discount)
        #             amount = float(total_price) * (discount / 100)
        #             total_price = round(float(total_price) - amount, 2)

        #         else:
        #             messages.warning(request, "Invalid coupon")
        #             return redirect("order:checkout", user)

        #     except Exception as e:
        #         print(e)
        #         messages.warning(request, "Enter valid coupon")
        #         return redirect("order:checkout", user)

        wallet_amount = wallet_balence(request, id)

        if payment_option == "wallet payment":
            if total_price > wallet_amount:
                messages.warning(request, "Insufficient Balence!")
                return redirect("order:checkout", id)

        current_date = timezone.now().date()
        formatted_date = current_date.strftime("%Y%m%d")
        address_id = Address.objects.get(id=address)
        user_id = UserProfile.objects.get(id=id)

        main_order = Order_Main_data.objects.create(
            total_amount=total_price,
            order_status=order_status,
            user=user_id,
            payment_option=payment_option,

            name = address_id.name,
            house_name = address_id.house_name,
            street_name = address_id.street_name,
            pin_number = address_id.pin_number,
            district = address_id.district,
            state = address_id.state,
            country = address_id.country,
            phone_number = address_id.phone_number,
            
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
            return redirect("user_panel:wallet-payment", order_id, id, coupon_code)

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

        context = {"order_id": order_id, "address": address_id, "subtotal": sub_total, "offers applied":offers_applied}

        return render(request, "user_side/order-success.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkout(request, id):
    data = Cart.objects.filter(user=id)
    coupons = Coupon.objects.filter(
        is_active=True, expiry_date__gte=timezone.now().date()
    )

    total_price = 0
    sub_total = 0
    coupon_code = None
    offer_applied = False
    discount = 0
    category_discount = None
    coupon_applied =False

    for i in data:
        if i.variant.variant_status:
            sub_total = float(sub_total) + i.quantity * float(i.product.offer_price)

    for i in data:
        if not i.variant.variant_status:
            continue

        unit_price = i.variant.product.offer_price
        category_discount = i.variant.product.product_category.discount

        if (
            i.product.product_category.minimum_amount is not None
            and float(i.product.product_category.minimum_amount) <= unit_price
        ):
            if category_discount:
                offer_applied = True
                unit_price = float(unit_price) - float(unit_price) * (
                    category_discount / 100
                )

        total_price = float(total_price) + i.quantity * float(unit_price)

    if request.method == "POST":
        try:
            coupon_code = request.POST.get("coupon code").strip()

            print("entered coupon:",coupon_code)

            coupon = Coupon.objects.get(
                Coupon_code=coupon_code,
                is_active=True,
                expiry_date__gte=date.today(),
            )

            print("coupon from the server:", coupon)

            if total_price > coupon.minimum_amount:
                discount = float(coupon.discount)
                amount = float(total_price) * (discount / 100)
                total_price = round(float(total_price) - amount, 2)
                coupon_applied = True

            else:
                messages.warning(request, "Invalid coupon")

        except Exception as e:
            print("exception",e)
            messages.warning(request, "Enter valid coupon")

    content = {
        "address": Address.objects.filter(user=id, status=True),
        "products": data,
        "total_price": round(total_price, 2),
        "coupon_code": coupon_code,
        "subtotal": sub_total,
        "offer_applied": offer_applied,
        "discount": discount,
        "category_discount": category_discount,
        "coupons": coupons,
        "datas": data,
        "coupon_applied":coupon_applied
    }
    return render(request, "user_side/checkout.html", content)
