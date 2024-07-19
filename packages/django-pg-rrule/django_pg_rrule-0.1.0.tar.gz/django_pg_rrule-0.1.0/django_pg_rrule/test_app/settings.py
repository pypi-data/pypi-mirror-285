DEBUG = True
USE_TZ = True
DATABASES = {
    "default": {
        "NAME": "default",
        "ENGINE": "django.db.backends.sqlite3",
    }
}

INSTALLED_APPS = ["django_pg_rrule.test_app"]
