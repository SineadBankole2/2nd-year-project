from django.test import TestCase, Client
from django.urls import reverse
from .forms import StyleQuizForm

class StyleQuizViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('style_quiz') 

    def test_get_request_returns_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], StyleQuizForm)
        self.assertContains(response, '<form')  

    def test_post_streetwear_result(self):
        data = {
            'q1': 'a', 
            'q2': 'a',  
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result'], 'streetwear')

    def test_post_formal_result(self):
        data = {
            'q1': 'b', 
            'q2': 'b',  
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.context['result'], 'formal')

    def test_post_minimalist_result(self):
        data = {
            'q1': 'c', 
            'q2': 'c', 
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.context['result'], 'minimalist')

    def test_post_sporty_result(self):
        data = {
            'q1': 'd', 
            'q2': 'd',  
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.context['result'], 'sporty')

    def test_invalid_form_shows_errors(self):
        data = {
            'q1': '', 
            'q2': 'a',
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'This field is required.')
        self.assertIsNone(response.context['result'])
