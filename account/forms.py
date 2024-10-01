from collections.abc import Iterator
from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        if len(username) < 4:
            raise ValidationError("Username must be at least 4 characters long")
        if not re.match(r'^(?!_+$)[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, underscores and cannot consist solely of underscores.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Invalid email format")
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise ValidationError("Invalid phone number format")
        return phone_number


    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one digit.")
        return password
        

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match")

        return cleaned_data

class OTPForm(forms.Form):
        otp = forms.CharField (max_length=6, required=True,widget=forms.TextInput(
            attrs={'class':'form-control','placeholder':'Enter OTP'})
                              )
        
class loginform(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

User=get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring focus:ring-purple-500 focus:ring-opacity-50','placeholder':'Enter your email'}),
        max_length=254,
        label="Email"
    )
    def get_users(self, email):
        active_users=User.objects.filter(email__iexact=email,is_active=True)
        return (u for u in active_users if u.has_usable_password())