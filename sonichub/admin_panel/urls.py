from django.urls import path
from admin_panel import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.admin_login, name="admin_login"),
    path("admin_dashboard", views.admin_dashboard, name="admin_dashboard"),
    path("users_list", views.users_list, name="users_list"),
    path(
        "block_unblock_user/<int:id>/",
        views.block_unblock_user,
        name="block_unblock_user",
    ),
    path("order-list", views.order_list, name="order-list"),
    path("order-status-change", views.order_status_change, name="order-status-change"),
    path(
        "admin-order-details/<int:id>",
        views.admin_order_details,
        name="admin-order-details",
    ),
    path("user-name-search", views.user_name_search, name="user-name-search"),
    path("brand-name-search", views.brand_name_search, name="brand-name-search"),
    path("category-name-search", views.category_name_search, name="category-name-search"),
    path("order-name-search",views.order_name_search,name='order-name-search'),
    path("sales-report", views.sales_report, name="sales-report"),
    path('sales-report-pdf',views.sales_report_pdf, name="sales-report-pdf"),
    path('sales-report-excel',views.sales_report_excel, name="sales-report-excel"),
    

]
