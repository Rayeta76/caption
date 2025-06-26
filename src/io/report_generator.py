"""Generador de informes HTML simplificado."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping


class ReportGenerator:
    """Crea un informe HTML básico con estadísticas."""

    def generar_informe_html(
        self,
        resultados: Iterable[Mapping],
        carpeta_salida: str | Path,
        resumen: Mapping | None = None,
    ) -> Path:
        carpeta = Path(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)
        archivo = carpeta / "informe.html"

        total = len(list(resultados))
        errores = resumen.get("errores", 0) if isinstance(resumen, Mapping) else 0

        html = f"""
<!DOCTYPE html>
<html lang='es'>
<head><meta charset='utf-8'><title>Informe StockPrep</title></head>
<body>
<h1>Informe de procesamiento</h1>
<p>Total de imágenes: {total}</p>
<p>Errores: {errores}</p>
</body>
</html>
"""
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(html)
        return archivo
=======
from pathlib import Path
import json

class ReportGenerator:
    """Genera un informe HTML muy básico."""
    def generar_informe_html(self, resultados: list, carpeta_salida: str | Path, resumen: dict) -> Path:
        carpeta = Path(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)
        html = ["<html><head><meta charset='utf-8'><title>Informe StockPrep</title></head><body>"]
        html.append("<h1>Resultados</h1>")
        html.append(f"<pre>{json.dumps(resultados, indent=2, ensure_ascii=False)}</pre>")
        html.append("</body></html>")
        path = carpeta / "informe.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(html))
        return path

