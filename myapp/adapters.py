
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.shortcuts import redirect
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):

        # If the user is already logged in, let Allauth handle it.
        if request.user.is_authenticated:
            return
        
        # If this Google account is already linked, let Allauth log them in.
        if sociallogin.is_existing:
            return

        # Check if a user with this email ALREADY exists in the database
        email = sociallogin.user.email

        if email:
            try:
                # Find the existing user by email
                existing_user = User.objects.get(email=email)
                
                # --- THE MAGIC FIX ---
                # Connect this new Google account to the existing user automatically
                sociallogin.connect(request, existing_user)
                
            except User.DoesNotExist:
                # If user doesn't exist, let Allauth create a new one (Auto Signup)
                pass