from django.urls import path
from .import views

app_name ='brand'

urlpatterns =[

  path('brand-list', views.brand_list, name='brand-list'),
  path('add-brand',views.add_brand, name='add-brand'),
  path('edit-brand/<int:id>', views.edit_brand,name='edit-brand'),
  path('status_update/<int:id>',views.status_update, name='status_update')
  

]