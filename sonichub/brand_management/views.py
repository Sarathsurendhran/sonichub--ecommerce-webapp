from django.shortcuts import render,redirect
from brand_management.models import Brand
from django.contrib import messages
from django.views.decorators.cache import cache_control
import admin_panel
from product_management.models import Products,Product_Variant

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def brand_list(request):
  if not request.user.is_superuser:
    return redirect('admin_panel:admin_login')
  brandlist = Brand.objects.all().order_by('id')
  content = {
    'brandlist':brandlist
  }

  return render(request, 'admin_side/brand-view.html', content)


@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def add_brand(request):
  if not request.user.is_superuser:
    return redirect('admin_panel:admin_login')
  
  if request.method == 'POST':
    brand_name = request.POST.get('brand_name')
    brand_image = request.FILES.get('brand_image')
    status = request.POST.get('status') == 'on'

    if brand_name == '':
      messages.warning(request, 'Brand Name Cannot Be Empty')
      return redirect('brand:add-brand')
    
    if brand_image == '':
       messages.warning(request, 'Brand Image Cannot Be Empty')
       return redirect('brand:add-brand')
    
    if not brand_name.replace(" ", "").isalpha():
      messages.warning(request, 'Brand Name Should Only Contain Alphabetical Characters')
      return redirect('brand:add-brand')
    
    try:

      if Brand.objects.filter(brand_name = brand_name).exists():
        messages.warning(request, 'Brand Name Already Exsists')
        return redirect('brand:add-brand')
      else:
        Brand.objects.create(brand_name = brand_name, brand_image= brand_image, status = status )
        messages.success(request, 'Brand Added Sucessfully')
        return redirect('brand:brand-list')
        
    except Exception as e:
      messages.error(request, f"An Error Occured: {str(e)}")

  return render(request, 'admin_side/add-brand.html')



@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def edit_brand(request,id):
    if not request.user.is_superuser:
      return redirect('admin_panel:admin_login')
    
    try:
        brand_data = Brand.objects.get(id=id)
        
    except Brand.DoesNotExist:
        messages.error(request, 'Brand does not exist.')
        return redirect('brand:add-brand')
      
    if not request.user.is_superuser:
      return redirect('admin_panel:admin_login')
  
    if request.method == 'POST':
      brand_name = request.POST.get('brand_name')
      brand_image = request.FILES.get('brand_image')
      status = request.POST.get('status') == 'on'

      if brand_name == '':
        messages.warning(request, 'Brand Name Cannot Be Empty')
        return redirect('brand:add-brand')
      
      if brand_image == '':
        messages.warning(request, 'Brand Image Cannot Be Empty')
        return redirect('brand:add-brand')
      
      if not brand_name.replace(" ", "").isalpha():
        messages.warning(request, 'Brand Name Should Only Contain Alphabetical Characters')
        return redirect('brand:add-brand')
      
      try:

        if Brand.objects.filter(brand_name=brand_name).exclude(id=id).exists():
          messages.warning(request, 'Brand Name Already Exsists')
          return redirect('brand:add-brand')
        else:
          brand_data.brand_name = brand_name
          brand_data.brand_image = brand_image
          brand_data.status = status
          brand_data.save()

          messages.success(request, 'Brand Updated Sucessfully')
          
      except Exception as e:
        messages.error(request, f"An Error Occured: {str(e)}")

    
    contents={
      'brand_data':brand_data

    }
    return render(request, 'admin_side/edit-brand.html',contents)



def status_update(request, id):
  if not request.user.is_superuser:
    return redirect('admin_panel: admin_login')
  
  try:
    brand = Brand.objects.get(id = id)
    products = Products.objects.filter(product_brand_id=id)
    if brand.status == True:
      brand.status = False
      brand.save()
      products.update(is_active=False)
      
    else:
      brand.status = True
      brand.save()
      products.update(is_active=True)
     
  except Exception:
    messages.warning(request, 'No Such Category')
  
  return redirect('brand:brand-list')