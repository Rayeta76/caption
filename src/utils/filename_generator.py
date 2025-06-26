"""Generador básico de nombres de archivo."""

import re


class FilenameGenerator:
    """Genera nombres de archivo seguros a partir de la descripción."""

    def generar_nombre(self, descripcion: str, extension: str) -> str:
        base = descripcion.lower()
        base = re.sub(r"[^\w\s-]", "", base)
        base = re.sub(r"[-\s]+", "-", base).strip("-")
        base = base[:50] if base else "imagen"
        ext = extension if extension.startswith(".") else f".{extension}"
        return f"{base}{ext}"
