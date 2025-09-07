from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from .models import Wishlist
from store.models import Product, Size


User = get_user_model()


def add_to_wishlist(request, product_id):
    size = request.GET.get('size') 
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        customer = request.user
    else:
        return redirect('cos_accounts:signup')

    
    size_id = request.GET.get('size')

    if size_id:
        size = get_object_or_404(Size, id=size_id)
        
    
        wishlist_item, created = Wishlist.objects.get_or_create(
            customer=customer, 
            product=product,
            size=size  
        )
    else:
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            customer=customer, 
            product=product
        )

    return redirect('wishlist:wishlist_view')  

def wishlist_view(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(customer=request.user)
        return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})
    else:
    
        return render(request, 'wishlist.html', {'wishlist_items': [], 'message': 'Please sign in to view your wishlist.'})


def remove_from_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    customer = request.user
    wishlist_item = get_object_or_404(Wishlist, customer=customer, product_id=product_id)
    wishlist_item.delete()
    return redirect('wishlist:wishlist_view')


