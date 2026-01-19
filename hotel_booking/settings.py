"""
Django settings for hotel_booking project.
"""
from pathlib import Path
import os
from decouple import config
import dj_database_url  # Render PostgreSQL auto detect සඳහා

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-please')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
       # ... කලින් ටික ...
    'rest_framework',


    # Third party
    'cloudinary_storage',
    'cloudinary',
    'multiselectfield',

    # Local
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hotel_booking.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_stats',
                
            ],
        },
    },
]

WSGI_APPLICATION = 'hotel_booking.wsgi.application'

# Database - Local SQLite, Render PostgreSQL auto detect
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Render එකේ DATABASE_URL එක තියෙනවා නම් PostgreSQL use කරනවා
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.parse(os.environ.get('DATABASE_URL'))

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Colombo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (uploaded images - Cloudinary)
MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Cloudinary config
CLOUDINARY_STORAGE = {
    #'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default='dmokxu46m'),
    #'API_KEY': config('CLOUDINARY_API_KEY', default='7764447697492844'),
    #'API_SECRET': config('CLOUDINARY_API_SECRET', default='hvaFnrPgXouI0QB6jrmpvF1DMrM'), 

    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
   'API_SECRET': config('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Twilio config (optional)
# Twilio for WhatsApp notifications
TWILIO_SID = 'ACb0297ddadc17bf00ce312f3f100b78ae'  # Twilio dashboard එකේ ගන්න
TWILIO_AUTH_TOKEN = 'd7148a2e1f1827fb3ba7fbb10995929f'  # Twilio dashboard එකේ ගන්න
TWILIO_PHONE_NUMBER = '+12512552335'  # Twilio WhatsApp sandbox number (or your number)
OWNER_PHONE = '+94740948966'  # Owner එකගේ WhatsApp number (E.164 format)

# Login redirect
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# Email backend (development එකේ console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'