from django import forms
from .models import PassportOfficer

class PassportOfficerForm(forms.ModelForm):
    class Meta:
        model = PassportOfficer
        fields = ['UserNaMe', 'PassWoRd', 'email', 'name', 'employee_id', 'phone_number', 'branch_location', 'assigned_region', 'date_of_joining', 'status']
        widgets = {
            'PassWoRd': forms.PasswordInput(),  # Hide password input
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),  # Add date picker
        }

class AdminLoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField()
