from django.urls import path
from .import views


app_name = 'category'

urlpatterns =[
  path('category-list',views.category_list, name='category-list'),
  path('add-category',views.add_category, name='add-category'),
  path('category-status-update/<int:id>',views.status_update,name='category-status-update'),
  path('eidt-category/<int:id>', views.edit_category, name='edit-category'),
]

