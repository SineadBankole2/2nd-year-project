from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Order

class OrderHistoryViewTest(TestCase):
    
    def setUp(self):
        
        self.user = User.objects.create_user(username='testuser', password='password', email='test@example.com')
        
        
        Order.objects.create(emailAddress=self.user.email, item_name="Item 1", quantity=2)
        Order.objects.create(emailAddress=self.user.email, item_name="Item 2", quantity=1)
        Order.objects.create(emailAddress=self.user2.email, item_name="Item 3", quantity=3)
        
    
    def test_order_history_authenticated(self):
    
        self.client.login(username='testuser', password='password')
        
        response = self.client.get(reverse('order_history'))  
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(len(response.context['orders']), 2)  
        
        self.assertTrue(all(order.emailAddress == self.user.email for order in response.context['orders']))

    
    def test_order_history_not_authenticated(self):
        
        response = self.client.get(reverse('order_history'))  
        
        self.assertRedirects(response, '/login/?next=/order-history/')  
