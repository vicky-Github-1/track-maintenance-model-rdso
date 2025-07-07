from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser ,Task
from django.core.exceptions import ValidationError

class CustomRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('engineer', 'Engineer'),
    )
    ZONE_CHOICES = (
        ('North', 'North'),
        ('South', 'South'),
        ('East', 'East'),
        ('West', 'West'),
        ('Central', 'Central'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    zone = forms.ChoiceField(choices=ZONE_CHOICES, required=True)
    city = forms.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role','zone']
    
    
    def __init__(self, *args, **kwargs):
        super(CustomRegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# forms.py
from django import forms
from .models import CustomUser

class UserEditForm(forms.ModelForm):
    password1 = forms.CharField(required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role','zone','city']  # only editable fields

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }