from django.db import models
from django.conf import settings  
from store.models import Customer

class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, default=1)  
    text = models.TextField()
    answer = models.TextField(blank=True, null=True)  
    created = models.DateTimeField(auto_now_add=True)
    answered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)  
