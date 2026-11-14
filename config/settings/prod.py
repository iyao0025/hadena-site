from .base import *

DEBUG = False

# Vérification stricte de la clé secrète en prod
if SECRET_KEY == "insecure-hadena-default-dev-key":
    raise ValueError("DJANGO_SECRET_KEY doit obligatoirement être configurée en production !")

# Sécurité HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
