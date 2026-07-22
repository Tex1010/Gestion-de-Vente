from django import template

register = template.Library()


@register.filter
def in_wishlist(product_id, wishlist_ids):
    """Vérifie si un ID de produit est dans la liste des IDs des favoris."""
    if wishlist_ids is None:
        return False
    return product_id in wishlist_ids