
from django import forms
from .models import AppUsers
from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholder text to make the fields more user-friendly
        self.fields['old_password'].widget.attrs.update({'placeholder': 'Enter your current password'})
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'Enter your new password'})
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Confirm your new password'})

        # Remove the default help text
        self.fields['new_password1'].help_text = ''
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = AppUsers
        # List the fields from model that user to be able to edit.
        fields = ['first_name', 'last_name', 'email', 'profile_photo']
        widgets = {
            'profile_photo': forms.FileInput(),
        }