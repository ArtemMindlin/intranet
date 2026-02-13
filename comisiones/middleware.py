from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone


class SessionIdleTimeoutMiddleware:
    """Cierra sesion si el usuario autenticado supera el tiempo de inactividad."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timeout_seconds = int(getattr(settings, "SESSION_IDLE_TIMEOUT_SECONDS", 0))
        if timeout_seconds > 0 and request.user.is_authenticated:
            now_ts = int(timezone.now().timestamp())
            last_activity_ts = request.session.get("last_activity_ts")

            # Evita aplicar timeout en rutas de autenticacion y recursos estaticos.
            path = request.path or ""
            is_exempt = (
                path.startswith("/accounts/login/")
                or path.startswith("/accounts/logout/")
                or path.startswith("/static/")
                or path.startswith("/media/")
            )

            if not is_exempt and last_activity_ts is not None:
                if now_ts - int(last_activity_ts) > timeout_seconds:
                    logout(request)
                    return redirect(f"{settings.LOGIN_URL}?session_expired=1")

            request.session["last_activity_ts"] = now_ts

        return self.get_response(request)
