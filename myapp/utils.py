# myapp/utils.py
import random
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = 'Your Verification Code - Quizolve'
    message = f'Your One-Time Password (OTP) is: {otp}\n\nThis code is valid for 5 minutes. Do not share it with anyone.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    try:
        send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False