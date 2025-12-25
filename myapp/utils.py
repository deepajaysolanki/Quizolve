# myapp/utils.py
import pyotp
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    # Generate a 6-digit random number
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300) # 300s = 5 minutes validity
    return totp.now()

def send_otp_email(email, otp):
    subject = 'Your Verification Code - Quizolve'
    message = f'Your One-Time Password (OTP) is: {otp}\n\nThis code is valid for 5 minutes. Do not share it with anyone.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(subject, message, email_from, recipient_list)