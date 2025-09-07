from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Voucher

class VoucherApplyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('vouchers:apply')
        self.valid_voucher = Voucher.objects.create(
            code='DISCOUNT10',
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1),
            discount=10,
            active=True
        )
        self.expired_voucher = Voucher.objects.create(
            code='EXPIRED',
            valid_from=timezone.now() - timezone.timedelta(days=10),
            valid_to=timezone.now() - timezone.timedelta(days=5),
            discount=15,
            active=True
        )
        self.inactive_voucher = Voucher.objects.create(
            code='INACTIVE',
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1),
            discount=20,
            active=False
        )

    def test_apply_valid_voucher(self):
        response = self.client.post(self.url, {'code': 'DISCOUNT10', 'next': reverse('cart:cart_detail')})
        self.assertEqual(self.client.session.get('voucher_id'), self.valid_voucher.id)
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_apply_invalid_voucher(self):
        response = self.client.post(self.url, {'code': 'NOTEXIST', 'next': reverse('cart:cart_detail')})
        self.assertIsNone(self.client.session.get('voucher_id'))
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_apply_expired_voucher(self):
        response = self.client.post(self.url, {'code': 'EXPIRED', 'next': reverse('cart:cart_detail')})
        self.assertIsNone(self.client.session.get('voucher_id'))
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_apply_inactive_voucher(self):
        response = self.client.post(self.url, {'code': 'INACTIVE', 'next': reverse('cart:cart_detail')})
        self.assertIsNone(self.client.session.get('voucher_id'))
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_apply_redirects_to_next_url(self):
        response = self.client.post(self.url, {'code': 'DISCOUNT10', 'next': '/somewhere/'})
        self.assertRedirects(response, '/somewhere/')
