import os
import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration


load_dotenv()


sentry_sdk.init(
    dsn='https://42119f5248414dadbece89d2bea8f81f@o1259295.ingest.sentry.io/6433834',
    integrations=[DjangoIntegration()],
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = 'oz(k-(++=@zc*ryh@0kws!)#-p)z2)c@g_$wk#0^_fkwm(z*r4'


DEBUG = False

CSRF_FAILURE_VIEW = 'core.views.permission_denied_view'

ALLOWED_HOSTS = [
    '0.0.0.0',
    '51.250.101.1',
    'firsttrymarki.ddns.net',
    'www.nizzerato.pythonanywhere.com',
    'nizzerato.pythonanywhere.com'
    'testserver',
    '127.0.0.1',
    'localhost',
    '[::1]',
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'posts',
    'users.apps.UsersConfig',
    'core',
    'about',
    'sorl.thumbnail',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'yatube.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.year.year',
            ],
        },
    },
]

WSGI_APPLICATION = 'yatube.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
	'USER': os.getenv('POSTGRES_USER'),
	'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
	'HOST': os.getenv('DB_HOST'),
	'PORT': os.getenv('DB_PORT')
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


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'posts:main_page'
# LOGOUT_REDIRECT_URL = 'posts:main_page'


EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


POSTS = 10
PROFILE_POSTS = 5
