import os
from pathlib import Path

import environ
from rest_framework.permissions import AllowAny

print("DATABASE_URL repr:", repr(os.getenv("DATABASE_URL")))


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Load environment variables from .env file
env = environ.Env()
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, ".env"))
print(
    "DBVARS:",
    repr(env("DATABASE_NAME", default=None)),
    repr(env("DATABASE_USER", default=None)),
    repr(env("DATABASE_PASSWORD", default=None)),
    repr(env("DATABASE_HOST", default=None)),
    repr(env("DATABASE_PORT", default=None)),
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-jovyrahw%x-2w323nfg0$o@n+lz2ru5nca+f@#lyzwl5p3&+^%"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "apps.user.apps.UserConfig",
]

MIDDLEWARE = [
    # CORS doit être en premier
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "EXCEPTION_HANDLER": "config.exceptions.drf_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "200/min",
        "anon": "30/min",
        "auth": "10/min",  # Limite pour les endpoints d'authentification
    },
}

# Optionnel: personnalisation des headers JWT
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),  # donc "Authorization: Bearer <token>"
    "BLACKLIST_AFTER_ROTATION": True,  # pour blacklist les tokens après rotation
    "ROTATE_REFRESH_TOKENS": True
}

SPECTACULAR_SETTINGS = {
    "TITLE": "FreelanSign REST API",
    "DESCRIPTION": "API documentation for the FreelanSign REST application",
    "VERSION": "0.1.0",
    "TAGS": [
        {"name": "Auth", "description": "JWT Authentication & session endpoints"},
        {"name": "Users", "description": "User & profile management"},
    ],
}

# Models
AUTH_USER_MODEL = "user.User"

# CORS settings
import os

# En développement, on autorise les origines locales
if os.getenv("DEBUG", "False").lower() == "true":
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",  # Frontend local
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://0.0.0.0:3000",  # Docker internal
    ]

    # Pour le développement, on peut être plus permissif
    CORS_ALLOW_ALL_ORIGINS = True  # ⚠️ UNIQUEMENT en développement !

else:
    # En production, spécifier les domaines autorisés
    CORS_ALLOWED_ORIGINS = [
        "https://votre-frontend-prod.com",
        # Ajouter d'autres domaines autorisés
    ]

# Headers autorisés
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Méthodes HTTP autorisées
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Autoriser les cookies cross-origin si nécessaire
CORS_ALLOW_CREDENTIALS = True

# Préflight cache (optionnel)
CORS_PREFLIGHT_MAX_AGE = 86400

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
