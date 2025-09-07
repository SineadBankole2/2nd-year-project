from django.urls import path
from .views import style_quiz

app_name = 'stylequiz'

urlpatterns = [
    path('', style_quiz, name='quiz'),
]
