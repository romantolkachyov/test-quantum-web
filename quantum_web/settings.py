"""
Django settings for quantum_web project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-2(cv5ckqms8zm@%nd1316q213x%9k4qp5&1c08=502m5yt_$c1"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "quantum_web.webapp",
    "quantum_web.worker",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "quantum_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "quantum_web.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ASGI_APPLICATION = "quantum_web.asgi.application"

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 1

REDIS_LOCATION = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CACHES = {
    "default": {
        "BACKEND": "django_async_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_async_redis.client.DefaultClient",
            "REDIS_CLIENT_KWARGS": {
                "decode_responses": True,
            }
        }
    },
}

# queue with quantum jobs
JOB_QUEUE = os.getenv("JOB_QUEUE", "quantum_jobs")

# result queue key prefix
RESULT_QUEUE_PREFIX = os.getenv("RESULT_QUEUE_PREFIX", "quantum_result")

# result queue expire time
RESULT_QUEUE_EXPIRE = int(os.getenv("RESULT_QUEUE_EXPIRE", str(60 * 60)))

# number of tries when awaiting job stream
STREAM_WAIT_MAX_TRIES = int(os.getenv("STREAM_WAIT_MAX_TRIES", "60"))

# sleep interval between stream wait tries
STREAM_WAIT_SLEEP_INTERVAL = int(os.getenv("STREAM_WAIT_SLEEP_INTERVAL", "5"))

# maximum number of concurrent jobs running on a single worker instance
WORKER_MAX_CONCURRENCY = int(os.getenv("WORKER_MAX_CONCURRENCY", "2"))

QUANTUM_LOG_LEVEL = os.getenv("QUANTUM_LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{asctime} {levelname} {message}",
            "style": "{"
        },
    },
    "handlers": {
        "console": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.channels.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "quantum_web": {
            "handlers": ["console"],
            "level": QUANTUM_LOG_LEVEL,
            "propagate": False,
        },
        "quantum_web.webapp": {
            "handlers": ["console"],
            "level": QUANTUM_LOG_LEVEL,
            "propagate": False,
        },
    }
}
