from django.test import TestCase
from django.urls import reverse
from store.models import Product, Category  

class ProductSearchTestCase(TestCase):
    
    def setUp(self):
        
        category_men = Category.objects.create(name="Men's Clothing")
        Product.objects.create(name="T-shirt", description="Green Men's T-shirt", price=20, category=category_men)
        Product.objects.create(name="Blue Trousers", description="Blue trousers for men", price=35, category=category_men)

    def testSearchingByName(self):
        response = self.client.get(reverse('search'), {'q': 'T-shirt'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T-shirt")
        self.assertNotContains(response, "Blue Trousers")

    def testSearchingByDescription(self):
        response = self.client.get(reverse('search'), {'q': 'Green'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T-shirt")
        self.assertNotContains(response, "Blue Trousers")

    def testNoResults(self):
        response = self.client.get(reverse('search'), {'q': 'Multicolour'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products found matching your search", count=1)
        self.assertNotContains(response, "T-shirt")
        self.assertNotContains(response, "Blue Trousers")
