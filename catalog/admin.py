from django.contrib import admin

from .models import Banner, Category, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ["image", "alt_text", "is_primary", "order"]


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ["name", "sku", "price_adjustment", "stock", "is_active", "order"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "product_count", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["is_active"]

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Produits"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name", "category", "price", "stock", "is_active",
        "is_featured", "on_sale", "created_at"
    ]
    list_filter = ["is_active", "is_featured", "on_sale", "category"]
    search_fields = ["name", "sku", "short_description"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["is_active", "is_featured", "on_sale", "price", "stock"]
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = [
        ("Informations générales", {
            "fields": ["category", "name", "slug", "short_description", "description"]
        }),
        ("Prix et promotion", {
            "fields": ["price", "old_price", "on_sale"]
        }),
        ("Stock et référence", {
            "fields": ["sku", "stock", "weight", "dimensions"]
        }),
        ("Image", {
            "fields": ["image"]
        }),
        ("SEO", {
            "fields": ["meta_title", "meta_description"],
            "classes": ["collapse"]
        }),
        ("Statut", {
            "fields": ["is_active", "is_featured"]
        }),
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "is_primary", "order", "created_at"]
    list_filter = ["is_primary"]
    search_fields = ["product__name"]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["product", "name", "sku", "stock", "price_adjustment", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["product__name", "name", "sku"]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["title", "position", "is_active", "order", "created_at"]
    list_filter = ["position", "is_active"]
    list_editable = ["is_active", "order"]