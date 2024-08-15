from django import forms
from .models import Category


class Categoryforms(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','is_listed','category_image']
        widgets ={
            'name' : forms.TextInput(attrs={'class' : 'form-control'}),
            'category_image' : forms.ClearableFileInput(attrs={'class':'form-control'}),
            'is_listed' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
           
        }