from django.urls import path
from .views import search_results

urlpatterns = [
    path('results/', search_results, name='search'),
]
