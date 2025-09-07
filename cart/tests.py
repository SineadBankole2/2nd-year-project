from django.test import TestCase, Client
from django.urls import reverse
from store.models import Product, Size
from cart.models import Cart, CartItem
from loyalty.models import Loyalty
from order.models import Order, OrderItem
from vouchers.models import Voucher
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

class CartViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.product = Product.objects.create(name='Test Product', price=Decimal('10.00'), stock=10)
        self.size = Size.objects.create(name='M')
        self.voucher = Voucher.objects.create(
            code='SAVE10',
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1),
            discount=10,
            active=True
        )
        self.cart = Cart.objects.create(cart_id='testcartid')
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2, size=self.size)

    def test_add_cart_authenticated(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('cart:add_cart', args=[self.product.id])
        response = self.client.get(f"{url}?size={self.size.id}")
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_add_cart_unauthenticated_redirects_to_login(self):
        url = reverse('cart:add_cart', args=[self.product.id])
        response = self.client.get(f"{url}?size={self.size.id}")
        self.assertRedirects(response, reverse('login'))

    def test_cart_detail_no_cart(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0")  # total should be 0

    def test_cart_detail_with_voucher(self):
        session = self.client.session
        session['voucher_id'] = self.voucher.id
        session.save()

        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1, size=self.size)
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shopping Cart')  # your page title probably

    def test_cart_remove_item(self):
        self.client.session['cart_id'] = self.cart.cart_id
        self.client.session.save()
        url = reverse('cart:cart_remove', args=[self.product.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_full_remove_item(self):
        self.client.session['cart_id'] = self.cart.cart_id
        self.client.session.save()
        url = reverse('cart:full_remove', args=[self.product.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('cart:cart_detail'))
        self.assertFalse(CartItem.objects.filter(cart=self.cart, product=self.product).exists())

    def test_empty_cart(self):
        self.client.session['cart_id'] = self.cart.cart_id
        self.client.session.save()
        response = self.client.get(reverse('cart:empty_cart'))
        self.assertRedirects(response, reverse('cart:cart_detail'))
        self.assertFalse(Cart.objects.filter(cart_id=self.cart.cart_id).exists())

    def test_payment_success_authenticated(self):
        self.client.login(username='testuser', password='12345')
        session = self.client.session
        session['used_loyalty_points'] = 10
        session['cashback_points'] = 5
        session['total_amount'] = 100
        session.save()
        response = self.client.get(reverse('cart:payment_success'))
        self.assertRedirects(response, reverse('homepage'))

    def test_thank_you_page_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('cart:thank_you'))
        self.assertEqual(response.status_code, 200)

    def test_thank_you_page_unauthenticated(self):
        response = self.client.get(reverse('cart:thank_you'))
        self.assertEqual(response.status_code, 200)
