from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    is_organization = forms.BooleanField(
        required=False,
        label="Is this an organization?",
        initial=False
    )
    name = forms.CharField(
        max_length=100,
        label="Organization/Person Name"
    )
    address = forms.CharField(
        widget=forms.Textarea,
        label="Address"
    )
    phone_number = forms.CharField(
        max_length=20,
        label="Phone Number"
    )
    
    class Meta:
        model = Profile
        fields = ['is_organization', 'name', 'address', 'phone_number']