from django.shortcuts import render, redirect
from user_authentication.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from cart_management.models import Cart
from product_management.models import Product_Variant, Products
from django.db import transaction
from django.contrib.auth.decorators import login_required


@login_required(login_url='user_side:user_login')
def add_to_cart_index(request):
    if request.method == "POST":
        product = request.POST.get("product")

        user = request.user.id
        user_id = UserProfile.objects.get(id=user)
        product_id = Products.objects.get(id=product)
        variant = Product_Variant.objects.filter(
            product=product_id, variant_status=True
        ).first()

        quantity = 1
        variant_id = Product_Variant.objects.get(id=variant.id)
        variant_stock = variant.variant_stock
        if variant_stock and quantity <= variant_stock:
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

        return JsonResponse({"error": "error"})


@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product")
        user_id = request.user.id
        variant_id = request.POST.get("variant")
        newQty = int(request.POST.get("quantity"))

        user_obj = UserProfile.objects.get(id=user_id)
        product_obj = Products.objects.get(id=product_id)
        variant_obj = Product_Variant.objects.get(id=variant_id)

        availableQty = variant_obj.variant_stock
      
        print(variant_obj.colour_name,availableQty)

        # if availableQty == 0:
        #         return JsonResponse({"error": "Error: Item is out of stock"}, status=400)
        
        print("entered")

        with transaction.atomic():
            cart_obj, created = Cart.objects.get_or_create(
                user=user_obj,
                variant=variant_obj,
                product=product_obj,
                defaults={"quantity": newQty},
            )

            currentQty = cart_obj.quantity
            print("current",currentQty)

            

            if not created:
                if currentQty + newQty > availableQty or availableQty == 0:
                    return JsonResponse({"error":"Error"}, status=400)
                cart_obj.quantity += newQty
                cart_obj.save()
            return JsonResponse({"success": "Success"},status=200)


@login_required(login_url='user_side:user_login')
def product_cart(request):
    data = Cart.objects.filter(user=request.user.id)

    total_price = 0

    for i in data:
        if i.variant.variant_status:
            total_price += i.quantity * i.product.offer_price

    context = {
        "cart_items": Cart.objects.filter(user=request.user.id),
        "Total_Amount": total_price,
    }

    return render(request, "user_side/shop-cart.html", context)


def delete_cart_product(request, id):
    data = Cart.objects.get(id=id)
    data.delete()
    return redirect("cart:product-cart")


def quantity_update(request, id):
    quantity = request.POST.get("qty")
    print(quantity)
    data = Cart.objects.get(id=id)
    data.quantity = quantity
    data.save()

    return redirect("cart:product-cart")
