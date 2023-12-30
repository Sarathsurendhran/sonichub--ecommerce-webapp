"""
URL configuration for sonichub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('adminlogin/', admin.site.urls),
    path('admin/',include('admin_panel.urls')),
    path('',include('user_authentication.urls')),
    path('admin/category', include('category_management.urls')),
    path('admin/brand',include('brand_management.urls')),
    path('admin/product',include('product_management.urls')),
    path('user/',include('user_panel.urls')),
    path('user/cart',include('cart_management.urls'))
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)