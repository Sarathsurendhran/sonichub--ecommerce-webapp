from django.urls import path
from product_management import views

app_name = 'product'

urlpatterns = [
  path('product-list', views.product_list, name= 'product-list'),
  path('add-product', views.add_product, name='add-product'),
  path('add-images/<int:product>',views.add_images, name='add-images'),
  path('edit-product/<int:id>',views.edit_product,name='edit-product'),
  path('status-change/<int:id>',views.status_change,name='status-change'),
  path('add-variant/<int:product>',views.add_variant,name='add-variant'),
  path('variant-view/<int:id>',views.variant_view,name="variant-view"),
  path('variant-status-change/<int:id>',views.variant_status_change,name='variant-status-change'),
  path('delete-thumbnail/<int:id>',views.delete_thumbnail,name='delete-thumbnail'),
  path('edit-images/<int:id>',views.edit_images,name='edit-images'),
  path('thumbnail-update/<int:id>',views.thumbnail_update,name='thumbnail-update'),
  path('search',views.search,name='search')
  

]