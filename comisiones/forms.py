import re

from django import forms


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
