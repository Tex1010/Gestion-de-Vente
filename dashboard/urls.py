from django.urls import path

from .views import (
    DashboardLoginView,
    DashboardLogoutView,
    category_list,
    dashboard_home,
    order_list,
    product_list,
)

app_name = "dashboard"

urlpatterns = [
    path("login/", DashboardLoginView.as_view(), name="login"),
    path("logout/", DashboardLogoutView.as_view(), name="logout"),
    path("", dashboard_home, name="index"),
    path("produits/", product_list, name="product_list"),
    path("categories/", category_list, name="category_list"),
    path("commandes/", order_list, name="order_list"),
]
