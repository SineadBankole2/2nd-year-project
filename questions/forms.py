from django import forms
from .models import Question

class form_for_question(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class form_for_answer(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['answer']
