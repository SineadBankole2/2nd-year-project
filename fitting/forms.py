# fitting/forms.py
from django import forms
from .models import SizeProfile

class SizeProfileForm(forms.ModelForm):
    class Meta:
        model = SizeProfile
        fields = [
            'age', 'address',
            'height_cm', 'weight_kg',
            'chest_cm', 'waist_cm', 'shoe_size',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'chest_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'waist_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'shoe_size': forms.TextInput(attrs={'class': 'form-control'}),
        }
