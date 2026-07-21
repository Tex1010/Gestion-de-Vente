from decimal import Decimal


class Cart:
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(self.SESSION_KEY, {})

    def _get_item_key(self, product, variant=None):
        variant_key = variant.pk if variant else "base"
        return f"{product.pk}__{variant_key}"

    def _get_stock_limit(self, product, variant=None):
        if variant is not None:
            return variant.stock
        return product.stock

    def add(self, product, quantity=1, override_quantity=False, variant=None):
        item_key = self._get_item_key(product, variant)
        current_quantity = self.cart.get(item_key, {}).get("quantity", 0)
        new_quantity = quantity if override_quantity else current_quantity + quantity
        stock_limit = self._get_stock_limit(product, variant)
        quantity_capped = min(max(new_quantity, 1), stock_limit) if stock_limit > 0 else 0

        if quantity_capped <= 0:
            self.cart.pop(item_key, None)
            self.save()
            return

        unit_price = variant.effective_price if variant else product.price
        self.cart[item_key] = {
            "product_id": product.pk,
            "variant_id": variant.pk if variant else None,
            "variant_name": variant.name if variant else "",
            "name": product.name,
            "price": str(unit_price),
            "quantity": quantity_capped,
            "image": product.image.url if product.image else "",
            "slug": product.slug,
            "stock": stock_limit,
        }
        self.save()

    def remove(self, item_key):
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def __iter__(self):
        for item_key, item in self.cart.items():
            price = Decimal(item["price"])
            quantity = item["quantity"]
            yield {
                "item_key": item_key,
                "product_id": item["product_id"],
                "variant_id": item.get("variant_id"),
                "variant_name": item.get("variant_name", ""),
                "name": item["name"],
                "price": price,
                "quantity": quantity,
                "image": item.get("image", ""),
                "slug": item.get("slug", ""),
                "stock": item.get("stock", 0),
                "subtotal": price * quantity,
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def clear(self):
        self.session.pop(self.SESSION_KEY, None)
        self.session.modified = True

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True
