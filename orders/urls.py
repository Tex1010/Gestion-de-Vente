from django.urls import path

from .views import (
    cancel_order,
    cart_add,
    cart_detail,
    cart_remove,
    cart_update,
    checkout,
    order_success,
)

app_name = "orders"

urlpatterns = [
    path("panier/", cart_detail, name="cart_detail"),
    path("panier/ajouter/<int:product_id>/", cart_add, name="cart_add"),
    path("panier/modifier/<str:item_key>/", cart_update, name="cart_update"),
    path("panier/supprimer/<str:item_key>/", cart_remove, name="cart_remove"),
    path("commande/", checkout, name="checkout"),
    path("commande/succes/<int:order_id>/", order_success, name="order_success"),
    path("commande/annuler/<int:order_id>/", cancel_order, name="cancel_order"),
]
