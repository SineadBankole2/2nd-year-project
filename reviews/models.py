from django.conf import settings
from django.db import models
from store.models import Product

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    review_text = models.TextField()
    rating = models.PositiveIntegerField(null=True)
    helpful_count = models.PositiveIntegerField(default=0)
    # ✅ new: mark reviews that come from real purchases
    verified_purchase = models.BooleanField(default=False)

    class Meta:
        # ✅ new: one review per user per product
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='one_review_per_user_per_product'),
        ]

    def __str__(self):
        return f"Review by {self.user.username if self.user else 'Anonymous'} - Rating: {self.rating}"
