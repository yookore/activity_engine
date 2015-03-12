"""
Django settings for activity_engine project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2lvv_7&_ywy!((-m4gvmp+rod@y_40s=gdl(g#m%))p6p47pd1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cqlengine',
    'corsheaders',
    'stream_framework',
    'feed_engine',
    'django_extensions',
    'rest_framework',
    'rest_framework_swagger',
    'users',

)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'activity_engine.urls'

WSGI_APPLICATION = 'activity_engine.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'activity_engine',
        'HOST': '127.0.0.1',
        'USER': 'root',
        'PASSWORD': 'wordpass15'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/var/www/activity_engine/static/"

# Custom configuration applied by Jome
#AUTH_USER_MODEL = 'feed_engine.models.User'

AUTHENTICATION_BACKENDS = (
    'feed_engine.auth.YookoreBackend'
)

STREAM_DEFAULT_KEYSPACE = "yookore"

STREAM_ACTIVITY_TABLE = "activities"

STREAM_CASSANDRA_HOSTS = ['192.168.10.200', '192.168.10.201', '192.168.10.202']
#STREAM_CASSANDRA_HOSTS = ['127.0.0.1']

#CELERY_ACCEPT_CONTENT = ['application/json', 'application/x-python-serialize']
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

BROKER_URL = 'amqp://guest:Wordpass15@192.168.2.229:5672//'

BASE_URL = "http://localhost:8000/"

CONTENT_URL = "http://192.168.10.123:8000/api/"


SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.1',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    'is_authenticated': False,
    'is_superuser': False,
    'permission_denied_handler': None,
    'info': {
        'contact': 'yookore@gmail.com',
        'description': 'This is the POC Activity Engine Server for Yookore. ',
        'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html',
        'title': 'Yookore Activity Engine',
    },
    'doc_expansion': 'none',
}

APPEND_SLASH = False

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CORS_REPLACE_HTTPS_REFERER = False

CORS_ORIGIN_WHITELIST = (
    # '192.168.2.12:9000',
    # '192.168.2.12',
    # 'localhost:9000',
    # 'hostname.example.com'
)
CORS_ALLOW_METHODS = (
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS'
)



CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'authorization',
        'x-csrftoken'
    )
CORS_PREFLIGHT_MAX_AGE = 86400 # 24 hours