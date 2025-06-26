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
