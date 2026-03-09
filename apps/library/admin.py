from django.contrib import admin
from .models import ProductCategory, DigitalProduct, ProductFile, Purchase, Review, Wishlist

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'get_product_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['get_product_count']

@admin.register(DigitalProduct)
class DigitalProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'price', 'is_featured', 'is_active']
    list_filter = ['category', 'format', 'is_featured', 'is_active']
    search_fields = ['title', 'author', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'purchase_count']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'author', 'publisher', 'published_date')
        }),
        ('Content', {
            'fields': ('description', 'short_description', 'tags')
        }),
        ('Media', {
            'fields': ('cover_image', 'image_alt', 'preview_file')
        }),
        ('Product Details', {
            'fields': ('format', 'file_size', 'pages', 'duration', 'isbn')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price', 'is_free', 'stock', 'download_limit')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active', 'views_count', 'purchase_count')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description')
        }),
    )

@admin.register(ProductFile)
class ProductFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'file_type', 'file_size', 'order']
    list_filter = ['file_type']
    search_fields = ['title', 'product__title']

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'amount', 'status', 'purchase_date']
    list_filter = ['status', 'payment_method']
    search_fields = ['user__email', 'product__title', 'transaction_id']
    readonly_fields = ['purchase_date']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'verified_purchase', 'is_approved', 'created_at']
    list_filter = ['rating', 'verified_purchase', 'is_approved']
    search_fields = ['user__email', 'product__title', 'comment']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_date']
    list_filter = ['added_date']
    search_fields = ['user__email', 'product__title']