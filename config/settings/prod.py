from .base import *

DEBUG = False

# Vérification stricte de la clé secrète en prod
if SECRET_KEY == "insecure-hadena-default-dev-key":
    raise ValueError("DJANGO_SECRET_KEY doit obligatoirement être configurée en production !")

# Sécurité HTTPS
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
if env("DJANGO_SECURE_PROXY_SSL_HEADER", default=""):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
