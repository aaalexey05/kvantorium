from .base import *

DEBUG = False

USE_HTTPS = os.getenv("DJANGO_USE_HTTPS", "False") == "True"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'kvantorium.example.com').split(',')
