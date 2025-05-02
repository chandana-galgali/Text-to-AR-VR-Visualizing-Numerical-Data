from django import forms
from .models import ExtractedData
class TextInputForm(forms.ModelForm):
    class Meta:
        model = ExtractedData
        fields = ['input_text']
        widgets = {
            'input_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter your numerical data here...'
            }),
        }
        labels = {
            'input_text': 'Data Input',
        }