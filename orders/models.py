from decimal import Decimal

from django.db import models

from catalog.models import Product


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PREPARING = "preparing"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_CONFIRMED, "Confirmee"),
        (STATUS_PREPARING, "En preparation"),
        (STATUS_DELIVERED, "Livree"),
        (STATUS_CANCELLED, "Annulee"),
    ]

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    def __str__(self):
        return f"Commande #{self.pk} - {self.full_name}"

    def recalculate_total(self):
        total = sum(
            (item.unit_price * item.quantity for item in self.items.all()),
            start=Decimal("0.00"),
        )
        self.total_amount = total
        self.save(update_fields=["total_amount", "updated_at"])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    product_name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Article commande"
        verbose_name_plural = "Articles commande"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
