from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'email', 'age', 'address')  

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'age', 'address', 'first_name', 'last_name', 'is_active')  

from django import forms

class SignInForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)