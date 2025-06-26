"""Módulo sencillo para recopilar métricas de procesamiento."""

from __future__ import annotations

import time
from typing import Dict


class MetricasProcessor:
    """Calcula estadísticas básicas de las imágenes procesadas."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.contador = 0
        self.errores = 0
        self.tiempo_total = 0.0
        self.inicio = time.time()

    def actualizar(self, duracion: float, _memoria: float) -> None:  # noqa: D401
        """Actualiza el conteo y el tiempo acumulado."""
        self.contador += 1
        self.tiempo_total += duracion

    def registrar_error(self) -> None:
        self.errores += 1

    def get_tiempo_transcurrido(self) -> str:
        segundos = time.time() - self.inicio
        return f"{segundos:.1f}s"

    def get_velocidad(self) -> float:
        if self.tiempo_total == 0:
            return 0.0
        return (self.contador / self.tiempo_total) * 60

    def get_resumen(self) -> Dict[str, float | int]:
        return {
            "procesadas": self.contador,
            "errores": self.errores,
            "tiempo_segundos": round(self.tiempo_total, 2),
        }
