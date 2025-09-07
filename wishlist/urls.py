from django.urls import path, include
from .views import add_to_wishlist, wishlist_view, remove_from_wishlist
from pages.views import homepage



app_name = 'wishlist'  

urlpatterns = [
    path('add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('', wishlist_view, name='wishlist_view'),
    path('remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('home/', homepage, name='home'),
]


