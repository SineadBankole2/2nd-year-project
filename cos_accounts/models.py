from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)  

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='cos_accounts_user_set',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='cos_accounts_permission_user_set',  
        blank=True
    )
