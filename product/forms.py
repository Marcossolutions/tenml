from django import forms
from .models import Product, ProductVariant


class Productform(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_decription', 'product_category', 'price', 'offer_price', 'thumbnail', 'is_active']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'product_decription': forms.Textarea(attrs={'class': 'form-control'}),
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
        return product_name
    
    # def clean_price(self):
    #     price = self.cleaned_data.get('price')
    #     if price <= 0:
    #         raise forms.ValidationError("Price must be a positive number.")
    #     return price
    
    # def clean_offer_price(self):
    #     price = self.cleaned_data.get('price')
    #     offer_price = self.cleaned_data.get('offer_price')
    #     if offer_price is not None and offer_price >= price:
    #         raise forms.ValidationError("Offer price must be less than the regular price.")
    #     return offer_price
    
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
        
        return cleaned_data

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'variant_price', 'variant_stock', 'variant_status', 'discount_percentage']
        widgets = {
            'variant_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_size(self):
        size = self.cleaned_data.get('size')
        if size and len(size) > 10:
            raise forms.ValidationError("Size cannot be more than 10 characters.")
        return size

    def clean_variant_price(self):
        variant_price = self.cleaned_data.get('variant_price')
        if variant_price <= 0:
            raise forms.ValidationError("Variant price must be a positive number.")
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
