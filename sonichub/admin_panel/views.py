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
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import pandas as pd
from bs4 import BeautifulSoup
from django.template.loader import get_template
from io import StringIO 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import F
from django.db.models import Sum, Count
from datetime import datetime


def admin_logout(request):
    logout(request)
    return redirect('admin_panel:admin_login')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_report_search(request):
        if request.method == 'POST':
           try:
               query = request.POST.get('query')
               order_data = Order_Main_data.objects.filter(order_id__icontains=query)
               if order_data.exists():
                   return render(request, 'admin_side/sales-report.html',{'order_main_data':order_data})
               messages.warning(request,'Not Found!')
           except Exception as e:
               print(e)
               messages.warning(request, "An Error Occured{e}")
        
        return redirect('admin_panel:sales-report')



def fetch_monthly_data(request):
    response = {}

    end_date = timezone.now()
  
    start_date = end_date - timezone.timedelta(days=30)

    current_date = start_date

    while current_date <= end_date:
        purchase_count = Order_Main_data.objects.filter(date=current_date, payment_status=True).count()
        response[current_date.day] = purchase_count

        current_date += timezone.timedelta(days=1)

    return JsonResponse({'response': response}, status=200)



def fetch_weekly_data(request):
    response = {}

    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=7)

    current_date = start_date
    while current_date <= end_date:
        purchase_count = Order_Main_data.objects.filter(date=current_date, payment_status=True).count()
        day_name = current_date.strftime("%A")
        response[day_name] = purchase_count

        current_date += timezone.timedelta(days=1)

    return JsonResponse({'response':response},status=200)


def fetch_yearly_data(request):
    response = {}
    end_date = timezone.now()
    start_date = end_date.replace(month=1, day=1)
    current_date = start_date

    while current_date <= end_date:
        next_month = current_date.replace(month=(current_date.month + 1))
        purchase_count = Order_Main_data.objects.filter(
            date__gte=current_date, date__lt=next_month, payment_status=True
        ).count()

        month_name = current_date.strftime("%B")
    
        response[month_name] = purchase_count

        current_date = next_month

    return JsonResponse({'response': response}, status=200)



def sales_report_excel(request):

    try:
        start_date_str= request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
    except:
        pass

    #If both start_date and end_date are provided, filter data accordingly
    if start_date_str and end_date_str:

        start_date = datetime.strptime(start_date_str, '%b. %d, %Y, midnight')
        end_date = datetime.strptime(end_date_str, '%b. %d, %Y, midnight')
       
        start_date_formatted = start_date.strftime('%Y-%m-%d')
        end_date_formatted = end_date.strftime('%Y-%m-%d')
        order_main_data = Order_Main_data.objects.filter(date__range=[start_date_formatted, end_date_formatted])
    else:
       # If no dates provided, return all data
        order_main_data = Order_Main_data.objects.all()

    context = {"order_main_data": order_main_data}
    # using the same template that is used for pdf generation
    html_content = render_to_string("admin_side/sales-report-pdf.html",context)
  
    df_list = pd.read_html(StringIO(html_content))
    df = df_list[0]  

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales-report.xlsx'
    df.to_excel(response, index=False)

    return response




def sales_report_pdf(request):

    try:
        start_date_str= request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
    except:
        pass

   
    #If both start_date and end_date are provided, filter data accordingly
    if start_date_str and end_date_str:

        start_date = datetime.strptime(start_date_str, '%b. %d, %Y, midnight')
        end_date = datetime.strptime(end_date_str, '%b. %d, %Y, midnight')
       
        start_date_formatted = start_date.strftime('%Y-%m-%d')
        end_date_formatted = end_date.strftime('%Y-%m-%d')
        order_main_data = Order_Main_data.objects.filter(date__range=[start_date_formatted, end_date_formatted])
    else:
       # If no dates provided, return all data
        order_main_data = Order_Main_data.objects.all()

    context = {"order_main_data": order_main_data}
    html_content = render_to_string("admin_side/sales-report-pdf.html", context)
    pdf_response = HttpResponse(content_type="application/pdf")
    pdf_response["Content-Disposition"] = f'filename="{id}_details.pdf"'

    pisa_status = pisa.CreatePDF(html_content, dest=pdf_response)

    if pisa_status.err:
        return HttpResponse("error creating pdf")

    return pdf_response


def sales_date_search(request):
    if request.method == 'POST':
        try:
            start_date = request.POST.get('startDate')
            end_date = request.POST.get('endDate')
  
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

                order_data = Order_Main_data.objects.filter(date__range = [start_date, end_date])
                if order_data.exists():
                    content = {
                        'order_main_data':order_data,
                        'start_date':start_date,
                        'end_date':end_date

                    }
                    return render(request, 'admin_side/sales-report.html',content)
                messages.warning(request,'Not Found!')
        except Exception as e:
            print(e)
            messages.warning(request, "An Error Occured{e}")

    return redirect('admin_panel:sales-report')


# def sales_report_pdf(request):
#    context = {
#        "order_main_data":Order_Main_data.objects.all()
#    }
#    html_content = render_to_string("admin_side/sales-report-pdf.html",context)
#    pdf_response = HttpResponse(content_type = "application/pdf")
#    pdf_response["Content-Disposition"] = f'filename="{id}_details.pdf"'

#    pisa_status = pisa.CreatePDF(html_content, dest=pdf_response) 

#    if pisa_status.err:
#        return HttpResponse("error creating pdf")
   
#    return pdf_response




def sales_report(request):

    order_main_data = Order_Main_data.objects.all().order_by('id')
    paginator = Paginator(order_main_data, 3)
    page = request.GET.get('page', 1)
    
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    context = {
        "order_main_data":objects,
        "objects":objects
    }
    return render(request, "admin_side/sales-report.html",context )




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

    order_main_data = Order_Main_data.objects.all().order_by('id').reverse()
    order_sub_data = Order_Sub_data.objects.all().order_by("id").reverse()


    paginator = Paginator(order_main_data, 3)
    page = request.GET.get('page', 1)

    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)


    
    content={
        "order_main_data":objects,
        "objects":objects,
        "order_sub_data":order_sub_data
    } 
    return render(request,'admin_side/order-list.html',content)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("admin_panel:admin_login")
    
    current_date = timezone.now()
    purchase_count = Order_Main_data.objects.filter(date__month=current_date.month, payment_status=True).count()
    result = Order_Main_data.objects.aggregate(sum = Sum('total_amount'))
    total_amount = result['sum']
    rounded_total_amount = round(total_amount, 2)

    content = {
            "total_amount":rounded_total_amount,
            "orders":Order_Main_data.objects.filter(payment_status=True).count(),
            "products":Products.objects.filter(is_active=True).count(),
            "category":Category.objects.filter(is_available=True).count(),
            "monthly_sales":purchase_count

    }
    return render(request, "admin_side/admin-index.html", content)




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