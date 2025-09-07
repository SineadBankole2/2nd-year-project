from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model

class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.signin_url = reverse('signin')
        self.logout_url = reverse('logout')
        self.change_password_url = reverse('change_password')
        self.homepage_url = reverse('homepage')

        self.user = get_user_model().objects.create_user(username='testuser', password='testpass123')

   

    def test_signup_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_post_valid(self):
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.homepage_url)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_post_invalid(self):
        response = self.client.post(self.signup_url, {
            'username': '',
            'password1': 'x',
            'password2': 'y',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
        self.assertContains(response, 'This field is required')

   
    def test_signin_get(self):
        response = self.client.get(self.signin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_in.html')

    def test_signin_post_valid(self):
        response = self.client.post(self.signin_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.homepage_url)

    def test_signin_post_invalid(self):
        response = self.client.post(self.signin_url, {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_in.html')
        self.assertContains(response, 'Invalid username or password')

   

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.homepage_url)

    

    def test_change_password_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')

    def test_change_password_post_valid(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.change_password_url, {
            'old_password': 'testpass123',
            'new_password1': 'newsecurepass456',
            'new_password2': 'newsecurepass456'
        })
        self.assertRedirects(response, self.homepage_url)

      
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newsecurepass456'))

    def test_change_password_post_invalid(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.change_password_url, {
            'old_password': 'wrongold',
            'new_password1': 'newpass',
            'new_password2': 'newpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')
        self.assertContains(response, 'Your old password was entered incorrectly.')
