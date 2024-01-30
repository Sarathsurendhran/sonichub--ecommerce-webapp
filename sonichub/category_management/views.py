import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import cache_control
from .models import Category
import re
from product_management.models import Products
from datetime import date
from decimal import Decimal
from datetime import datetime



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_list(request):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")

    categories = Category.objects.all().order_by("id").reverse()

    content = {"categories": categories}

    return render(request, "admin_side/admin-category-view.html", content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_category(request):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")

    if request.method == "POST":
        category_name = request.POST["category_name"]
        status = request.POST["status"]
        parent = (
            None
            if request.POST["parent"] == "0"
            else Category.objects.get(id=request.POST["parent"])
        )

        # category offer
        try:
            minimum_amount = request.POST.get("minimum_amount",None)
            discount = request.POST.get("discount", None)
            discount = Decimal(discount) if discount else None
            expirydate = request.POST.get("date",None)
            if expirydate or minimum_amount:
              expirydate = datetime.strptime(expirydate, "%Y-%m-%d").date()
            else:
                expirydate = None
                minimum_amount = None

        except Exception as e:
            print(e)

        if category_name == "":
            messages.warning(request, "Category Name Cannot Be Empty")
            return redirect("category:add-category")

        if not category_name.replace(" ", "").isalpha():
            messages.warning(
                request, "Category Name Should Only Contain Alphabetical Characters"
            )
            return redirect("category:add-category")

        try:
            if Category.objects.filter(category_name=category_name).exists():
                messages.warning(request, "Category Name is Already Taken")
            else:
                Category.objects.create(
                    category_name=category_name,
                    parent=parent,
                    is_available=status,
                    minimum_amount=minimum_amount,
                    discount=discount,
                    expirydate=expirydate,
                )

                messages.success(request, "Category Added Sucessfully")
                return redirect("category:category-list")

        except Exception as e:
            messages.error(request, f"An Error Occured: {str(e)}")
    current_date = date.today().strftime("%Y-%m-%d")

    print()
    parentlist = Category.objects.filter(category_name__isnull=False).order_by('id').reverse()
    return render(
        request,
        "admin_side/add-category.html",
        {"parentlist": parentlist, "current_date": current_date},
    )


def status_update(request, id):
    if not request.user.is_superuser:
        return redirect("admin_panel: admin_login")
    try:
        category = Category.objects.get(id=id)
        parent_id = Category.objects.filter(parent_id=id)
        products = Products.objects.filter(product_category_id=id)

        if category.is_available == True:
            category.is_available = False
            category.save()
            parent_id.update(is_available=False)
            products.update(is_active=False)

        else:
            category.is_available = True
            category.save()
            products.update(is_active=True)
            parent_id.update(is_available=True)

    except Exception as e:
        messages.warning(request, "No Such Category")
        print("exception", e)

    return redirect("category:category-list")




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_category(request, id):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")
    checkbox_checked = False

    try:
        category_data = Category.objects.get(id=id)
        category_parent_data = Category.objects.all()
        if category_data.minimum_amount:
            checkbox_checked = True
       

    except Category.DoesNotExist:
        messages.error(request, "Category does not exist.")
        return redirect("category:add-category")

    if request.method == "POST":
        category_name = request.POST.get("category_name")
        status = request.POST.get("status")
        checkbox = request.POST.get('checkbox')
        
 
        parent = (
            None
            if request.POST["parent"] == "0"
            else Category.objects.get(id=request.POST["parent"])
        )

        if category_name == "":
            messages.warning(request, "Category Name Cannot Be Empty")
            return redirect("category:edit-category")

        if not category_name.replace(" ", "").isalpha():
            messages.warning(
                request, "Category Name Should Only Contain Alphabetical Characters"
            )
            return redirect("category:edit-category")

        try:
            if (
                Category.objects.filter(category_name=category_name).exclude(id=id).exists()):

            
                messages.warning(request, "Category Name is Already Taken")
            else:
                category_data.category_name = category_name
                category_data.is_available = status
                category_data.parent = parent
                
            
                try:
                    minimum_amount = request.POST.get("minimum_amount",None)
                    discount = request.POST.get("discount", None)
                    discount = Decimal(discount) if discount else None
                    expirydate = request.POST.get("date",None)
                    

                    if expirydate or minimum_amount:
                       expirydate = datetime.strptime(expirydate, "%Y-%m-%d").date()

                    else:
                        expirydate = None
                        minimum_amount = None

                    if not checkbox:
                        category_data.minimum_amount=None
                        category_data.discount=None
                        category_data.expirydate=None
                        category_data.save()
                    else:
                        category_data.minimum_amount=minimum_amount
                        category_data.discount=discount
                        category_data.expirydate=expirydate
                        category_data.save()

                except Exception as e:
                    print(e)

                messages.success(request, "Category Updated Successfully")
                return redirect("category:category-list")

        except Exception as e:
            messages.error(request, f"An Error Occurred: {str(e)}")

    context = {
        "category_data": category_data,
        "category_parent_data": category_parent_data,
        "checkbox_checked":checkbox_checked
    }

    return render(request, "admin_side/edit-category.html", context)
