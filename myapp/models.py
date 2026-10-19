from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from datetime import date
from django.utils import timezone

class AppUsersManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class AppUsers(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, verbose_name='password')
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        default='profile_photos/default.png',
        blank=True,
        null=True
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    subscription_expiry = models.DateField(null=True, blank=True)
    
    objects = AppUsersManager()

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []  # Fields needed when creating a superuser

    class Meta:
        verbose_name = 'App User'
        verbose_name_plural = 'App Users'

    def __str__(self):
        return self.email
    
class RegularUser(AppUsers):
    class Meta:
        proxy = True
        verbose_name = 'Regular User'
        verbose_name_plural = 'Regular Users'

# Model to track quiz attempts
class UserQuizAttempt(models.Model):
    QUIZ_TYPE_CHOICES = [
        ('category', 'Category'),
        ('exam', 'Exam'),
        ('custom', 'Custom Topic'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz_type = models.CharField(max_length=10, choices=QUIZ_TYPE_CHOICES)
    quiz_identifier = models.CharField(max_length=100) # e.g., 'History', 'UPSC', or '__custom__'
    created_at = models.DateTimeField(default=timezone.now)

    # Score out of 50
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.user.email} - {self.quiz_identifier} ({self.score}/{self.total_questions})"
    
    
# Model to store individual question answers for a quiz attempt
class AnsweredQuestion(models.Model):
    attempt = models.ForeignKey(UserQuizAttempt, related_name='answers', on_delete=models.CASCADE)
    question_text = models.TextField()
    user_answer = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=500)
    is_correct = models.BooleanField()

    def __str__(self):
        return self.question_text

# Model to handle contact messages from users
class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.full_name}"

# Model to handle payment requests for subscriptions
class PaymentRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=20)  # 'monthly' or 'yearly'
    amount = models.CharField(max_length=10)
    transaction_id = models.CharField(max_length=50, unique=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.transaction_id}"