from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product
from reviews.forms import ReviewForm

class HomeAndCategoryViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

      
        self.men_category = Category.objects.create(name='Men')
        self.women_category = Category.objects.create(name='women')
        self.kids_category = Category.objects.create(name='kids')

    
        self.men_product = Product.objects.create(name='Men Shirt', price=20.0, category=self.men_category)
        self.women_product = Product.objects.create(name='Women Dress', price=30.0, category=self.women_category)
        self.kids_product = Product.objects.create(name='Kids Shorts', price=15.0, category=self.kids_category)

    def test_homepage_view(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_mens_view(self):
        response = self.client.get(reverse('mens_view'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mens.html')
        self.assertIn(self.men_product, response.context['products'])
        self.assertIsInstance(response.context['review_form'], ReviewForm)

    def test_womens_view(self):
        response = self.client.get(reverse('womens_view'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'womens.html')
        self.assertIn(self.women_product, response.context['products'])
        self.assertIsInstance(response.context['review_form'], ReviewForm)

    def test_kids_view(self):
        response = self.client.get(reverse('kids_view'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kids.html')
        self.assertIn(self.kids_product, response.context['products'])
        self.assertIsInstance(response.context['review_form'], ReviewForm)
