from django import forms
from .models import Product, ProductVariant


class Productform(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_decription', 'product_category', 'price', 'offer_price', 'thumbnail', 'is_active']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'product_decription': forms.Textarea(attrs={'class': 'form-control','rows':5}),
            'product_category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'offer_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        if len(product_name) < 5:
            raise forms.ValidationError("Product name must be at least 5 characters long.")
        
        if not product_name.replace(' ', '').isalnum():
            raise forms.ValidationError("Product name must only contain letters and numbers.")

        if product_name.lower() in ['product', 'item', 'goods']:
            raise forms.ValidationError("Product name cannot be too generic (e.g., 'Product', 'Item'). Please choose a unique name.")

        return product_name
    
    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            extension = thumbnail.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError("Thumbnail must be in a valid image format (jpg, jpeg, png, gif).")
        return thumbnail

    def clean(self):
        cleaned_data = super().clean()
        product_decription = cleaned_data.get('product_decription')
        
        if product_decription and len(product_decription) < 10:
            self.add_error('product_decription', "Product description must be at least 10 characters long.")
            
        # words = product_decription.split()
        # word_count = {word: words.count(word) for word in words}
        # for word, count in word_count.items():
        #     if count > 5:  # Avoid descriptions that repeat words excessively
        #         raise forms.ValidationError(f"The word '{word}' is repeated too often. Please write a more informative description.")

        
        return cleaned_data

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'variant_price', 'variant_stock', 'variant_status', 'discount_percentage']
        widgets = {
            'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Size'}),
            'variant_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'variant_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Discount Percentage'}),
            'variant_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean_size(self):
        size = self.cleaned_data.get('size')
        if size and len(size) > 10:
            raise forms.ValidationError("Size cannot be more than 10 characters.")
        # if size and not re.match("^[A-Za-z0-9]*$", size):
        #     raise forms.ValidationError("Size should contain only letters and numbers.")
        return size

    def clean_variant_price(self):
        variant_price = self.cleaned_data.get('variant_price')
        if variant_price <= 0:
            raise forms.ValidationError("Variant price must be a positive number.")
        if variant_price > 1000000:  # Adjust this limit as needed
            raise forms.ValidationError("Variant price cannot exceed 1,000,000.")
        return variant_price

    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage < 0 or discount_percentage > 100:
            raise forms.ValidationError("Discount percentage must be between 0 and 100.")
        return discount_percentage

    def clean_variant_stock(self):
        variant_stock = self.cleaned_data.get('variant_stock')
        if variant_stock < 0:
            raise forms.ValidationError("Variant stock cannot be negative.")
        return variant_stock

    def clean(self):
        cleaned_data = super().clean()
        size = cleaned_data.get('size')

        if size and self.product:
            existing_variant = ProductVariant.objects.filter(product=self.product, size=size).exclude(pk=self.instance.pk).first()
            if existing_variant:
                raise forms.ValidationError("A variant with this size already exists for this product.")

        return cleaned_data