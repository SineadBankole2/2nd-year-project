from django.urls import path
from . import views

app_name = 'loyalty'  

urlpatterns = [
    path('', views.view_loyalty, name='view_loyalty'),
]
