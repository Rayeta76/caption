import time

class MetricasProcessor:
    """Calcula tiempos y estadísticas básicas."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.inicio = time.time()
        self.errores = 0
        self.tiempos = []

    def actualizar(self, tiempo_procesamiento: float, _objetos: int):
        self.tiempos.append(tiempo_procesamiento)

    def registrar_error(self):
        self.errores += 1

    def get_tiempo_transcurrido(self) -> str:
        return f"{time.time() - self.inicio:.1f}s"

    def get_velocidad(self) -> float:
        if not self.tiempos:
            return 0.0
        promedio = sum(self.tiempos) / len(self.tiempos)
        return 60.0 / promedio if promedio else 0.0

    def get_resumen(self) -> dict:
        return {
            "imagenes": len(self.tiempos),
            "errores": self.errores,
            "tiempo": self.get_tiempo_transcurrido(),
        }
