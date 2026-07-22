from .models import Wishlist


def wishlist_ids(request):
    """Fournit la liste des IDs des produits dans les favoris de l'utilisateur connecté."""
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)
        )
    else:
        wishlist_ids = []
    return {"wishlist_ids": wishlist_ids, "is_in_wishlist": lambda pid: pid in wishlist_ids}