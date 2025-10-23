import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# For development only; replace via environment variable in production.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-secret-key-change-me")

# Development settings
DEBUG = True
ALLOWED_HOSTS = ["*","127.0.0.1", "localhost", "testserver","172.20.190.181","172.20.10.3"]

## Celery settings (removed; using lightweight background threads instead)
# CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
# CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Installed apps: Django, DRF, simple history, and our complaints app
# NOTE: Do NOT put "ratelimit" here; it's not a Django app.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",          # Django REST framework
    "simple_history",          # Audit history
    # Local apps
    "complaints.apps.ComplaintsConfig",  # Our app with signals in ready()
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Attach request.user to history changes
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # We will add templates later (frontend), keep list empty for now
        "DIRS": [],
        "APP_DIRS": True,  # Looks for templates/ folders inside apps
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Custom role flags for templates (admin UI visibility)
                "complaints.context_processors.role_flags",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# SQLite for zero-cost local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation (simplified for easier testing)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", 
     "OPTIONS": {"min_length": 4}},  # Reduced from default 8
    # Other validators removed for easier testing
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (not used yet; frontend later)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

# Media files (uploads: images/audio/video)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email backend for development: prints emails to the console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@example.com"

# DRF minimal settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",  # login via /admin or session
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

# Simple History config: keep user on historical records
SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True

# Admin-access secret key for HOD/Principal gate. In production, set env var.
ADMIN_SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY", "adminisgoingtologin")
# Require HTTPS for admin-access login in production; keep disabled by default for tests/dev
ADMIN_ACCESS_REQUIRE_HTTPS = os.environ.get("ADMIN_ACCESS_REQUIRE_HTTPS", "false").lower() == "true"

# Redirect to home after logout
LOGOUT_REDIRECT_URL = "/"

# Redirect to home after login to avoid /accounts/profile/ 404s
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/auth/login/"

# Allow admin self-signup (HOD/Principal) in development. Disable in production by setting to "false".
ADMIN_SIGNUP_ENABLED = os.environ.get("ADMIN_SIGNUP_ENABLED", "true").lower() == "true"