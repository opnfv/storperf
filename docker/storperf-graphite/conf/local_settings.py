# flake8: noqa
# Edit this file to override the default graphite settings, do not edit settings.py

# Turn on debugging and restart apache if you ever see an "Internal Server Error" page
# DEBUG = True

# Set your local timezone (django will try to figure this out automatically)
TIME_ZONE = 'Europe/Zurich'

# Secret key for django
SECRET_KEY = '%%SECRET_KEY%%'

URL_PREFIX = "/graphite/"
