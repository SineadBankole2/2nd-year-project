from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.decorators import login_required




@login_required(login_url='/accounts/signin/')
def order_history(request):
    email = request.user.email
    order_details = Order.objects.filter(emailAddress=email)
    return render(request, 'orders_list.html', {'order_details': order_details})


@login_required(login_url='/accounts/signin/')
def order_detail(request, order_id):
    email = request.user.email
    order = get_object_or_404(Order, id=order_id, emailAddress=email)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'orders_list.html', {'order': order, 'order_items': order_items})


@login_required(login_url='/accounts/signin/')
def cancel_order(request, order_id):
    email = request.user.email
    order = get_object_or_404(Order, id=order_id, emailAddress=email)

    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled successfully.")
    else:
        messages.warning(request, f"Order #{order.id} is already cancelled.")

    return redirect('order_history')







