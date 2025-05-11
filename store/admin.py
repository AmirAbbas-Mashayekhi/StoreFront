from decimal import Decimal
from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.utils.html import format_html, urlencode
from django.urls import reverse

from store.forms import PromotionSelectionForm
from . import models
from .models import ProductImage


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [
            ("<10", "Low (<10)"),
            (">=100", "High (≥100)"),
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)
        if self.value() == ">=100":
            return queryset.filter(inventory__gte=100)
        return queryset


# TODO: Permission issue with /media
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    readonly_fields = ["thumbnail"]

    def thumbnail(self, instance):
        if instance.image.name != "":
            return format_html(f'<img src="{instance.image.url}" class="thumbnail">')
        return ""


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ["collection", "promotions"]
    prepopulated_fields = {"slug": ["title"]}
    actions = ["clear_inventory", "add_to_promotion"]
    inlines = [ProductImageInline]
    list_display = ["title", "unit_price", "inventory_status", "collection_title"]
    list_editable = ["unit_price"]
    list_filter = ["collection", "last_update", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]
    search_fields = ["title"]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        return "Low" if product.inventory < 10 else "OK"

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f"{updated_count} products were successfully updated.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Add products to a promotion")
    def add_to_promotion(self, request, queryset):
        if "apply" in request.POST:
            form = PromotionSelectionForm(request.POST)
            if form.is_valid():
                promo = form.cleaned_data["promotion"]
                for p in queryset:
                    if promo not in p.promotions.all():
                        p.promotions.add(promo)
                        p.unit_price = p.unit_price - (
                            p.unit_price * Decimal(promo.discount)
                        )
                        p.save()
                self.message_user(
                    request,
                    f"Added {queryset.count()} products to promotion '{promo}'.",
                    level=messages.SUCCESS,
                )
                return redirect(request.get_full_path())
        else:
            form = PromotionSelectionForm()

        # capture the original action name
        action_name = request.POST.get("action", "add_to_promotion")

        context = {
            **self.admin_site.each_context(request),
            "title": f"Select a promotion to apply",
            "queryset": queryset,
            "form": form,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
            "action_name": action_name,
        }
        return render(request, "admin/add_to_promotion.html", context)

    class Media:
        css = {"all": ["store/styles.css"]}


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ["featured_product"]
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html(
            '<a href="{}">{} Products</a>', url, collection.products_count
        )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("products"))


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders"]
    list_editable = ["membership"]
    list_per_page = 10
    list_select_related = ["user"]
    ordering = ["user__first_name", "user__last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="orders_count")
    def orders(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count("order"))


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]
    list_display = ["id", "placed_at", "customer"]


@admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ["description", "discount"]
    search_fields = ["description"]
