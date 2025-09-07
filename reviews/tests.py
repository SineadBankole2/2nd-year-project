from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product, Category
from .models import Review


class ReviewTests(TestCase):
    def setUp(self):
        self.client = Client()

      
        self.user = User.objects.create_user(username='testuser', password='testpass')

       
        self.category = Category.objects.create(name='Men')
        self.product = Product.objects.create(
            name='Test Shirt',
            description='A test shirt.',
            price=10.00,
            category=self.category
        )

       
        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            review_text='Nice product!',
            rating=5,
            helpful_count=0
        )

    def test_review_list_page_loads(self):
        response = self.client.get(reverse('reviews'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reviews')

    def test_create_review_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('reviews'), {
            'product': self.product.id,
            'review_text': 'Great!',
            'rating': 4
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 2)

    def test_create_review_redirects_when_not_logged_in(self):
        response = self.client.post(reverse('reviews'), {
            'product': self.product.id,
            'review_text': 'Great!',
            'rating': 4
        })
        self.assertRedirects(response, reverse('cos_accounts:signin'))

    def test_like_review_increments_count(self):
        prev_count = self.review.helpful_count
        response = self.client.post(reverse('like_review', args=[self.review.id]))
        self.assertEqual(response.status_code, 200)
        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, prev_count + 1)

    def test_delete_review_by_owner(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_review', args=[self.review.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_cannot_delete_review_by_other_user(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('delete_review', args=[self.review.id]))
        self.assertEqual(response.status_code, 403)  
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())
