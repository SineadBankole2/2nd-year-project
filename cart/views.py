from decimal import Decimal
import logging

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

import stripe
from stripe import StripeError

from cart.models import Cart, CartItem
from loyalty.models import Loyalty
from order.models import Order, OrderItem
from store.models import Product, Size
from vouchers.forms import VoucherApplyForm
from vouchers.models import Voucher

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

    if not request.user.is_authenticated:
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
    """Cart page + start Stripe Checkout."""
    voucher = None
    voucher_discount_amount = Decimal('0')
    loyalty_points_discount = Decimal('0')
    cashback_points = 0

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum((item.product.price * item.quantity) for item in cart_items) if cart_items else Decimal('0')
    except Cart.DoesNotExist:
        cart, cart_items, total = None, [], Decimal('0')

    # Apply voucher (if one has been stored in session by your voucher view)
    if request.session.get('voucher_id'):
        try:
            voucher = Voucher.objects.get(id=request.session['voucher_id'], active=True)
            voucher_discount_amount = (Decimal(voucher.discount) / Decimal('100')) * total
        except Voucher.DoesNotExist:
            request.session['voucher_id'] = None
            voucher = None
            voucher_discount_amount = Decimal('0')

    # Total after voucher
    subtotal_after_voucher = total - voucher_discount_amount
    final_total = subtotal_after_voucher

    # Loyalty points application (when user submits the form)
    if request.user.is_authenticated:
        loyalty_account, _ = Loyalty.objects.get_or_create(user=request.user)
    else:
        loyalty_account = None

    if request.method == 'POST' and loyalty_account:
        requested_points = int(request.POST.get('requested_points', 0))
        if requested_points > 0:
            # NOTE: using your existing API which returns (discount_amount, cashback_points)
            loyalty_points_discount, cashback_points = loyalty_account.convert_points_to_discount(
                requested_points, subtotal_after_voucher
            )

        final_total = subtotal_after_voucher - Decimal(loyalty_points_discount)
        if final_total < 0:
            final_total = Decimal('0')

        # Deduct *points* used. Your code previously did: points -= int(discount_amount)
        # Keeping that behavior for compatibility.
        loyalty_account.points = max(0, loyalty_account.points - int(loyalty_points_discount))
        loyalty_account.save()

        # Stash for success page + order creation
        request.session['used_loyalty_points'] = int(loyalty_points_discount)
        request.session['cashback_points'] = int(cashback_points)
        request.session['total_amount'] = float(final_total)

        if cart:
            request.session['active_cart_id'] = cart.cart_id

        # Build success URL back to our site
        success_url = request.build_absolute_uri(
            reverse('cart:payment_success')
        ) + f'?session_id={{CHECKOUT_SESSION_ID}}&voucher_id={(voucher.id if voucher else "")}&cart_total={subtotal_after_voucher}'

        # Include customer_email so Stripe returns it
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': 'Shopping Cart'},
                    'unit_amount': int(final_total * 100),  # cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=request.build_absolute_uri('/cart/cancel/'),
            customer_email=request.user.email if request.user.is_authenticated else None,
        )
        return redirect(checkout_session.url)

    voucher_apply_form = VoucherApplyForm()

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'new_total': subtotal_after_voucher,              # after voucher
        'final_total': final_total,                       # after voucher + points
        'voucher': voucher,
        'discount': voucher_discount_amount,              # keep key name 'discount' if your template expects it
        'loyalty_points': loyalty_account.points if loyalty_account else 0,
        'cashback_points': cashback_points,
        'voucher_apply_form': voucher_apply_form,
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
    """Create an Order from the Stripe checkout session and current Cart."""
    try:
        session_id = request.GET.get('session_id')
        voucher_id = request.GET.get('voucher_id')

        if not session_id:
            raise ValueError("Session ID not found.")

        logger.info(f"Stripe Session ID: {session_id}")

        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except StripeError as e:
            logger.error(f"Stripe Error: {e}", exc_info=True)
            messages.error(request, f"Stripe error: {e}")
            return redirect("store:all_products")

        # --- SAFE GETTERS ---
        cd = getattr(session, "customer_details", None)

        def _get_attr(obj, name, default=""):
            try:
                val = getattr(obj, name) if obj is not None else None
            except Exception:
                val = None
            return val if val is not None else default

        # email & name
        user_email = (request.user.email if request.user.is_authenticated else "") or _get_attr(cd, "email", "")
        full_name = (request.user.get_full_name() if request.user.is_authenticated else "") or _get_attr(cd, "name", "")

        # address
        addr = _get_attr(cd, "address", None)
        line1 = _get_attr(addr, "line1", "")
        city = _get_attr(addr, "city", "")
        postcode = _get_attr(addr, "postal_code", "")
        country = _get_attr(addr, "country", "")

        # Create order (keep total equal to Stripe amount actually paid)
        order_details = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            token=session.id,
            total=Decimal(session.amount_total) / Decimal('100'),
            emailAddress=user_email,
            billingName=full_name or "",
            billingAddress1=line1 or "",
            billingCity=city or "",
            billingPostcode=postcode or "",
            billingCountry=country or "",
            shippingName=full_name or "",
            shippingAddress1=line1 or "",
            shippingCity=city or "",
            shippingPostcode=postcode or "",
            shippingCountry=country or "",
        )

        # Attach voucher metadata (do NOT change total here)
        if voucher_id:
            try:
                voucher = get_object_or_404(Voucher, id=voucher_id)
                order_details.voucher = voucher
                order_details.discount = voucher.discount  # percent 0–100
                order_details.save(update_fields=["voucher", "discount"])
            except Exception as e:
                logger.warning(f"Voucher metadata attachment skipped: {e}")

        # --- CART & ITEMS ---
        cart_id = _cart_id(request)
        try:
            cart = Cart.objects.get(cart_id=cart_id)
            cart_items = CartItem.objects.filter(cart=cart, active=True)
        except ObjectDoesNotExist:
            logger.error("Cart not found or empty.")
            messages.error(request, "Cart not found or empty while creating order.")
            return redirect("store:all_products")

        # Build each OrderItem; set product_ref so detail page can show image + allow review
        for ci in cart_items:
            OrderItem.objects.create(
                order=order_details,
                product=ci.product.name,    # legacy display name
                product_ref=ci.product,     # ✅ important for images + review link
                quantity=ci.quantity,
                price=ci.product.price,     # unit price
            )
            # reduce stock
            p = ci.product
            p.stock = max(0, p.stock - ci.quantity)
            p.save()

        # clear cart
        cart_items.delete()
        if not cart.cartitem_set.exists():
            cart.delete()
            request.session.pop('active_cart_id', None)

        logger.info(
            f"Order #{order_details.id} created for {user_email} "
            f"(user_id={order_details.user_id}, addr_present={bool(line1 or city or postcode or country)})"
        )
        return redirect('cart:thank_you')

    except Exception as e:
        logger.error(f"Unexpected error in create_order: {e}", exc_info=True)
        messages.error(request, f"Order creation error: {e}")
        return redirect("cart:thank_you")


def thank_you(request):
    if request.user.is_authenticated:
        latest_order = (
            Order.objects
            .filter(Q(user=request.user) | Q(emailAddress__iexact=request.user.email))
            .order_by('-created')
            .first()
        )
        order_items = OrderItem.objects.filter(order=latest_order) if latest_order else []
        loyalty_points = Loyalty.objects.filter(user=request.user).values_list('points', flat=True).first() or 0
    else:
        latest_order, order_items, loyalty_points = None, [], 0

    return render(request, 'cart/thank_you.html', {
        'order': latest_order,
        'order_items': order_items,
        'loyalty_points': loyalty_points,
    })
