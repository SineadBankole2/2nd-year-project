from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from store.models import Product
from .models import Order, OrderItem


@login_required(login_url='/accounts/signin/')
def order_history(request):
    orders = (
        Order.objects
        .filter(Q(user=request.user) | Q(emailAddress__iexact=request.user.email))
        .prefetch_related('orderitem_set')
        .order_by('-created')
    )
    # Combined template handles list & detail
    return render(request, 'orders_list.html', {'order_details': orders})


@login_required(login_url='/accounts/signin/')
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        Q(id=order_id) & (Q(user=request.user) | Q(emailAddress__iexact=request.user.email))
    )

    items = (
        OrderItem.objects
        .filter(order=order)
        .select_related('product_ref')
        .order_by('id')
    )

    # Fallback for older rows with no product_ref: match by product name
    missing_names = [it.product for it in items if it.product_ref_id is None and it.product]
    if missing_names:
        prod_map = {
            p.name.lower(): p
            for p in Product.objects.filter(name__in=missing_names)
        }
        for it in items:
            if it.product_ref_id is None and it.product:
                it.product_ref = prod_map.get(it.product.lower())

    # Render the same combined template
    return render(request, 'orders_list.html', {'order': order, 'order_items': items})


@login_required(login_url='/accounts/signin/')
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order,
        Q(id=order_id) & (Q(user=request.user) | Q(emailAddress__iexact=request.user.email))
    )
    if order.status != Order.OrderStatus.CANCELLED:
        order.status = Order.OrderStatus.CANCELLED
        order.save(update_fields=['status'])
        messages.success(request, f"Order #{order.id} has been cancelled successfully.")
    else:
        messages.warning(request, f"Order #{order.id} is already cancelled.")
    return redirect('order:order_history')
