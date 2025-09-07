from django.contrib import admin
from .models import Wishlist

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'added_at')  
 

admin.site.register(Wishlist, WishlistAdmin)
