"""Mejorador sencillo de captions."""

from .translator import Translator


class CaptionEnhancer:
    """Aplica mejoras simples a un caption."""

    def __init__(self, translator: Translator | None = None) -> None:
        self.translator = translator

    def mejorar_caption(self, caption: str) -> str:
        """Devuelve el caption mejorado (sin cambios reales)."""
        if self.translator:
            return self.translator.translate(caption)
        return caption.strip()
=======
class CaptionEnhancer:
    """Pequeño placeholder para mejorar captions."""
    def __init__(self, translator=None):
        self.translator = translator

    def mejorar_caption(self, texto: str) -> str:
        return texto.strip()
