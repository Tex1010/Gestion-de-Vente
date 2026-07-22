from django.urls import path

from .views import (
    activity_log,
    activity_log_delete,
    activity_log_detail,
    banner_create,
    banner_delete,
    banner_edit,
    banner_list,
    category_create,
    category_delete,
    category_edit,
    category_list,
    coupon_create,
    coupon_delete,
    coupon_edit,
    coupon_list,
    DashboardLoginView,
    dashboard_home,
    dashboard_logout_view,
    database_backup,
    order_detail,
    order_list,
    payment_create,
    payment_delete,
    payment_edit,
    payment_list,
    password_reset_request_list,
    password_reset_send,
    product_create,
    product_delete,
    product_edit,
    product_list,
    shipping_create,
    shipping_delete,
    shipping_edit,
    shipping_list,
    site_settings,
    tax_create,
    tax_delete,
    tax_edit,
    tax_list,
    user_create,
    user_delete,
    user_edit,
    user_list,
)

app_name = "dashboard"

urlpatterns = [
    # Auth
    path("login/", DashboardLoginView.as_view(), name="login"),
    path("logout/", dashboard_logout_view, name="logout"),
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
    # Users
    path("utilisateurs/", user_list, name="user_list"),
    path("utilisateurs/ajouter/", user_create, name="user_create"),
    path("utilisateurs/<int:pk>/modifier/", user_edit, name="user_edit"),
    path("utilisateurs/<int:pk>/supprimer/", user_delete, name="user_delete"),
    # Coupons
    path("coupons/", coupon_list, name="coupon_list"),
    path("coupons/ajouter/", coupon_create, name="coupon_create"),
    path("coupons/<int:pk>/modifier/", coupon_edit, name="coupon_edit"),
    path("coupons/<int:pk>/supprimer/", coupon_delete, name="coupon_delete"),
    # Shipping
    path("livraison/", shipping_list, name="shipping_list"),
    path("livraison/ajouter/", shipping_create, name="shipping_create"),
    path("livraison/<int:pk>/modifier/", shipping_edit, name="shipping_edit"),
    path("livraison/<int:pk>/supprimer/", shipping_delete, name="shipping_delete"),
    # Taxes
    path("taxes/", tax_list, name="tax_list"),
    path("taxes/ajouter/", tax_create, name="tax_create"),
    path("taxes/<int:pk>/modifier/", tax_edit, name="tax_edit"),
    path("taxes/<int:pk>/supprimer/", tax_delete, name="tax_delete"),
    # Activity Log
    path("journal/", activity_log, name="activity_log"),
    path("journal/<int:pk>/", activity_log_detail, name="activity_log_detail"),
    path("journal/<int:pk>/supprimer/", activity_log_delete, name="activity_log_delete"),
    # Backup
    path("sauvegarde/", database_backup, name="database_backup"),
    # Payment methods
    path("paiements/", payment_list, name="payment_list"),
    path("paiements/ajouter/", payment_create, name="payment_create"),
    path("paiements/<int:pk>/modifier/", payment_edit, name="payment_edit"),
    path("paiements/<int:pk>/supprimer/", payment_delete, name="payment_delete"),
    # Password reset requests (admin)
    path("reinitialisations/", password_reset_request_list, name="password_reset_list"),
    path("reinitialisations/<int:pk>/envoyer/", password_reset_send, name="password_reset_send"),
    # Site settings
    path("site/", site_settings, name="site_settings"),
]