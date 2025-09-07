from django.db import models
from django.conf import settings

class SizeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    height_cm = models.PositiveIntegerField(blank=True, null=True)
    weight_kg = models.PositiveIntegerField(blank=True, null=True)
    chest_cm = models.PositiveIntegerField(blank=True, null=True)
    waist_cm = models.PositiveIntegerField(blank=True, null=True)
    shoe_size = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Size Profile"
