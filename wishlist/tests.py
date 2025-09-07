from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from store.models import Product, Category  
from wishlist.models import Wishlist

User = get_user_model()

class WishlistTestCase(TestCase):
   
    def setUp(self):
       
        self.category = Category.objects.create(name="Men's Clothing")
       
       
        self.user = User.objects.create_user(username='testuser', password='testpass')
       
       
        self.product_1 = Product.objects.create(name="T-shirt", description="Green Men's T-shirt", price=20, category=self.category)
        self.product_2 = Product.objects.create(name="Blue Trousers", description="Blue trousers for men", price=35, category=self.category)
       
       
        self.client.login(username='testuser', password='testpass')
   
    def testAddingToWishlist(self):
        response = self.client.get(reverse('wishlist:add_to_wishlist', args=[self.product_1.id]))
       
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Wishlist.objects.count(), 1)  
       
        wishlist_item = Wishlist.objects.first()
        self.assertEqual(wishlist_item.product, self.product_1)
        self.assertEqual(wishlist_item.customer, self.user)

    def testAddingToWishlistByAGuest(self):
        self.client.logout()
       
        response = self.client.get(reverse('wishlist:add_to_wishlist', args=[self.product_1.id]))
       
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/wishlist/add/1/')  

    def testViewingWishlistByCustomer(self):
       
        Wishlist.objects.create(customer=self.user, product=self.product_1)
        Wishlist.objects.create(customer=self.user, product=self.product_2)
       
        response = self.client.get(reverse('wishlist:wishlist_view'))
       
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product_1.name)
        self.assertContains(response, self.product_2.name)

    def testViewingWishlistByGuest(self):
        self.client.logout()
       
        response = self.client.get(reverse('wishlist:wishlist_view'))
       
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please sign in to view your wishlist")
        self.assertNotContains(response, self.product_1.name)
        self.assertNotContains(response, self.product_2.name)

    def testRemovingFromWishlistByCustomer(self):
       
        wishlist_item = Wishlist.objects.create(customer=self.user, product=self.product_1)
       
        response = self.client.get(reverse('wishlist:remove_from_wishlist', args=[self.product_1.id]))
       
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Wishlist.objects.count(), 0)  

    def testRemovingFromWishlistByGuest(self):
        self.client.logout()
       
        response = self.client.get(reverse('wishlist:remove_from_wishlist', args=[self.product_1.id]))
       
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/wishlist/remove/1/')  
