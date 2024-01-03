from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("add-to-cart", views.add_to_cart, name="add-to-cart"),
    path("product-cart", views.product_cart, name="product-cart"),
    path(
        "delete-cart-product/<int:id>",
        views.delete_cart_product,
        name="delete-cart-product",
    ),
    path("quantity-update/<int:id>", views.quantity_update, name="quantity-update"),
]
