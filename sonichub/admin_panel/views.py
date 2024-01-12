from django.shortcuts import redirect, render
from user_authentication.models import UserProfile
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.cache import cache_control
from order_managements.models import Order_Main_data,Order_Sub_data
from django.http import JsonResponse,HttpResponse
from brand_management.models import Brand
from category_management.models import Category
from product_management.models import Products
from order_managements.models import Order_Main_data

def admin_order_details(request,id):
   content = {
      "order_main":Order_Main_data.objects.get(id=id),
      "order_sub_data":Order_Sub_data.objects.filter(main_order_id=id) 
   }  
   return render(request,"admin_side/admin-order-details.html",content)


def order_status_change(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        order_data = Order_Main_data.objects.get(order_id=order_id)
        order_data.order_status=status
        order_data.save()
        print(request.POST.get('order_id'))
        return JsonResponse({"success":'success'})




def order_list(request):
    
    content={
        "order_main_data":Order_Main_data.objects.all(),
        "order_sub_data":Order_Sub_data.objects.all()
    } 
    return render(request,'admin_side/order-list.html',content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")
    return render(request, "admin_side/admin-index.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.user.is_superuser:
        return redirect("admin_panel:admin_dashboard")

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        if not email.strip() or not password.strip():
            messages.warning(request, "Avoid Space and Enter Details")
            return redirect("admin_panel:admin_login")

        try:
            if not UserProfile.objects.filter(email=email).exists():
                messages.warning(request, "No User Found")
                return redirect("admin_panel:admin_login")
        except:
            pass

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.warning(request, "Invalid Details")
            return redirect("admin_panel:admin_login")

        else:
            if user.is_superuser:
                login(request, user)
                return redirect("admin_panel:admin_dashboard")
            else:
                messages.warning(request, "Only for Admins")

    return render(request, "admin_side/admin-login.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def users_list(request):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")
    user_details = UserProfile.objects.all().filter(is_superuser=False)
    context = {"user_details": user_details}

    return render(request, "admin_side/admin-userslist.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def block_unblock_user(request, id):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")

    try:
        user = UserProfile.objects.get(id=id)
        if user.is_active == False:
            user.is_active = True
            user.save()
        else:
            user.is_active = False
            user.save()

    except Exception:
        messages.warning("There is no such user")

    return redirect("admin_panel:users_list")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_name_search(request):
    if request.method == 'POST':
        try:
            query = request.POST.get('query')
            user_name = UserProfile.objects.filter(username__icontains=query)
            if user_name.exists():
                return render(request, "admin_side/admin-userslist.html", {"user_details":user_name})
            else:
                messages.warning(request,'Not Found')
        except Exception as a:
            messages.warning(request, "An Error Occured{a}")
    return redirect("admin_panel:user_list")



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def brand_name_search(request):
    if request.method == "POST":
        try:
            query = request.POST.get('query')
            brand_name = Brand.objects.filter(brand_name__icontains=query)
            if brand_name.exists():
                return render(request, 'admin_side/brand-view.html',{'brandlist':brand_name})
            else:
                messages.warning(request,'No data Found')
        except Exception as e:
            messages.warning(request, "An error Occured:{e}")
    return redirect("brand:brand-list")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_name_search(request):
    if request.method == 'POST':       
        try:
            query = request.POST.get('query')
            category_name = Category.objects.filter(category_name__icontains=query)
            
            if category_name.exists():
                return render(request, 'admin_side/admin-category-view.html', {"categories": category_name})
            else:
                messages.warning(request, 'No data Found')

        except Exception as e:
            messages.warning(request, f'An error occurred: {str(e)}')
            print(e)

    return redirect('category:category-list')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_name_search(request):
    if request.method == "POST":
        try:
            query = request.POST.get('query')
            order_id = Order_Main_data.objects.filter(order_id__icontains=query)

            if order_id.exists():
                return render(request,'admin_side/order-list.html',{"order_main_data":order_id})
            else:
                messages.warning(request, 'No data Found')

        except Exception as e:
            messages.warning(request,"An Error Occured{e}")
    return redirect("admin_panel:order-list")