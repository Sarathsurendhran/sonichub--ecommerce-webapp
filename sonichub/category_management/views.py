from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.decorators.cache import cache_control
from .models import Category
import re


@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def category_list(request):
  if not request.user.is_superuser:
    return redirect('admin_panel:admin_login')
  
  categories = Category.objects.all().order_by('id')

  content = {
    "categories" : categories
  }

  return render(request, 'admin_side/admin-category-view.html', content)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_category(request):
  if not request.user.is_superuser:
    return redirect('admin_panel:admin_login')
  
  if request.method == 'POST':  
    category_name = request.POST['category_name']
    status = request.POST['status']
    parent = None if request.POST['parent'] == '0' else Category.objects.get(
             id = request.POST['parent'])
  
    if category_name == '':
      messages.warning(request, 'Category Name Cannot Be Empty')
      return redirect('category:add-category')

    if not category_name.replace(" ", "").isalpha():
      messages.warning(request, 'Category Name Should Only Contain Alphabetical Characters')
      return redirect('category:add-category')

    try:

        if Category.objects.filter(category_name = category_name).exists():
          messages.warning(request, 'Category Name is Already Taken')
        else:
         Category.objects.create(
              category_name = category_name, parent = parent, is_available = status)
         
         messages.success(request, 'Category Added Sucessfully')
          
         
    except Exception as e:
        messages.error(request, f"An Error Occured: {str(e)}")
        
  parentlist = Category.objects.filter(category_name__isnull=False)
  return render(request, 'admin_side/add-category.html',{'parentlist': parentlist})
  



def status_update(request, id):
  if not request.user.is_superuser:
    return redirect('admin_panel: admin_login')
  
  try:
    category = Category.objects.get(id = id)
    if category.is_available == True:
      category.is_available = False
      category.save()
    else:
      category.is_available = True
      category.save()

  except Exception:
    messages.warning(request, 'No Such Category')
  
  return redirect('category:category-list')
   


@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def edit_category(request, id):
    if not request.user.is_superuser:
      return redirect('admin_panel:admin_login')
    try:
        category_data = Category.objects.get(id=id)
        category_parent_data = Category.objects.filter()

    except Category.DoesNotExist:
        messages.error(request, 'Category does not exist.')
        return redirect('category:add-category')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        status = request.POST.get('status')
        parent = None if request.POST['parent'] == '0' else Category.objects.get(
             id = request.POST['parent'])
  
       
        if category_name == '':
            messages.warning(request, 'Category Name Cannot Be Empty')
            return redirect('category:edit-category')

        if not category_name.replace(" ", "").isalpha():
            messages.warning(request, 'Category Name Should Only Contain Alphabetical Characters')
            return redirect('category:edit-category')

        try:
            if Category.objects.filter(category_name=category_name).exclude(id=id).exists():
                messages.warning(request, 'Category Name is Already Taken')
            else:
                category_data.category_name = category_name
                category_data.is_available = status
                category_data.parent = parent
                category_data.save()

                messages.success(request, 'Category Updated Successfully')

        except Exception as e:
            messages.error(request, f"An Error Occurred: {str(e)}")

    context = {
        'category_data': category_data,
        'category_parent_data': category_parent_data,
    }

    return render(request, 'admin_side/edit-category.html', context)

