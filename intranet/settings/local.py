from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Email SMTP para incidencias (solo entorno local)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.office365.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = "tu_correo@marcosautomocion.com"
EMAIL_HOST_PASSWORD = "tu_password_o_app_password"
DEFAULT_FROM_EMAIL = "tu_correo@marcosautomocion.com"

INCIDENCIAS_EMAIL_TO = "artem.mindlin@marcosautomocion.com"
