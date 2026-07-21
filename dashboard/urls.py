from django.urls import path

from .views import (
    banner_create,
    banner_delete,
    banner_edit,
    banner_list,
    category_create,
    category_delete,
    category_edit,
    category_list,
    DashboardLoginView,
    DashboardLogoutView,
    dashboard_home,
    order_detail,
    order_list,
    product_create,
    product_delete,
    product_edit,
    product_list,
    site_settings,
)

app_name = "dashboard"

urlpatterns = [
    # Auth
    path("login/", DashboardLoginView.as_view(), name="login"),
    path("logout/", DashboardLogoutView.as_view(), name="logout"),
    # Home
    path("", dashboard_home, name="index"),
    # Products
    path("produits/", product_list, name="product_list"),
    path("produits/ajouter/", product_create, name="product_create"),
    path("produits/<int:pk>/modifier/", product_edit, name="product_edit"),
    path("produits/<int:pk>/supprimer/", product_delete, name="product_delete"),
    # Categories
    path("categories/", category_list, name="category_list"),
    path("categories/ajouter/", category_create, name="category_create"),
    path("categories/<int:pk>/modifier/", category_edit, name="category_edit"),
    path("categories/<int:pk>/supprimer/", category_delete, name="category_delete"),
    # Orders
    path("commandes/", order_list, name="order_list"),
    path("commandes/<int:pk>/", order_detail, name="order_detail"),
    # Banners
    path("bannieres/", banner_list, name="banner_list"),
    path("bannieres/ajouter/", banner_create, name="banner_create"),
    path("bannieres/<int:pk>/modifier/", banner_edit, name="banner_edit"),
    path("bannieres/<int:pk>/supprimer/", banner_delete, name="banner_delete"),
    # Site settings
    path("site/", site_settings, name="site_settings"),
]
