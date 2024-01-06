from django.shortcuts import render, redirect
from user_panel.models import Address
from cart_management.models import Cart
from order_managements.models import Order_Main_data, Order_Sub_data
from user_panel.models import Address
from user_authentication.models import UserProfile
from django.utils import timezone
from product_management.models import Product_Variant
from django.views.decorators.cache import cache_control
from django.utils.crypto import get_random_string

@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def current_order_details(request,order_id):
    order_main = Order_Main_data.objects.get(order_id=order_id)
    content = {
        "order_main":Order_Main_data.objects.get(order_id=order_id),
        "order_sub":Order_Sub_data.objects.filter(main_order_id=order_main.id)
        
    }
    return render(request, "user_side/current-order-details.html",content)


@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def confirm_order(request, id):
    if request.method == "POST":
        total_amount = request.POST.get("total_amount")
        order_status = request.POST.get("order_status")
        address = request.POST.get("addressId")
        user = request.user.id
        payment_option = request.POST.get("payment_option")

        current_date = timezone.now().date()
        formatted_date = current_date.strftime("%Y%m%d")

        r_string = get_random_string(length=4)

        address_id = Address.objects.get(id=address)

        user_id = UserProfile.objects.get(id=id)
        order_id = "#OD" + str(formatted_date) + str(user) + r_string.upper()

        main_order = Order_Main_data.objects.create(
            total_amount=total_amount,
            order_status=order_status,
            address=address_id,
            user=user_id,
            payment_option=payment_option,
            order_id=order_id,
        )
        
        try:
           
            carts_data = Cart.objects.filter(user=id)
            main_order_id = Order_Main_data.objects.get(id=main_order.id)

            for product in carts_data:
                Order_Sub_data.objects.create(
                    quantity=product.quantity,
                    main_order=main_order_id,
                    user=user_id,
                    variant=product.variant,
                )
            carts_data.delete()
        except Exception as e:
            print(e)

        context = {
            'order_id': order_id,
            'address':address_id
        }

    return render(request, "user_side/order-success.html",context)


@cache_control(no_cache = True, must_revalidate = True, no_store = True)
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
