from django.db import models
from django.conf import settings
from store.models import Product

class Wishlist(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, null=True, blank=True)  
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer.username} - {self.product.name} - {self.size}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'product'], name='unique_wishlist_item')
        ]
