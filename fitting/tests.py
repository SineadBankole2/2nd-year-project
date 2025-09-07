from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import SizeProfile

class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('fitting:profile')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  

    def test_get_creates_profile_if_missing(self):
        self.client.login(username='testuser', password='testpass')
        self.assertFalse(SizeProfile.objects.filter(user=self.user).exists())

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SizeProfile.objects.filter(user=self.user).exists())
        self.assertTemplateUsed(response, 'fitting/profile.html')

    def test_get_uses_existing_profile(self):
        profile = SizeProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], profile)

    def test_post_updates_profile(self):
        self.client.login(username='testuser', password='testpass')
        profile = SizeProfile.objects.create(user=self.user)

        data = {
            'height': 180,
            'weight': 75,
            'waist': 32
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertEqual(profile.height, 180)
        self.assertEqual(profile.weight, 75)
        self.assertEqual(profile.waist, 32)
