from decimal import Decimal


class Cart:
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(self.SESSION_KEY, {})

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.pk)
        current_quantity = self.cart.get(product_id, {}).get("quantity", 0)
        new_quantity = quantity if override_quantity else current_quantity + quantity
        quantity_capped = min(max(new_quantity, 1), product.stock) if product.stock > 0 else 0

        if quantity_capped <= 0:
            self.cart.pop(product_id, None)
            self.save()
            return

        self.cart[product_id] = {
            "name": product.name,
            "price": str(product.price),
            "quantity": quantity_capped,
            "image": product.image.url if product.image else "",
            "slug": product.slug,
            "stock": product.stock,
        }
        self.save()

    def remove(self, product):
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        for product_id, item in self.cart.items():
            price = Decimal(item["price"])
            quantity = item["quantity"]
            yield {
                "product_id": product_id,
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
