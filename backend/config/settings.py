import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import environ
from rest_framework.permissions import AllowAny

print("DATABASE_URL repr:", repr(os.getenv("DATABASE_URL")))


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Load environment variables from .env file
env = environ.Env(
    DEBUG=(bool, False),
    DATABASE_URL=(str, None),
)
env_candidate = BASE_DIR / ".env"
loaded_env_file = None
if env_candidate.exists():
    loaded_env_file = env_candidate
    environ.Env.read_env(str(env_candidate))
    print(f"Loaded .env file from {env_candidate}")

# Debug logs pour vérifier ce qui est réellement chargé
print("DATABASE_URL repr:", repr(env("DATABASE_URL", default=None)))
print(
    "DBVARS:",
    repr(env("DATABASE_NAME", default=None)),
    repr(env("DATABASE_USER", default=None)),
    repr(env("DATABASE_PASSWORD", default=None)),
    repr(env("DATABASE_HOST", default=None)),
    repr(env("DATABASE_PORT", default=None)),
)

DEBUG = env("DEBUG", default=True)

# Si DATABASE_URL est défini (ex: postgres://user:pass@host:5432/dbname), on l'utilise.
if env("DATABASE_URL", default=None):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    # Sinon on lit les variables séparées ; si manquantes, fallback SQLite pour permettre makemigrations
    db_name = env("DATABASE_NAME", default=None)
    if db_name:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": db_name,
                "USER": env("DATABASE_USER"),
                "PASSWORD": env("DATABASE_PASSWORD"),
                "HOST": env("DATABASE_HOST", default="localhost"),
                "PORT": env("DATABASE_PORT", default="5432"),
            }
        }
    else:
        print("⚠️ Aucune config DB trouvée — fallback SQLite (dev only).")
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

from decouple import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

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
    "apps.core.apps.CoreConfig",
    "apps.catalog.apps.CatalogConfig",
    "apps.quote.apps.QuoteConfig",
    "apps.client.apps.ClientConfig",
]

MIDDLEWARE = [
    # CORS doit être en premier
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.request_logging.RequestLoggingMiddleware",
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
        "catalog": "60/min",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# Optionnel: personnalisation des headers JWT
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),  # donc "Authorization: Bearer <token>"
    "BLACKLIST_AFTER_ROTATION": True,  # pour blacklist les tokens après rotation
    "ROTATE_REFRESH_TOKENS": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "FreelanSign REST API",
    "DESCRIPTION": "API documentation for the FreelanSign REST application",
    "VERSION": "0.1.0",
    "TAGS": [
        {"name": "Auth", "description": "JWT Authentication & session endpoints"},
        {"name": "Users", "description": "User & profile management"},
        {"name": "Catalog", "description": "Areas & Prestations"},
    ],
    "SERVE_INCLUDE_SCHEMA": False,  # include schema endpoint into schema
    "COMPONENT_SPLIT_REQUEST": True,
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

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # garde les loggers Django
    "filters": {
        "context_filter": {
            "()": "apps.core.logging.ContextFilter",
        }
    },
    "formatters": {
        "detailed": {"format": "%(asctime)s %(levelname)s [%(name)s] [req=%(request_id)s user=%(user_id)s] %(message)s"},
        "standard": {"format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "filters": ["context_filter"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "detailed",
            "filters": ["context_filter"],
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        # loggers spécifiques si tu veux niveauter différemment
        # "apps.catalog": {"handlers": ["console","file"], "level": "DEBUG", "propagate": False},
    },
}
