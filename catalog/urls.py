from django.urls import path

from .views import product_detail, product_list

app_name = "catalog"

urlpatterns = [
    path("catalogue/", product_list, name="product_list"),
    path("catalogue/<slug:category_slug>/", product_list, name="product_list_by_category"),
    path("produit/<slug:slug>/", product_detail, name="product_detail"),
]
