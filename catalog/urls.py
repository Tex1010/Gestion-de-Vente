from django.urls import path

from .views import product_detail

app_name = "catalog"

urlpatterns = [
    path("produit/<slug:slug>/", product_detail, name="product_detail"),
]
