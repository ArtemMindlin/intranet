import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginPorDNIForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Por favor, introduce un DNI y contraseña correctos.",
    }

    username = forms.CharField(
        label="DNI",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "autocomplete": "username",
                "placeholder": "Introduce tu DNI",
            }
        ),
    )

    def clean_username(self):
        return (self.cleaned_data.get("username") or "").strip().upper()


class MiPerfilEditableForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        required=True,
        error_messages={"required": "El email es obligatorio."},
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
    )

    def clean_telefono(self):
        telefono = (self.cleaned_data.get("telefono") or "").strip()
        if telefono and not re.fullmatch(r"[0-9+\-\s()]{7,20}", telefono):
            raise forms.ValidationError("El teléfono no tiene un formato válido.")
        return telefono
