from django import forms
from .models import Category
from django.core.exceptions import ValidationError


class Categoryforms(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','is_listed','category_image']
        widgets ={
            'name' : forms.TextInput(attrs={'class' : 'form-control'}),
            'category_image' : forms.ClearableFileInput(attrs={'class':'form-control'}),
            'is_listed' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        
        # Check if the category name is at least 3 characters long
        if len(category_name) < 3:
            raise ValidationError("Category name must be at least 3 characters long.")
        
        # Check if the category name contains only alphanumeric characters and spaces
        if not category_name.replace(' ', '').isalnum():
            raise ValidationError("Category name can only contain letters, numbers, and spaces.")
        
        # Check if the category name already exists (case-insensitive)
        if Category.objects.filter(category_name__iexact=category_name).exists():
            raise ValidationError("A category with this name already exists.")
        
        return category_name

    def clean_category_image(self):
        category_image = self.cleaned_data.get('category_image')
        if category_image:
        # Ensure category_image is a file-like object
            if hasattr(category_image, 'content_type'):
                # Check if the file is an image
                if not category_image.content_type.startswith('image'):
                    raise ValidationError("Uploaded file must be an image.")
                
                # Check if the image size is less than 2MB
                if category_image.size > 2 * 1024 * 1024:
                    raise ValidationError("Image file size must be less than 2MB.")
            
        
        return category_image
        

    def clean(self):
        cleaned_data = super().clean()
        category_name = cleaned_data.get('category_name')
        is_listed = cleaned_data.get('is_listed')
        
        if category_name and is_listed:
            # Example of cross-field validation
            if category_name.lower() == 'uncategorized' and is_listed:
                raise ValidationError("The 'Uncategorized' category cannot be listed.")
        
        return cleaned_data
