import os
from pathlib import Path

import environ

# --------------------------------------------------------------------------------------
# Paths
# settings.py est dans backend/config/settings.py
# parents[0] = backend/config, parents[1] = backend, parents[2] = RACINE DU REPO
# --------------------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # <-- racine du repo (là où est .env)
PROJECT_DIR = Path(__file__).resolve().parents[1]  # backend/
BASE_DIR = PROJECT_DIR  # compat Django (si tu l'utilises ailleurs)

# --------------------------------------------------------------------------------------
# Env loading (django-environ)
# --------------------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)

# Charge .env à la racine du repo (fallback: ne crashe pas s'il n'existe pas)
env_file = REPO_ROOT / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# --------------------------------------------------------------------------------------
# Core settings
# --------------------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY")  # lève si manquant (voulu)
DEBUG = env("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# --------------------------------------------------------------------------------------
# Field-level encryption (RGPD compliance - SPECIFICATIONS_RGPD.md Section 3.1.1)
# --------------------------------------------------------------------------------------
# 32-byte Fernet key for encrypting sensitive personal data:
# - Client: email, phone, vat_number
# - Account: legal_id (SIRET)
# Generate new key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Security: Rotate annually, backup to AWS Secrets Manager in production
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY")

# --------------------------------------------------------------------------------------
# RGPD Retention Policy (SPECIFICATIONS_RGPD.md Section 3.4)
# --------------------------------------------------------------------------------------
# Automated data purge to comply with GDPR Article 5(1)(e) storage limitation
# - AuditLog: 13 months (395 days) - CNIL recommendation
# - Soft-deleted Accounts/Clients: 10 years - French accounting law (CGI Art. L.102 B)
# Runs weekly via CRON (Sunday 3am) in production
# Default: DISABLED (must be explicitly enabled in production)
RETENTION_POLICY_ENABLED = env.bool("RETENTION_POLICY_ENABLED", default=False)
RETENTION_AUDIT_LOGS_DAYS = env.int("RETENTION_AUDIT_LOGS_DAYS", default=395)  # 13 months
RETENTION_ACCOUNTING_YEARS = env.int("RETENTION_ACCOUNTING_YEARS", default=10)

USE_X_FORWARDED_HOST = True

# --------------------------------------------------------------------------------------
# Security settings (Production)
# --------------------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
    SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
    CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "SAMEORIGIN"

# --------------------------------------------------------------------------------------
# Email settings
# --------------------------------------------------------------------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="sandbox.smtp.mailtrap.io")
EMAIL_PORT = env.int("EMAIL_PORT", default=2525)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="54e99456c8cc20")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="04ef95b11a8fce")
EMAIL_FROM = env("EMAIL_FROM", default="noreply@example.com")
RESET_PASSWORD_URL = env("RESET_PASSWORD_URL", default="http://localhost:3000/reset-password")

# --------------------------------------------------------------------------------------
# Database
# - Priorité à DATABASE_URL
# - Sinon, variables séparées
# - En dernier recours, SQLite pour dev
# --------------------------------------------------------------------------------------
DATABASE_URL = env("DATABASE_URL", default=None)

if DATABASE_URL:
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    db_name = env("DATABASE_NAME", default=None)
    if db_name:
        DATABASES = {
            "default": {
                "ENGINE": env("DATABASE_ENGINE", default="django.db.backends.postgresql"),
                "NAME": db_name,
                "USER": env("DATABASE_USER", default=""),
                "PASSWORD": env("DATABASE_PASSWORD", default=""),
                "HOST": env("DATABASE_HOST", default="localhost"),
                "PORT": env("DATABASE_PORT", default="5432"),
                "CONN_MAX_AGE": 600,
            }
        }
    else:
        # Dernier recours (dev local sans config) : SQLite
        print("⚠️ Aucune config DB trouvée — fallback SQLite (dev only).")
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": REPO_ROOT / "db.sqlite3",
            }
        }

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
    "apps.branding.apps.BrandingConfig",
    "apps.email.apps.EmailConfig",
    "apps.legal_terms.apps.LegalTermsConfig",
    "django_extensions",
]

MIDDLEWARE = [
    # CORS doit être en premier
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.user.interface.middleware.AccountContextMiddleware",  # Phase 4
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.request_logging.RequestLoggingMiddleware",
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
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]


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
        # Connection pooling settings
        "CONN_MAX_AGE": env.int("CONN_MAX_AGE", default=600),  # 10 minutes
        "CONN_HEALTH_CHECKS": True,  # Check connections before use
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",  # 30s query timeout
        },
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
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "EXCEPTION_HANDLER": "config.api_errors.custom_exception_handler",
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
        "audit-logs": "100/hour",
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

# --------------------------------------------------------------------------------------
# Account Feature Flags (Phase 4)
# --------------------------------------------------------------------------------------
ENABLE_ACCOUNT_MODEL = env.bool("ENABLE_ACCOUNT_MODEL", default=False)

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
    "x-account-id",  # Phase 4: Account context header
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

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

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

# --------------------------------------------------------------------------------------
# Sentry (Error Tracking)
# --------------------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default=None)
if SENTRY_DSN and SENTRY_DSN.startswith("http"):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=env("SENTRY_ENVIRONMENT", default="production"),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
        integrations=[DjangoIntegration()],
        send_default_pii=False,
    )
