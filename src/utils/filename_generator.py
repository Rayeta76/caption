"""Generador básico de nombres de archivo."""

import re
from pathlib import Path


class FilenameGenerator:
    """Crea nombres seguros basados en una descripción."""

    def generar_nombre(self, descripcion: str, extension: str) -> str:
        base = descripcion.split(".")[0].lower()
        base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
        if not base:
            base = "imagen"
        ext = extension if extension.startswith(".") else f".{extension}"
        return f"{base}{ext}"
=======
import re

class FilenameGenerator:
    """Genera nombres de archivo seguros a partir de la descripción."""
    def generar_nombre(self, descripcion: str, extension: str) -> str:
        base = descripcion.lower()
        base = re.sub(r'[^\w\s-]', '', base)
        base = re.sub(r'[-\s]+', '-', base).strip('-')
        base = base[:50] if base else 'imagen'
        return f"{base}{extension}"
