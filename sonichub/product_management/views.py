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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage



def price_range(request):
    try:
        min_price = request.POST.get('min-value')
        max_price = request.POST.get('max-value')
        products = Products.objects.filter(offer_price__range=[min_price, max_price], is_active=True)

    except Products.DoesNotExist:
        products = []

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')

    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    content = {
        "products": paginated_products,
        "categories": Category.objects.filter(is_available=True),
        "brands": Brand.objects.filter(status=True)
    }

    return render(request, 'user_side/shop-product-list.html', content)





def shop_product_list(request, brand_id=None, category_id=None):
    
    if brand_id:
        try:
            products = Products.objects.filter(product_brand=brand_id, is_active=True)
        except Products.DoesNotExist:
            products = []

       

    elif category_id:
        print(category_id)
        try:
            products = Products.objects.filter(product_category=category_id, is_active=True)
            print(products)
        except Products.DoesNotExist:
            products = []
        
        
    else:
        products = Products.objects.all()
    
    paginator = Paginator(products, 6)
    page = request.GET.get('page', 1)

    try:
        paginated_products = paginator.page(page)
    
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)


    content = {
        "products":paginated_products,
        "categories":Category.objects.filter(is_available=True),
        "brands":Brand.objects.filter(status=True)
    }

    return render(request, 'user_side/shop-product-list.html', content)



def edit_variant_status_change(request, id):
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

    return redirect("product:edit-variant-in-edit-product", product_variant.product.id)



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


def delete_thumbnail_add_image(request, id):
    product_data = Products.objects.get(id=id)
    product_data.thumbnail.delete()
    return redirect("product:add-images", product_data.id)


def delete_thumbnail_edit_image(request, id):
    product_data = Products.objects.get(id=id)
    product_data.thumbnail.delete()
    return redirect("product:edit-images", product_data.id)


def delete_images(request):
    image_id = request.POST.get("image_id")
    product = request.POST.get("product_id")
    images = Product_images.objects.get(id=image_id)
    images.delete()
    return redirect("product:add-images", product)



def delete_images_edit(request):
    image_id = request.POST.get("image_id")
    product = request.POST.get("product_id")
    images = Product_images.objects.get(id=image_id)
    images.delete()
    return redirect("product:edit-images", product)



def edit_variant_in_edit_product(request,product):
    if request.method == 'POST':
        try:
            color = request.POST.get("color")
            name = request.POST.get("name")
            stock = request.POST.get("stock")
            variant_id = request.POST.get("variant_id")
            print("variant_id:",variant_id,stock)

            data = Product_Variant.objects.get(id=variant_id)
            data.colour_code = color
            data.colour_name = name
            data.variant_stock = stock
            data.save()
            return JsonResponse({"success": True}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({"error": True}, status=400)

    content = {
        "products": Products.objects.get(id=product),
        "variants": Product_Variant.objects.filter(product_id=product).order_by('id').reverse(),
    }

    return render(request, "admin_side/edit-variants1.html", content)



def edit_variant(request, variant_id):
    try:
        color = request.GET.get("color")
        name = request.GET.get("name")
        stock = request.GET.get("stock")
        data = Product_Variant.objects.get(id=variant_id)
        data.colour_code = color
        data.colour_name = name
        data.variant_stock = stock
        data.save()
        return JsonResponse({"success": True}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"error": True}, status=400)
    


def edit_thumbnail(request):
    image = request.FILES.get("imageFiles")
    product = request.POST.get("productId")
    product_data = Products.objects.get(id=product)
    product_data.thumbnail = image
    product_data.save()
    return redirect("product:edit-images", product)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_images(request, product):
    product_id = Products.objects.get(id=product)
    thumbnail = Products.objects.get(id=product)

    if request.method == "POST":
        image_files= request.FILES.getlist("imageFiles")

        existing_images = Product_images.objects.filter(product=product)

        for image in image_files:
            Product_images.objects.create(product=product_id, images=image)


        messages.success(request, "Image Added Sucessfully")

        
    content = {
        "existing_images": Product_images.objects.filter(product=product_id)
        .order_by("id")
        .reverse(),
        "product": product,
        "thumbnail": Products.objects.get(id=product),
    }
    return render(request, "admin_side/edit-images1.html", content)




def variant_view(request, id):
    content = {
        "products": Products.objects.get(id=id),
        "variants": Product_Variant.objects.filter(product_id=id),
    }

    return render(request, "admin_side/product-variant-view.html", content)



def add_thumbnail(request):
    image = request.FILES.get("imageFiles")
    product = request.POST.get("productId")
    product_data = Products.objects.get(id=product)
    product_data.thumbnail = image
    product_data.save()
    return redirect("product:add-images", product)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_images(request, product):
    product_id = Products.objects.get(id=product)
    thumbnail = Products.objects.get(id=product)

    if request.method == "POST":
        images = request.FILES.getlist("imageFiles")

        # product_id = Products.objects.get(id=product)
        for image in images:
            Product_images.objects.create(product=product_id, images=image)

        existing_images = Product_images.objects.filter(product=product_id)
        image = existing_images

        messages.success(request, "Image Added Sucessfully")
        return render(
            request,
            "admin_side/add-images1.html",
            {"product": product, "existing_images": existing_images},
        )

        # return redirect("product:add-variant", product)
    content = {
        "existing_images": Product_images.objects.filter(product=product_id)
        .order_by("id")
        .reverse(),
        "product": product,
        "thumbnail": Products.objects.get(id=product),
    }
    return render(request, "admin_side/add-images1.html", content)




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

            return JsonResponse({"success": True}, status=200)

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
        
        if float(offer_price) > float(price):
            messages.warning(request, "Offer Price Should be lessthan actual price")
            return redirect("product:edit-product", id)

        if price.startswith("-") or offer_price.startswith("-"):
            messages.warning(request, "Please Enter positive values")
            return redirect("product:add-product")

        if not any(char.isalpha() for char in product_name):
            messages.warning(request, "Product Name should contain at least one alphabetical character")
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
        "products": Products.objects.all().order_by("id").reverse(),
        "variants": Product_Variant.objects.filter(id__isnull=False)
        .order_by("id")
        .reverse(),
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

        if float(offer_price) > float(price):
            messages.warning(request, "Offer Price Should be lessthan acual price")
            return redirect("product:edit-product", id)

        if price.startswith("-") or offer_price.startswith("-"):
            messages.warning(request, "Please Enter positive values")
            return redirect("product:edit-product", id)

        if not any(char.isalpha() for char in product_name):
            messages.warning(request, "Product Name should contain at least one alphabetical character")
            return redirect("product:add-product")

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
            return redirect("product:edit-images", product=id)

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
            messages.warning(request, "No data")
            return redirect("product:product-list")
