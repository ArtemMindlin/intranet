from django.contrib.auth.backends import ModelBackend

from .models import Perfil


class DNIAutenticacionBackend(ModelBackend):
    """Autentica usuarios usando el DNI guardado en Perfil."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        dni = (username or "").strip()
        if not dni or password is None:
            return None

        perfil = Perfil.objects.select_related("user").filter(dni__iexact=dni).first()
        if not perfil:
            return None

        user = perfil.user
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
