from django.contrib import admin
from .models import Category, Product, DailyOffer

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DailyOffer)
class DailyOfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'active', 'created']
    list_filter = ['active', 'created']
    list_editable = ['active']