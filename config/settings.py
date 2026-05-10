"""
Django settings for config project.
"""

from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-key")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,.onrender.com"
).split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",

    "apps.accounts",
    "apps.tenants",
    "apps.transactions",
    "apps.telecom",
    "apps.risk",
    "apps.fraud_cases",
    "apps.audit",
    "apps.ai_assistant",
    "apps.dashboard",
    "apps.cases",
    "apps.alerts",
    "apps.onboarding.apps.OnboardingConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

CORS_ALLOW_ALL_ORIGINS = True

CAMARA_MODE = os.getenv("CAMARA_MODE", "mock")

CAMARA_BASE_URL = os.getenv(
    "CAMARA_BASE_URL",
    "https://network-as-code.p-eu.rapidapi.com",
)

CAMARA_API_KEY = os.getenv("CAMARA_API_KEY", "")

CAMARA_HOST = os.getenv(
    "CAMARA_HOST",
    "network-as-code.p-eu.rapidapi.com",
)

CAMARA_TIMEOUT = int(os.getenv("CAMARA_TIMEOUT", "30"))

NUMBER_VERIFY_PATH = os.getenv(
    "NUMBER_VERIFY_PATH",
    "/passthrough/camara/v1/number-verification/number-verification/v0/verify",
)

SIM_SWAP_CHECK_PATH = os.getenv(
    "SIM_SWAP_CHECK_PATH",
    "/passthrough/camara/v1/sim-swap/sim-swap/v0/check",
)

DEVICE_SWAP_CHECK_PATH = os.getenv(
    "DEVICE_SWAP_CHECK_PATH",
    "/passthrough/camara/v1/device-swap/device-swap/v1/check",
)

LOCATION_VERIFY_PATH = os.getenv(
    "LOCATION_VERIFY_PATH",
    "/location-verification/v1/verify",
)

KYC_MATCH_PATH = os.getenv(
    "KYC_MATCH_PATH",
    "/passthrough/camara/v1/kyc-match/kyc-match/v0.3/match",
)

KYC_TENURE_PATH = os.getenv(
    "KYC_TENURE_PATH",
    "/passthrough/camara/v1/kyc-tenure/kyc-tenure/v0.1/check-tenure",
)

KYC_FILL_IN_PATH = os.getenv(
    "KYC_FILL_IN_PATH",
    "/passthrough/camara/v1/kyc-fill-in/kyc-fill-in/v0.4/fill-in",
)

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
