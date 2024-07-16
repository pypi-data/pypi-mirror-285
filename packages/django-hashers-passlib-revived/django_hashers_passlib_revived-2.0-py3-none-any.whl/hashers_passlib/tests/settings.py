SECRET_KEY = "django-insecure"  # noqa: S105 Possible hardcoded password
DEBUG = False
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "hashers_passlib",
]
ROOT_URLCONF = None
AUTH_PASSWORD_VALIDATORS = []
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
USE_TZ = False
USE_I18N = False
