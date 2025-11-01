"""
Django settings for alx_travel_app project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'django_filters',
    'corsheaders',
    
    # Local apps
    'listings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'alx_travel_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'alx_travel_app.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Chapa Payment Gateway Configuration
CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')
CHAPA_PUBLIC_KEY = os.getenv('CHAPA_PUBLIC_KEY')
CHAPA_BASE_URL = os.getenv('CHAPA_BASE_URL', 'https://api.chapa.co/v1')

# Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# ============================================
# CELERY CONFIGURATION
# ============================================

# Celery Broker Settings (RabbitMQ)
CELERY_BROKER_URL = os.getenv(
    'CELERY_BROKER_URL', 
    'amqp://guest:guest@localhost:5672//'  # Default RabbitMQ connection
)

# Celery Result Backend (optional - stores task results)
# You can use RabbitMQ or Redis for this
CELERY_RESULT_BACKEND = os.getenv(
    'CELERY_RESULT_BACKEND',
    'rpc://'  # Using RabbitMQ RPC backend
)

# Celery accepts content types
CELERY_ACCEPT_CONTENT = ['json']

# Task serialization format
CELERY_TASK_SERIALIZER = 'json'

# Result serialization format
CELERY_RESULT_SERIALIZER = 'json'

# Timezone for Celery (should match Django timezone)
CELERY_TIMEZONE = TIME_ZONE  # Uses your Django TIME_ZONE setting

# Enable UTC
CELERY_ENABLE_UTC = True

# Task result expires after 1 hour (optional)
CELERY_RESULT_EXPIRES = 3600

# Task tracking (track if task has been started)
CELERY_TASK_TRACK_STARTED = True

# Task time limit (10 minutes)
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Task soft time limit (gives task time to clean up)
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# Maximum retries for failed tasks
CELERY_TASK_MAX_RETRIES = 3

# Retry delay (seconds)
CELERY_TASK_DEFAULT_RETRY_DELAY = 60

# Ignore result for tasks that don't need it (saves memory)
CELERY_TASK_IGNORE_RESULT = False

# Log level
CELERY_WORKER_LOG_LEVEL = 'INFO'

# Concurrency (number of worker processes)
# Default is number of CPU cores
CELERY_WORKER_CONCURRENCY = 4

# Prefetch multiplier (how many tasks each worker prefetches)
CELERY_WORKER_PREFETCH_MULTIPLIER = 4

# ============================================
# EMAIL CONFIGURATION (for sending emails)
# ============================================

# Email backend
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'  # Use SMTP
)

# For development, you can use console backend to see emails in terminal
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SMTP Configuration (Gmail example)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@travelapp.com')

# Email timeout
EMAIL_TIMEOUT = 10

# ============================================
# CELERY BEAT SCHEDULE (Optional - for periodic tasks)
# ============================================
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Example: Cleanup old bookings every day at 2 AM
    'cleanup-old-bookings': {
        'task': 'listings.tasks.cleanup_old_bookings',
        'schedule': crontab(hour=2, minute=0),
    },
}
