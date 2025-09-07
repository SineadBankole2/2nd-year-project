"""
URL configuration for clothingstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),  
    path('store/', include('store.urls')), 
    path('search/', include('search.urls')), 
    path('accounts/',include('cos_accounts.urls')),
    path('reviews/', include('reviews.urls')),
    path('', include('pages.urls')),
    path('search/', include('search.urls')),
    path('wishlist/', include('wishlist.urls', namespace='wishlist')),
    path('cart/', include('cart.urls')),
    path('loyalty/', include('loyalty.urls', namespace='loyalty')),
    path('questions/', include('questions.urls', namespace='questions')),  
    path('order/', include('order.urls')),
    path('stylequiz/', include('stylequiz.urls', namespace='stylequiz')),
    path('vouchers/', include('vouchers.urls')),
    


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
