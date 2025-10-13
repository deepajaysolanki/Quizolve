
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.shortcuts import redirect
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Get the process from the sociallogin state, which is passed from the button.
        process = sociallogin.state.get('process')
        email = sociallogin.user.email

        # This is the main logic
        if process == 'signup':
            # If the user's intent was to 'signup' and an email already exists...
            if EmailAddress.objects.filter(email__iexact=email).exists():
                # ...then block the signup and show an error.
                messages.error(request, f"A user with the email '{email}' already exists")
                raise ImmediateHttpResponse(redirect('registration')) # Redirect to your signup page

        # For all other cases (e.g., the process is 'login'),
        # allow the default allauth behavior to proceed, which will log the user in.
        return