from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your first name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your last name'
    }))
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['wake_up_time', 'sleep_time', 'plan', 'water_target_liters', 'food_preference']
        widgets = {
            'wake_up_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'sleep_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'water_target_liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.5', 'max': '5.0'}),
            'food_preference': forms.Select(attrs={'class': 'form-select'}),
        }