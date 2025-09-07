from django.contrib import admin
from .models import Category, Product, Customer, Size, ProductSize


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent'] 
    search_fields = ['name']  
    list_filter = ['parent']  

admin.site.register(Category, CategoryAdmin)


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1  
    fields = ['size', 'quantity']  
    min_num = 1  


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity_in_stock') 
    search_fields = ('name',) 
    list_filter = ('category',)  
    inlines = [ProductSizeInline]  


admin.site.register(Product, ProductAdmin)
admin.site.register(Customer)
admin.site.register(Size)
admin.site.register(ProductSize)






