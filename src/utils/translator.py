"""Traductor mínimo para la aplicación GUI."""

class Translator:
    """Simula un traductor básico."""

    def __init__(self, language: str = "es") -> None:
        self.language = language

    def set_language(self, language: str) -> None:
        """Establece el idioma destino."""
        self.language = language

    def translate(self, text: str, dest_language: str | None = None) -> str:
        """Devuelve el texto sin cambios (placeholder)."""
        return text
