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
