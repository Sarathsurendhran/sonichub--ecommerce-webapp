from django.shortcuts import render, redirect
from user_authentication.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from cart_management.models import Cart
from product_management.models import Product_Variant, Products
from django.db import transaction


@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        product = request.POST.get("product")
        user = request.user.id
        variant = request.POST.get("variant")
        quantity = request.POST.get("quantity")

        user_id = UserProfile.objects.get(id=user)
        product_id = Products.objects.get(id=product)
        variant_id = Product_Variant.objects.get(id=variant)

        with transaction.atomic():
            if not Cart.objects.filter(
                user=user_id, variant=variant_id, product=product_id
            ):
                Cart.objects.create(
                    user=user_id,
                    variant=variant_id,
                    quantity=quantity,
                    product=product_id,
                )

    return JsonResponse({"success": "success"})


def product_cart(request):
    
    data = Cart.objects.filter(user=request.user.id)
    

    total_price = 0

    for i in data:
        if i.variant.variant_status:
            total_price += i.quantity*i.product.offer_price
        
    context = {
        "cart_items": Cart.objects.filter(user=request.user.id),
        "Total_Amount": total_price        
    }

    return render(request, "user_side/shop-cart.html", context)


def delete_cart_product(request, id):
    data = Cart.objects.get(id=id)
    data.delete()
    return redirect("cart:product-cart")


def quantity_update(request, id):
    quantity = request.POST.get("qty")
    data = Cart.objects.get(id=id)
    data.quantity = quantity
    data.save()

    return redirect("cart:product-cart")
