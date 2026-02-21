from pathlib import Path
from decouple import config, Csv
import dj_database_url
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-locally-only')

# Checks if we are on Render. If yes, Debug=False. If no, Debug=True.
DEBUG = True

# DEBUG = not config('RENDER', default=False, cast=bool)
# Allow all hosts for now to prevent 400 Bad Request errors
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # for signup with google functionality
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # my app
    'myapp',

    # for sending emails (OTPs)
    'anymail',
]

AUTH_USER_MODEL = 'myapp.AppUsers'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        # 'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


DATABASES = {
    'default': {}
}

# INTELLIGENT DATABASE SWITCH
if config('RENDER', default=False, cast=bool):
    # YES -> Use PostgreSQL (Render automatically provides DATABASE_URL)
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

    # # FIX SSL LOOP (Crucial for "Infinite Loading")
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # SECURE_SSL_REDIRECT = True
    
    # Enable Compressed Static Files (Crucial for CSS)
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

    # We TRUST Render to handle the HTTPS. We do NOT ask Django to redirect.
    SECURE_SSL_REDIRECT = False            
    SESSION_COOKIE_SECURE = True            
    CSRF_COOKIE_SECURE = True               
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

else:
    # NO -> Use MySQL (Your local setup)
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    # BASE_DIR / "static",
    os.path.join(BASE_DIR, 'static'),
]

# This is for production (but good to have)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Signup with google functionality
SOCIALACCOUNT_ADAPTER = 'myapp.adapters.MySocialAccountAdapter'
SOCIALACCOUNT_EMAIL_VERIFICATION = "none" # Trust emails from Google (and other social logins) automatically
ACCOUNT_EMAIL_VERIFICATION = "none" # Skip verification for normal signups:
SOCIALACCOUNT_AUTO_SIGNUP = True # Ensure the user is logged in immediately after signing up via Google
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_LOGIN_ON_GET = True
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SITE_ID = 1

# New setting to fix the admin error
ACCOUNT_USER_DISPLAY = lambda user: user.email

# Settings for custom user model (no username)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
# This setting removes the warnings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Setting to skip the intermediate "Continue" page
SOCIALACCOUNT_LOGIN_ON_GET = True

# custom adapter
SOCIALACCOUNT_ADAPTER = 'myapp.adapters.MySocialAccountAdapter'

# This new block fixes the deprecation warnings in your terminal
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account',
        }
    }
}

# allauth specific settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# API key for AI models
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Email settings for sending OTPs in user email 
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
ANYMAIL = {
    "RESEND_API_KEY": os.environ.get("RESEND_API_KEY"),
}

# Resend uses this default address for testing without a custom domain
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"

                                                                                                                                                            