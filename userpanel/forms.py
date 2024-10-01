from typing import Any
from django import forms
from django.contrib.auth.base_user import AbstractBaseUser
from .models import UserProfile,UserAddress
from account.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re



class UserPofileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ['user','bio']


class UserAddressForm(forms.ModelForm):
    
    class Meta:
        model = UserAddress
        fields = ['name', 'house_name', 'street_name', 'pin_number', 'district', 'state', 'country', 'phone_number']

    def validate_field(self, field_value, field_name):
        """
        General validation method for fields to allow only alphanumeric characters,
        hyphens, and spaces, and checks if the field contains only spaces or consecutive spaces.
        """
        # Strip leading and trailing spaces
        field_value = field_value.strip()

        # Check if the field is empty after stripping
        if not field_value:
            raise forms.ValidationError(f"{field_name} cannot be empty or contain only spaces.")
        
        if len(field_value) < 3:
            raise forms.ValidationError(f"{field_name} must be at least 3 characters long.")
        
        # Check for consecutive spaces
        if "  " in field_value:
            raise forms.ValidationError(f"{field_name} cannot contain consecutive spaces.")

        # Validate allowed characters: letters, numbers, spaces, and hyphens
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', field_value):
            raise forms.ValidationError(f"{field_name} can only contain letters, numbers, spaces, and hyphens (-).")
        if not re.search(r'[A-Za-z]', field_value):
            raise forms.ValidationError(f"{field_name} must contain at least one letter.")

        return field_value

    def clean_name(self):
        name = self.cleaned_data.get('name')
        return self.validate_field(name, 'Name')

    def clean_house_name(self):
        house_name = self.cleaned_data.get('house_name')
        return self.validate_field(house_name, 'House Name')

    def clean_street_name(self):
        street_name = self.cleaned_data.get('street_name')
        return self.validate_field(street_name, 'Street Name')

    def clean_district(self):
        district = self.cleaned_data.get('district')
        return self.validate_field(district, 'District')

    def clean_state(self):
        state = self.cleaned_data.get('state')
        return self.validate_field(state, 'State')

    def clean_country(self):
        country = self.cleaned_data.get('country')
        return self.validate_field(country, 'Country')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        # Ensure phone number contains only digits
        if not re.match(r'^\d{10,15}$', phone_number):
            raise forms.ValidationError('Phone number must contain only digits and be between 10 and 15 characters long.')

        return phone_number

    def clean_pin_number(self):
        pin_number = self.cleaned_data.get('pin_number')

        # Ensure pin number is a valid integer
        if not re.match(r'^\d{6}$', str(pin_number)):
            raise forms.ValidationError('PIN number must be a valid 6-digit number.')

        return pin_number

class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','phone_number','email']
        widgets = {
            'email': forms.EmailInput(attrs = {'readonly':'readonly'}),
        }
    
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise ValidationError("Username must be at least 4 characters long")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise ValidationError("Invalid phone number format. Must be between 9 and 15 digits.")
        return phone_number    
        
User = get_user_model


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'})
            
            field.required = False  # Ensure the field is still marked as required
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
     
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
       
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
   
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        
       
        common_passwords = ['password', '123456', 'qwerty', 'admin']
        if password.lower() in common_passwords:
            raise ValidationError("This password is too common. Please choose a more unique password.")

        return password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")
        return password2