from django import forms
from .models import UserProfile,UserAddress
from account.models import User


class UserPofileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ['user','bio']


class UserAddressForm(forms.ModelForm):
    
    class Meta:
        model = UserAddress
        exclude = ['user']

    def clean_pin_number(self):
        pin_number = self.cleaned_data.get('pin_number')
        if len(str(pin_number)) != 6:
            raise forms.ValidationError("PIN number must be exactly 6 digits.")
        return pin_number

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) < 10 or len(phone_number) > 15:
            raise forms.ValidationError("Phone number must be between 10 and 15 digits.")
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        country = cleaned_data.get('country')

        if name and any(char.isdigit() for char in name):
            self.add_error('name', "Name should not contain numbers.")

        if country == "null":
            self.add_error('country', "Country must be specified.")

        return cleaned_data
       
class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','phone_number','email']
        widgets = {
            'email': forms.EmailInput(attrs = {'readonly':'readonly'}),
        }
        