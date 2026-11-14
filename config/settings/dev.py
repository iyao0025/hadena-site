from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

# En dev local, cookies non-sécurisés HTTPS
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
