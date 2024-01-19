from django.urls import path
from product_management import views

app_name = 'product'

urlpatterns = [
  path('product-list', views.product_list, name= 'product-list'),
  path('variant-view/<int:id>',views.variant_view,name="variant-view"),

  path('add-product', views.add_product, name='add-product'),
  path('add-images/<int:product>',views.add_images, name='add-images'),
  path('add-variant/<int:product>',views.add_variant,name='add-variant'),
  path('add-thumbnail',views.add_thumbnail,name="add-thumbnail"),


  path('edit-product/<int:id>',views.edit_product,name='edit-product'),
  path('edit-images/<int:product>',views.edit_images,name='edit-images'),
  #this are coming from the product view 
  path('edit-variant/<int:variant_id>',views.edit_variant,name='edit-variant'),
  path('edit-thumbnail',views.edit_thumbnail,name="edit-thumbnail"),
  #this are coming from the edit product 
  path('edit-variant-in-edit-product/<int:product>',views.edit_variant_in_edit_product,name='edit-variant-in-edit-product'),


  path('status-change/<int:id>',views.status_change,name='status-change'),
  path('variant-status-change/<int:id>',views.variant_status_change,name='variant-status-change'),
  path('edit-variant-status-change/<int:id>',views.edit_variant_status_change,name='edit-variant-status-change'),

  path('thumbnail-update/<int:id>',views.thumbnail_update,name='thumbnail-update'),

  path('delete_thumbnail_add_image/<int:id>',views.delete_thumbnail_add_image,name='delete_thumbnail_add_image'),
  path('delete_thumbnail_edit_image/<int:id>',views.delete_thumbnail_edit_image,name='delete_thumbnail_edit_image'),
  path('delete-images',views.delete_images,name='delete-images'),
  path('delete-images-edit',views.delete_images_edit,name='delete-images-edit'),


  path('search',views.search,name='search'),
 


  # path('delete-variant/<int:variant_id>/<int:product>',views.delete_variant,name="delete-variant")
  

]