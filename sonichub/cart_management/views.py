from django.shortcuts import render,redirect
from user_authentication.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


@csrf_exempt
def product_cart(request):
  # request.user.id

  return render(request,'user_side/shop-cart.html')

def add_to_cart(request):
  variant_id = request.POST.get('')



