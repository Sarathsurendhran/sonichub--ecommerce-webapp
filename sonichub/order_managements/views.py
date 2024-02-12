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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def cancel_individual_product(request, order_sub_id, order_id):
    data = Order_Sub_data.objects.get(id=order_sub_id)
    data.is_active = False
    data.save()

    user_id = UserProfile.objects.get(id=request.user.id)

    order_main = Order_Main_data.objects.get(id=data.main_order.id)

    find_sub_total = Order_Sub_data.objects.filter(main_order=order_main.id)
    sub_total = 0

    order_sub_data = Order_Sub_data.objects.filter(main_order=order_main.id, is_active=False).count()
    order_sub_data_total = Order_Sub_data.objects.filter(main_order=order_main.id).count()

    try:
        user_coupon = Users_Coupon.objects.get(order=order_main.id)
        coupons = Coupon.objects.get(Coupon_code=user_coupon.coupon_code)
    except Exception as e:
        print("exception :", e)
        user_coupon = None
        coupons = None
        pass

    # credit cash on wallet when cancel individual product
    if (
        order_main.payment_option == "online payment"
        or order_main.payment_option == "wallet payment"
    ):
        
        price = data.variant.product.offer_price * data.quantity
        offer_discount = data.variant.product.product_category.discount

        if offer_discount:
            orginal_price = data.variant.product.price
            discount_total = float(orginal_price) * (offer_discount / 100)
            price = float(price) - discount_total


        if order_sub_data == order_sub_data_total:
             if user_coupon and coupons:
                if price >= coupons.minimum_amount:
                    discount = float(user_coupon.coupon_discount)
                    amount = float(price) * (discount / 100)
                    price = round(float(price) - amount, 2)


        # storing the datas in the transtaction table for wallet amount
        Transaction.objects.create(
            description="Cancelled Product    " + data.variant.product.product_name,
            amount=price,
            transaction_type="Credit",
            user=user_id,
        )


    # Calculating the tota amount for storing main order table
    for i in find_sub_total:
        if not i.is_active:
            continue

        unit_price = i.variant.product.offer_price * i.quantity
        if i.variant.product.product_category.discount:
            price = i.variant.product.price
            category_discount = int(i.variant.product.product_category.discount)
            total_discount = float(price) * (category_discount / 100)
            unit_price = float(unit_price) - total_discount

        if i.variant.variant_status:
            sub_total += float(unit_price)

    # calculating the amount afert coupon discount if any
    if user_coupon and coupons:
        print("enterd coupon applying section")
        if sub_total >= coupons.minimum_amount:
            discount = float(user_coupon.coupon_discount)
            amount = float(sub_total) * (discount / 100)
            sub_total = round(float(sub_total) - amount, 2)
            
    
    order_main.total_amount = sub_total
    order_main.save()

    # if full product cancelled individullay this code will mark that order cancelled

    if order_sub_data == order_sub_data_total:
        order_main.order_status = "Cancelled"
        order_main.save()

        return redirect("order:order-details", order_main.id)

    return redirect("order:order-details", order_main.id)


def generate_pdf(request, order_id):
      
    order_main = Order_Main_data.objects.get(order_id=order_id)
    order_sub = Order_Sub_data.objects.filter(main_order_id=order_main.id)
    sub_total = 0
    price = 0
    amount = 0
    total_subtotal = 0

    for i in order_sub:
        sub_total = i.variant.product.offer_price * i.quantity
        if i.variant.product.product_category.discount:
            price = i.variant.product.price
            category_discount = int(i.variant.product.product_category.discount)
            total_discount = float(price) * (category_discount / 100)
            sub_total =  float(sub_total) - total_discount
            print("subtotal in side loop:",sub_total)

        total_subtotal += float(sub_total)
    
    try:
        order_main = Order_Main_data.objects.get(id=order_main.id)
        user_coupon = Users_Coupon.objects.get(order=order_main.id)
        coupons = Coupon.objects.get(Coupon_code=user_coupon.coupon_code)
        
        
        if user_coupon:
            if not order_main.total_amount >= coupons.minimum_amount: 
                coupons = None

    except Exception as e:
        print(e)
        user_coupon = None
        coupons = None
        pass

    content = { 
        "order_main": order_main,
        "order_sub_data": order_sub,
        "sub_total": total_subtotal,
        "user_coupon":user_coupon,
        "coupons":coupons,
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


def online_payment(request, order_id, coupon_code=None):
    order_instance = get_object_or_404(Order_Main_data, order_id=order_id)
    if order_instance.payment_status:
        return redirect("order:current-order-details", order_id)
    


    if coupon_code is not None and coupon_code != "None":
        coupon = Coupon.objects.get(Coupon_code=coupon_code)
        user = UserProfile.objects.get(id=request.user.id)
        Users_Coupon.objects.create(
            user=user,
            coupon_code=coupon.Coupon_code,
            coupon_discount=coupon.discount,
            order=order_instance
        )
     # clearing the cart after payment
    data = Cart.objects.filter(user=request.user.id)
    data.delete()

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

            Transaction.objects.create(
                user=user,
                description="Cancelled Order " + order_id,
                amount=amount,
                transaction_type="Credit",
            )

        return redirect("order:order-list", user_id)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_details(request, id):
    order_sub = Order_Sub_data.objects.filter(main_order_id=id)
    sub_total = 0
    price = 0
    amount = 0
    total_subtotal = 0

    for i in order_sub:
        sub_total = i.variant.product.offer_price * i.quantity
        if i.variant.product.product_category.discount:
            price = i.variant.product.price
            category_discount = int(i.variant.product.product_category.discount)
            total_discount = float(price) * (category_discount / 100)
            sub_total =  float(sub_total) - total_discount
           
        total_subtotal += float(sub_total)
      
    try:
        order_main = Order_Main_data.objects.get(id=id)
        user_coupon = Users_Coupon.objects.get(order=id)
        coupons = Coupon.objects.get(Coupon_code=user_coupon.coupon_code)
        
        for i in order_sub:
            if not i.is_active:
                continue
            if i.variant.product.product_category.discount:
                sub_total = float(sub_total) + float(i.variant.product.offer_price * i.quantity)
            else:
                amount = float(amount) + float(i.variant.product.offer_price * i.quantity)
                

            # if i.variant.product.product_category.discount:
            #     print("not","sub_total", sub_total,">=", "coupon min amount", coupons.minimum_amount)
            #     if not sub_total >= coupons.minimum_amount:
            #         coupons = None
            # else:
            #     print("not","amount:",amount, ">=" ,"coupon minimum amount:",coupons.minimum_amount,)
            #     if  not amount >= coupons.minimum_amount :
            #         coupons = None
                
        if user_coupon:
            if not order_main.total_amount >= coupons.minimum_amount: 
                coupons = None       

    except Exception as e:
        print(e)
        user_coupon = None
        coupons = None
        pass

    content = { 
        "order_main": order_main,
        "order_sub_data": order_sub,
        "sub_total": total_subtotal,
        "user_coupon":user_coupon,
        "coupons":coupons, 
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

    flat_grouped_data = [(key, value) for key, value in grouped_data.items()]

    paginator = Paginator(flat_grouped_data, 3)
    page = request.GET.get("page", 1)

    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    context = {"grouped_order_data": objects, "objects": objects}
    return render(request, "user_side/order-list.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def current_order_details(request, order_id):
    print(order_id)
    
    order_main = Order_Main_data.objects.get(order_id=order_id)
    order_sub = Order_Sub_data.objects.filter(main_order_id=order_main.id)
    sub_total = 0
    price = 0
    amount = 0
    total_subtotal = 0

    for i in order_sub:
        sub_total = i.variant.product.offer_price * i.quantity
        if i.variant.product.product_category.discount:
            price = i.variant.product.price
            category_discount = int(i.variant.product.product_category.discount)
            total_discount = float(price) * (category_discount / 100)
            sub_total =  float(sub_total) - total_discount
            print("subtotal in side loop:",sub_total)

        total_subtotal += float(sub_total)
    
    try:
        order_main = Order_Main_data.objects.get(id=order_main.id)
        user_coupon = Users_Coupon.objects.get(order=order_main.id)
        coupons = Coupon.objects.get(Coupon_code=user_coupon.coupon_code)
        
        
        if user_coupon:
            if not order_main.total_amount >= coupons.minimum_amount: 
                coupons = None

    except Exception as e:
        print(e)
        user_coupon = None
        coupons = None
        pass

    content = { 
        "order_main": order_main,
        "order_sub_data": order_sub,
        "sub_total": total_subtotal,
        "user_coupon":user_coupon,
        "coupons":coupons,
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

        try:
            discount_percentage = Coupon.objects.get(Coupon_code=coupon_code)
            discount = discount_percentage.discount
        except:
            discount = None
            pass

        if float(total_price) < float(sub_total):
            offers_applied = True

        wallet_amount = wallet_balence(request, id)

        if payment_option == "wallet payment":
            if float(total_price) > float(wallet_amount):
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
            coupon_discount=discount,
            name=address_id.name,
            house_name=address_id.house_name,
            street_name=address_id.street_name,
            pin_number=address_id.pin_number,
            district=address_id.district,
            state=address_id.state,
            country=address_id.country,
            phone_number=address_id.phone_number,
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
            if coupon_code:
                return redirect("order:online-payment", order_id, coupon_code)
            else:
                return redirect("order:online-payment", order_id)


        if payment_option == "wallet payment":
            if coupon_code:
                return redirect("user_panel:wallet-payment", order_id, id, coupon_code)
            else:
                return redirect("user_panel:wallet-payment", order_id, id)

        # clearing the cart
        data.delete()

        # saving coupon information of each users
        if coupon_code is not None and coupon_code != "None":
            coupon = Coupon.objects.get(Coupon_code=coupon_code)
            user = UserProfile.objects.get(id=request.user.id)
            Users_Coupon.objects.create(
                user=user,
                coupon_code=coupon.Coupon_code,
                coupon_discount=coupon.discount,
                order_id=main_order_id.id
                
            )

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

        context = {
            "order_id": order_id,
            "address": address_id,
            "subtotal": sub_total,
            "offers applied": offers_applied,
        }

        return render(request, "user_side/order-success.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkout(request, id):
    data = Cart.objects.filter(user=id)

    # Fetching all active coupons that have not expired
    all_coupons = Coupon.objects.filter(
        status=True, expiry_date__gte=timezone.now().date()
    )
    user_coupon = Users_Coupon.objects.filter(user=id)
    # Fetching all the coupons that are not in the user coupon
    coupons = all_coupons.exclude(
        Coupon_code__in=user_coupon.values_list("coupon_code", flat=True)
    )


    total_price = 0
    sub_total = 0
    coupon_code = None
    offer_applied = False
    discount = 0
    category_discount = None
    coupon_applied = False

    for i in data:
        if i.variant.variant_status:
            sub_total = float(sub_total) + i.quantity * float(i.product.offer_price)

    for i in data:
        if not i.variant.variant_status:
            continue

        unit_price = i.variant.product.offer_price
        print("initial unit price:", unit_price)
        category_discount = i.variant.product.product_category.discount

        if (
            i.product.product_category.minimum_amount is not None
            and float(i.product.product_category.minimum_amount) <= unit_price
        ):
            price = i.variant.product.price
            print("initial unit price if category offer:", unit_price)
            if category_discount:
                offer_applied = True

                amount = float(price) * (category_discount / 100)
                unit_price = float(unit_price) - float(amount)
                print("unit price after category discount:", unit_price)

        total_price = float(total_price) + i.quantity * float(unit_price)
        print("final price :", total_price)

    if request.method == "POST":
        try:
            coupon_code = request.POST.get("coupon code").strip()

            print("entered coupon:", coupon_code)

            coupon = Coupon.objects.get(
                Coupon_code=coupon_code,
                status=True,
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
            print("exception", e)
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
        "coupon_applied": coupon_applied,
    }
    return render(request, "user_side/checkout.html", content)
