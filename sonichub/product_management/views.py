from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control
from product_management.models import Products, Product_images, Product_Variant
from category_management.models import Category
from brand_management.models import Brand
from .models import *
from django.db import transaction
from django.contrib.auth import authenticate
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


def variant_view(request, id):
    content = {
        "products": Products.objects.get(id=id),
        "variants": Product_Variant.objects.filter(product_id=id),
    }

    return render(request, "admin_side/product-variant-view.html", content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_images(request, product):
    if request.method == "POST":
        images = request.FILES.getlist("images")

        product_id = Products.objects.get(id=product)
        for image in images:
            Product_images.objects.create(product=product_id, images=image)

        messages.success(request, "Image Added Sucessfully")
        return redirect("product:add-variant", product)

    return render(request, "admin_side/add-images.html", {"product": product})


@csrf_exempt
def add_variant(request, product):
    try:
        product = Products.objects.get(id=product)
    except Products.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            variants = data.get("variants", [])
            for variant_data in variants:
                Product_Variant.objects.create(
                    colour_code=variant_data["color_code"],
                    colour_name=variant_data["color_name"],
                    variant_stock=int(variant_data["variant_stock"]),
                    variant_status=variant_data["variant_status"],
                    product=product,
                )

            return JsonResponse({"status": "success"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"})

    return render(request, "admin_side/add-product-variants.html", {"product": product})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")

    if request.method == "POST":
        product_name = request.POST.get("product_name")
        product_description = request.POST.get("product_description")
        brand = request.POST.get("brand")
        category = request.POST.get("category")
        price = request.POST.get("price")
        offer_price = request.POST.get("offer_price")
        status = request.POST.get("status") == "on"
        thumbnail = request.FILES.get("thumbnail_image")

        if not product_name:
            messages.warning(request, "Product Name Cannot Be Empty")
            return redirect("product:add-product")

        if product_description == "":
            messages.warning(request, "Product Description Cannot Be Empty")
            return redirect("product:add-product")

        if price == "":
            messages.warning(request, "Price Cannot Be Empty")
            return redirect("product:add-product")

        if offer_price == "":
            messages.warning(request, "Offer Price Cannot Be Empty")
            return redirect("product:add-product")

        if price.startswith("-") or offer_price.startswith("-"):
            messages.warning(request, "Please Enter positive values")
            return redirect("product:add-product")

        if not product_name.replace(" ", "").isalpha():
            messages.warning(request, "Product Name Only Allow Alphabetical Characters")
            return redirect("product:add-product")

        try:
            if Products.objects.filter(product_name=product_name).exists():
                messages.warning(request, "Product Name Already Exsists")
                return redirect("product:add-product")
            else:
                product = Products.objects.create(
                    product_name=product_name,
                    product_description=product_description,
                    product_brand_id=brand,
                    product_category_id=category,
                    price=price,
                    offer_price=offer_price,
                    is_active=status,
                    thumbnail=thumbnail,
                )

                return redirect("product:add-images", product.id)

        except Exception as e:
            s = f"An Error Occured: {str(e)}"
            print(s)
            messages.error(request, f"An Error Occured: {str(e)}")

    content = {
        "branddata": Brand.objects.filter(brand_name__isnull=False),
        "categorydata": Category.objects.filter(category_name__isnull=False),
    }

    return render(request, "admin_side/add-product.html", content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_list(request):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")
    content = {
        "products": Products.objects.all().order_by("id"),
        "variants": Product_Variant.objects.filter(id__isnull=False).order_by("id"),
    }

    return render(request, "admin_side/product-view.html", content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_product(request, id):
    product_data = Products.objects.get(id=id)

    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")

    if request.method == "POST":
        product_name = request.POST.get("product_name")
        product_description = request.POST.get("product_description")
        brand = request.POST.get("brand")
        category = request.POST.get("category")
        price = request.POST.get("price")
        offer_price = request.POST.get("offer_price")
        status = request.POST.get("status") == "on"
        # thumbnail = request.FILES.get("thumbnail_image")

        if not product_name:
            messages.warning(request, "Product Name Cannot Be Empty")
            return redirect("product:edit-product", id)

        if product_description == "":
            messages.warning(request, "Product Description Cannot Be Empty")
            return redirect("product:edit-product", id)
        if price == "":
            messages.warning(request, "Price Cannot Be Empty")
            return redirect("product:edit-product", id)

        if offer_price == "":
            messages.warning(request, "Offer Price Cannot Be Empty")
            return redirect("product:edit-product", id)

        if offer_price > price:
            messages.warning(request, "Offer Price Should be lessthan acual price")
            return redirect("product:edit-product", id)

        if price.startswith("-") or offer_price.startswith("-"):
            messages.warning(request, "Please Enter positive values")
            return redirect("product:edit-product", id)

        if not product_name.replace(" ", "").isalpha():
            messages.warning(request, "Product name only allow alphabetical characters")
            return redirect("product:edit-product", id)

        try:
            if (
                Products.objects.filter(product_name=product_name)
                .exclude(id=id)
                .exists()
            ):
                messages.warning(request, "Product Name Already Exsists")
                return redirect("product:edit-product", id)
            else:
                with transaction.atomic():
                    product_data.product_name = product_name
                    product_data.product_description = product_description
                    product_data.product_brand = Brand.objects.get(id=brand)
                    product_data.product_category = Category.objects.get(id=category)
                    product_data.price = price
                    product_data.offer_price = offer_price
                    product_data.is_active = status
                    # product_data.thumbnail = thumbnail
                    product_data.save()

            messages.success(request, "Product Updated Sucessfully")
            return redirect("product:edit-images", id=id)

        except Exception as e:
            s = f"An Error Occured: {str(e)}"
            print(s)
            messages.error(request, f"An Error Occured: {str(e)}")

    content = {
        "products": product_data,
        "images": Product_images.objects.filter(product=id),
        "branddata": Brand.objects.filter(brand_name__isnull=False),
        "categorydata": Category.objects.filter(category_name__isnull=False),
    }

    return render(request, "admin_side/edit-product.html", content)


def thumbnail_update(request, id):
    if request.method == "POST":
        thumbnail = request.FILES.get("thumbnail_image")
        if not thumbnail:
            messages.warning(request, "Please select Image")
            return redirect("product:edit-product", id)

        data = Products.objects.get(id=id)
        data.thumbnail = thumbnail
        data.save()
        return redirect("product:edit-product", id)


def status_change(request, id):
    if not request.user.is_superuser:
        return redirect("admin_panel: admin_login")

    try:
        product = Products.objects.get(id=id)
        if product.is_active == True:
            product.is_active = False
            product.save()
        else:
            product.is_active = True
            product.save()

    except Exception:
        messages.warning(request, "No Such Product")

    return redirect("product:product-list")


def variant_status_change(request, id):
    if not request.user.is_superuser:
        return redirect("admin_panel: admin_login")

    try:
        product_variant = Product_Variant.objects.get(id=id)
        if product_variant.variant_status == True:
            product_variant.variant_status = False
            product_variant.save()
        else:
            product_variant.variant_status = True
            product_variant.save()

    except Exception as e:
        print(e)

    return redirect("product:variant-view", product_variant.product_id)


def delete_thumbnail(request, id):
    product_data = Products.objects.get(id=id)
    product_data.thumbnail.delete()
    return redirect("product:edit-product", id)


def edit_images(request, id):
    print(id)

    return render(request, "admin_side/edit-images.html", {"id": id})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search(request):
    if request.method == "POST":
        query = request.POST.get("query")
        product_name = Products.objects.filter(product_name__icontains=query)
        if product_name.exists():
            content = {
                "products": product_name,
                
            }

            return render(request, "admin_side/product-view.html", content)
        else:
            
            messages.warning(request,'No data')
            return redirect("product:product-list")
