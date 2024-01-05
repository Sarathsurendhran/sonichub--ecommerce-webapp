from django.shortcuts import render,redirect
from user_panel.models import Address


def order(request,id):

  content={
    "address":Address.objects.filter(status=True)
  }
  return render(request, 'user_side/order.html',content)


def checkout(request,id):
  content={
    "address": Address.objects.filter(id=id, status=True)
  }
  return render(request, 'user_side/checkout.html',content)