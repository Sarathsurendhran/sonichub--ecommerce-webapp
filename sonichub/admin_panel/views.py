from django.shortcuts import redirect, render
from user_authentication.models import UserProfile
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.cache import cache_control
from order_managements.models import Order_Main_data,Order_Sub_data
from django.http import JsonResponse,HttpResponse


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
