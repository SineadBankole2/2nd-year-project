from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Loyalty
from .views import create_loyalty_for_user

class LoyaltyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('view_loyalty')  

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  

    def test_view_loyalty_creates_new_if_missing(self):
        self.client.login(username='testuser', password='testpass')
        self.assertFalse(Loyalty.objects.filter(user=self.user).exists())

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Loyalty.objects.filter(user=self.user).exists())
        self.assertTemplateUsed(response, 'loyalty/view_loyalty.html')

    def test_view_loyalty_loads_existing_record(self):
        Loyalty.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loyalty/view_loyalty.html')

    def test_create_loyalty_for_user_creates_record(self):
        self.assertFalse(Loyalty.objects.filter(user=self.user).exists())
        create_loyalty_for_user(self.user)
        self.assertTrue(Loyalty.objects.filter(user=self.user).exists())

    def test_create_loyalty_for_user_does_not_duplicate(self):
        Loyalty.objects.create(user=self.user)
        create_loyalty_for_user(self.user)
        self.assertEqual(Loyalty.objects.filter(user=self.user).count(), 1)
