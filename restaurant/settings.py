"""
Django settings for restaurant project.

Generated by 'django-admin startproject' using Django 3.0.14.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os


STRIPE_TEST_PUBLISHABLE_KEY = 'pk_test_51MYo3QGJo8Lf1SxiSIFyrT6a8Zj0tQ3jxqI3AtFn36iWezcdblvgsKlpj8ZFkf1Wtt4HVaHTleH6pmh2jizeVzC900mueFpgHM'
STRIPE_TEST_SECRET_KEY = 'sk_test_51MYo3QGJo8Lf1Sxi290GN4siI5kxgo1TXe8fTApoksRuzuAh3RlS4UVmNTYdd98iIHSPJHjVkqlkHxixUJary3ZB00RV62uCEF'
STRIPE_ENDPOINT_SECRET= "whsec_a396f60474b5a70f1b2d0c6fb6d41dd00c1591aa0f203a4880b5e0b6df95b236"

DEFAULT_AUTO_FIELD='django.db.models.AutoField'
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f5m=-b(%$72mt)g*g&43ksdcfjff0%y)!@x@nbrjo16nn!@h+e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]






# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'my_restaurant',
    'django.contrib.humanize',
    'crispy_forms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    
    'allauth.socialaccount.providers.google',
    
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'


SOCIALACCOUNT_ADAPTER = 'my_restaurant.My_adapter.MySocialAccountAdapter'

GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {'approval_prompt': 'force'}
ACCOUNT_SESSION_REMEMBER = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 3600
SOCIALACCOUNT_STORE_TOKENS = False
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET= True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_EMAIL_REQUIRED = True
STATELESS: False
ACCOUNT_EMAIL_VERIFICATION = 'optional'



AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend'
    
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'restaurant.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
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

WSGI_APPLICATION = 'restaurant.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'hu-hu'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'g.laszlo2003@gmail.com'
EMAIL_HOST_PASSWORD = 'jmjazbhagbpnpbpg'
EMAIL_DEBUG = True
