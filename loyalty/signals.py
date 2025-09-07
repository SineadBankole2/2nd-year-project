from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Loyalty

@receiver(user_logged_in)
def create_loyalty_record_for_logged_in_user(sender, request, user, **kwargs):
    
    if not Loyalty.objects.filter(user=user).exists():
        
        Loyalty.objects.create(user=user)
        print(f"Loyalty record created for user {user.username}")
