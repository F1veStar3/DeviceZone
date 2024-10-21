from django.contrib import admin
from .models import Category, Brand, Product, Promo, Banner, Color, ProductAttribute, LikedProduct, CartItem, Cart, Customer, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_available')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'alt_text', 'is_available')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'final_price', 'is_available', 'created_at')

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('title', 'alt_text', 'in_index_page', 'redirect_product')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('alt_text', 'is_available')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('product', 'color',)

@admin.register(LikedProduct)
class LikedProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'user')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'color', 'final_price_by_product')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'total_items', 'total_price', 'in_order', 'for_anonymous_user')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'payment_method', 'created_at')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')


