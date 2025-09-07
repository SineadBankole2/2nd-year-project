from django.shortcuts import redirect, render, get_object_or_404
from store.models import Product, Size
from cart.models import Cart, CartItem
from loyalty.models import Loyalty
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
from order.models import Order, OrderItem
from stripe import StripeError
import logging
from vouchers.models import Voucher
from vouchers.forms import VoucherApplyForm
from decimal import Decimal
from store.models import Product
from django.contrib import messages

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    size_value = request.GET.get('size')
    product = get_object_or_404(Product, id=product_id)

    if not size_value:
        return redirect('store:all_products')

    try:
        if size_value.isdigit():
            size = get_object_or_404(Size, id=int(size_value))
        else:
            size = get_object_or_404(Size, name=size_value)
    except Size.DoesNotExist:
        return redirect('store:all_products')

    if request.user.is_authenticated:
        customer = request.user
    else:
        return redirect('login')

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart:cart_detail')

def cart_detail(request):
    discount = 0
    voucher_id = 0
    new_total = 0
    voucher = None

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.product.price * item.quantity for item in cart_items)

        if 'voucher_id' in request.session:
            try:
                voucher = Voucher.objects.get(id=request.session['voucher_id'], active=True)
                discount = (Decimal(voucher.discount) / Decimal('100')) * Decimal(total)
                new_total = total - discount
            except Voucher.DoesNotExist:
                request.session['voucher_id'] = None
                discount = 0
                new_total = total
        else:
            new_total = total

    except Cart.DoesNotExist:
        cart_items = []
        total = 0
        cart = None

    final_total = total
    cashback_points = 0

    if request.user.is_authenticated:
        loyalty_account, _ = Loyalty.objects.get_or_create(user=request.user)
    else:
        loyalty_account = None

    if request.method == 'POST' and loyalty_account:
        requested_points = int(request.POST.get('requested_points', 0))
        if requested_points > 0:
            discount, cashback_points = loyalty_account.convert_points_to_discount(requested_points, total)

        final_total = total - discount if total >= discount else 0

    
        loyalty_account.points = max(0, loyalty_account.points - int(discount))
        loyalty_account.save()

        request.session['used_loyalty_points'] = int(discount)
        request.session['cashback_points'] = int(cashback_points)
        request.session['total_amount'] = float(final_total)

        if cart:
            request.session['active_cart_id'] = cart.cart_id

     
        success_url = request.build_absolute_uri(
            reverse('cart:payment_success')
        ) + f'?session_id={{CHECKOUT_SESSION_ID}}&voucher_id={(voucher.id if voucher else "")}&cart_total={(new_total or total)}'

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': 'Shopping Cart',
                        },
                        'unit_amount': int(final_total * 100),
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=request.build_absolute_uri('/cart/cancel/'),
        )

        return redirect(checkout_session.url)

    voucher_apply_form = VoucherApplyForm()

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'final_total': final_total,
        'loyalty_points': loyalty_account.points if loyalty_account else 0,
        'cashback_points': cashback_points,
        'voucher_apply_form': voucher_apply_form,
        'new_total': new_total,
        'voucher': voucher,
        'discount': discount
    })

def cart_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to access your cart.')
        return redirect('login')

    cart_items = request.session.get('cart', [])
    selected_items = request.POST.getlist('selected_items')

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('homepage')

    if selected_items:
        selected_cart_items = [item for item in cart_items if str(item['product_id']) in selected_items]
    else:
        selected_cart_items = cart_items

    total = sum(item['product'].price * item['quantity'] for item in selected_cart_items)

    context = {
        'cart_items': selected_cart_items,
        'total': total,
    }

    return render(request, 'cart/cart.html', context)

def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    cart_items = CartItem.objects.filter(product=product, cart=cart)

    if cart_items.exists():
        cart_item = cart_items.first()
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('cart:cart_detail')

def full_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart_detail')

def payment_success(request):
    
    session_id = request.GET.get('session_id')
    voucher_id = request.GET.get('voucher_id')
    cart_total = request.GET.get('cart_total')

    if request.user.is_authenticated:
        loyalty_account, _ = Loyalty.objects.get_or_create(user=request.user)

      
        discount_used = int(request.session.pop('used_loyalty_points', 0))
        cashback_points = int(request.session.pop('cashback_points', 0))
        total_amount_spent = float(request.session.pop('total_amount', 0))

        if cashback_points > 0:
            loyalty_account.points += cashback_points

     
        if total_amount_spent > 0:
            points_earned = int(Decimal(str(total_amount_spent)) * Decimal('0.1'))
            loyalty_account.points += points_earned
        else:
            points_earned = 0

        loyalty_account.save()

        messages.success(
            request,
            f"You earned {cashback_points + points_earned} loyalty points. New balance: {loyalty_account.points}."
        )

    create_order_url = (
        reverse('cart:new_order')
        + f'?session_id={session_id or ""}&voucher_id={voucher_id or ""}&cart_total={cart_total or ""}'
    )
    return redirect(create_order_url)

def empty_cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = cart.cartitem_set.all()

        if cart_items.exists():
            logger.info(f"Deleting {cart_items.count()} cart items for cart ID: {cart.cart_id}")
            cart_items.delete()

        logger.info(f"Deleting cart with ID: {cart.cart_id}")
        cart.delete()

    except Cart.DoesNotExist:
        logger.info("Cart does not exist, skipping deletion.")
        pass

    return redirect('cart:cart_detail')

def create_order(request):
    try:
        session_id = request.GET.get('session_id')
        cart_total = request.GET.get('cart_total')
        voucher_id = request.GET.get('voucher_id')
        if not session_id:
            raise ValueError("Session ID not found.")

        logger.info(f"Stripe Session ID: {session_id}")

        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except StripeError as e:
            logger.error(f"Stripe Error: {e}")
            return redirect("store:all_products")

        customer_details = session.customer_details
        if not customer_details or not customer_details.address:
            raise ValueError("Missing Stripe customer address info.")

        order_details = Order.objects.create(
            token=session.id,
            total=session.amount_total / 100,
            emailAddress=customer_details.email,
            billingName=customer_details.name,
            billingAddress1=customer_details.address.line1,
            billingCity=customer_details.address.city,
            billingPostcode=customer_details.address.postal_code,
            billingCountry=customer_details.address.country,
            shippingName=customer_details.name,
            shippingAddress1=customer_details.address.line1,
            shippingCity=customer_details.address.city,
            shippingPostcode=customer_details.address.postal_code,
            shippingCountry=customer_details.address.country,
        )
        order_details.save()

        cart_id = _cart_id(request)

        try:
            cart = Cart.objects.get(cart_id=cart_id)
            all_cart_items = CartItem.objects.filter(cart=cart, active=True)
        except ObjectDoesNotExist:
            logger.error("Cart not found or empty.")
            return redirect("store:all_products")

        selected_items_raw = request.POST.getlist('selected_items')
        if selected_items_raw:
            selected_items = []
            for item in selected_items_raw:
                try:
                    product_id, size = item.split(":")
                    product_id = int(product_id)
                    size = size.strip()
                    cart_item = all_cart_items.filter(product__id=product_id, size=size).first()
                    if cart_item:
                        selected_items.append(cart_item)
                except Exception as e:
                    logger.warning(f"Skipping malformed selected item '{item}': {e}")
            cart_items = selected_items
        else:
            cart_items = all_cart_items

        if voucher_id:
            voucher = get_object_or_404(Voucher, id=voucher_id)
            if voucher:
                order_details.voucher = voucher
                cart_total = Decimal(cart_total)
                order_details.discount = cart_total * (voucher.discount / Decimal('100'))
                order_details.total = (cart_total - order_details.discount)
                order_details.save()

        for item in cart_items:
            try:
                oi = OrderItem.objects.create(
                    product=item.product.name,
                    quantity=item.quantity,
                    price=item.product.price,
                    order=order_details
                )

                product = item.product
                product.stock = max(0, product.stock - item.quantity)
                product.save()

                if voucher_id:
                    discount = (oi.price * (voucher.discount / Decimal('100')))
                    oi.price = (oi.price - discount)
                else:
                    oi.price = oi.price * oi.quantity
                oi.save()
            except Exception as e:
                logger.error(f"Error creating OrderItem: {e}")
                return redirect("store:all_products")

        for item in cart_items:
            item.delete()

        if not cart.cartitem_set.exists():
            cart.delete()
            request.session.pop('active_cart_id', None)
            logger.info("Cart emptied successfully.")

        return redirect('cart:thank_you')

    except Exception as e:
        logger.error(f"Unexpected error in create_order: {e}")
        empty_cart(request)
        return redirect("cart:thank_you")

def thank_you(request):
    if request.user.is_authenticated:
        latest_order = Order.objects.filter(emailAddress=request.user.email).order_by('-created').first()
        order_items = OrderItem.objects.filter(order=latest_order) if latest_order else []
        
        loyalty_points = Loyalty.objects.filter(user=request.user).values_list('points', flat=True).first() or 0
    else:
        latest_order = None
        order_items = []
        loyalty_points = 0

    return render(request, 'cart/thank_you.html', {
        'order': latest_order,
        'order_items': order_items,
        'loyalty_points': loyalty_points,
    })
