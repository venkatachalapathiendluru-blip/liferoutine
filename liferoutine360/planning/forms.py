from django import forms
from .models import MealItem


class MealItemForm(forms.ModelForm):
    class Meta:
        model = MealItem
        fields = ['meal_type', 'food', 'quantity', 'quantity_unit', 'calories', 'notes']
        widgets = {
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'food': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter food name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1'}),
            'quantity_unit': forms.Select(attrs={'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes'})
        }


class MealPlanForm(forms.Form):
    MEAL_PLAN_CHOICES = [
        ('tomorrow', 'Tomorrow'),
        ('next_7_days', 'Next 7 Days'),
        ('custom', 'Custom Range'),
    ]
    
    plan_type = forms.ChoiceField(
        choices=MEAL_PLAN_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='tomorrow'
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )