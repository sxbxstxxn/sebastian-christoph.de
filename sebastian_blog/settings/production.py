from .base import *
DEBUG = env_bool("DEBUG", False)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
