from django.db import models
from django.conf import settings
from decimal import Decimal  

class Loyalty(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='loyalty_account'  
    )
    points = models.IntegerField(default=0)

    def convert_points_to_discount(self, requested_points, cart_total):
        """Calculate the discount based on requested points and the cart total."""

        
        requested_points = Decimal(requested_points)
        current_points = Decimal(self.points)
        cart_total = Decimal(cart_total)

       
        points_to_apply = min(requested_points, current_points, cart_total)

        
        cashback_points = int(points_to_apply * Decimal("0.1"))

        return points_to_apply, cashback_points

    def __str__(self):
        return f"Loyalty points for {self.user.username}"