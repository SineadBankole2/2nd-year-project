from django.urls import path, include
from store.views import mens_view, kids_view, womens_view  
from reviews.views import ReviewsView  
from . import views

urlpatterns = [
    path('store/men/',mens_view, name='mens'),
    path('', views.homepage, name='homepage'),  
    path('cos_accounts/', include('cos_accounts.urls')),
    path('reviews/', include('reviews.urls')),
    path('store/kids/', kids_view, name='kids'),
    path('store/women/', womens_view, name='womens'),
    path('loyalty/', include('loyalty.urls')), 
    path('fitting/', include('fitting.urls')),  



]


