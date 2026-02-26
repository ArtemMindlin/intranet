from .base import *

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Email SMTP para incidencias (solo entorno local)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.grupomarcos.com"
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = "noresponder@grupomarcos.com"

INCIDENCIAS_EMAIL_TO = "artem.mindlin@marcosautomocion.com"
