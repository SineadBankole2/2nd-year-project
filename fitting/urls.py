from django.urls import path,include
from .views import profile_view

app_name = 'fitting'

urlpatterns = [
    path('profile/', profile_view, name='profile'),

]
