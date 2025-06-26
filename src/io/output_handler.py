"""Gestor de exportación de resultados.

Este módulo se encarga únicamente de copiar las imágenes procesadas,
generar archivos ``.txt`` opcionales y servir de ayuda para exportar
la información generada por :class:`core.batch_engine.BatchEngine`.
"""
import os
import shutil
import yaml
from pathlib import Path
from typing import Callable, List


class OutputHandler:
    """Gestiona la copia de archivos y la creación de ficheros de salida."""

    def __init__(self, image_processor, status_callback: Callable = None):
        self.image_processor = image_processor
        self.status_callback = status_callback
        self.stop_processing = False
        # _leer_config_salida inicializa self.exportar_txt
        self.output_dir = self._leer_config_salida()
        os.makedirs(self.output_dir, exist_ok=True)

    def _leer_config_salida(self):
        """Lee la configuración de salida y la opción de exportar TXT.

        Si `exportar_txt` no está definida en ``settings.yaml`` se asume ``True``
        para mantener la compatibilidad con versiones anteriores.
        """
        try:
            repo_root = Path(__file__).resolve().parents[2]
            config_path = repo_root / "config" / "settings.yaml"
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Bandera que indica si se generará un TXT por imagen procesada
            self.exportar_txt = config.get("exportar_txt", True)

            ruta = config.get("ruta_salida", "output")
            ruta_path = Path(ruta)
            if not ruta_path.is_absolute():
                ruta_path = repo_root / ruta

            return str(ruta_path)
        except Exception as e:
            self.exportar_txt = True
            self._log(f"⚠️ No se pudo leer la ruta de salida: {e}")
            return str(Path.cwd() / "output")

    def _log(self, message):
        if self.status_callback:
            self.status_callback('log', message)

    def _guardar_txt(self, resultado: dict):
        titulo = resultado.get("descripcion", "").split('.')[0][:70]
        descripcion = resultado.get("descripcion", "(sin descripción)")
        objetos = resultado.get("objetos", {}).get("labels", []) if isinstance(resultado.get("objetos"), dict) else []
        keywords = resultado.get("keywords", [])

        txt = []
        txt.append(f"\U0001F4CC Título: {titulo}\n")
        txt.append("\U0001F4DD Descripción:\n")
        txt.append(descripcion.strip() + "\n")
        txt.append("\n\U0001F50D Objetos detectados:")
        for obj in objetos:
            txt.append(f"- {obj}")
        txt.append("\n\U0001F3F7️ Palabras clave:")
        for kw in keywords:
            txt.append(f"- {kw}")

        nombre_txt = Path(resultado['archivo_renombrado']).stem + ".txt"
        ruta_txt = Path(self.output_dir) / nombre_txt

        try:
            with open(ruta_txt, "w", encoding="utf-8") as f:
                f.write("\n".join(txt))
        except Exception as e:
            self._log(f"⚠️ No se pudo guardar el .txt: {e}")

    def run(self, image_folder_path: str) -> List[dict]:
        """Procesa y guarda todas las imágenes compatibles de una carpeta."""
        self.stop_processing = False
        image_paths = [
            p for p in Path(image_folder_path).iterdir()
            if p.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
        ]

        if not image_paths:
            self._log("❌ No se encontraron imágenes compatibles en la carpeta.")
            return []

        self._log(f"📂 Se encontraron {len(image_paths)} imágenes. Iniciando procesamiento...")
        all_results = []

        for i, path in enumerate(image_paths):
            if self.stop_processing:
                self._log("⏹️ Procesamiento detenido por el usuario.")
                break

            if self.status_callback:
                self.status_callback('progress', (i + 1, len(image_paths)))

            self._log(f"🖼️ Procesando: {path.name}")

            resultado = self.image_processor.procesar_imagen(str(path))
            resultado['archivo_original'] = path.name
            resultado['ruta_original'] = str(path)

            if not resultado.get("error"):
                keywords = self.image_processor.extraer_keywords(resultado)
                resultado['keywords'] = keywords

                descripcion = resultado.get("descripcion", "").strip()
                if descripcion:
                    nuevo_nombre = descripcion.split('.')[0][:70].replace(' ', '_').replace('/', '-') + path.suffix.lower()
                    nuevo_path = Path(self.output_dir) / nuevo_nombre
                    try:
                        shutil.copy(str(path), str(nuevo_path))
                        resultado['archivo_renombrado'] = nuevo_nombre
                        resultado['ruta_renombrada'] = str(nuevo_path)
                        if self.exportar_txt:
                            self._guardar_txt(resultado)
                        self._log(f"  ➡ Copiado como: {nuevo_nombre}")
                    except Exception as e:
                        self._log(f"  ⚠️ No se pudo copiar: {e}")

                self._log(f"  ✍️ Descripción: {descripcion[:80]}...")
                self._log(f"  🌐 Keywords: {', '.join(keywords)}")
            else:
                self._log(f"  ❌ Error: {resultado['error']}")

            all_results.append(resultado)

        if not self.stop_processing:
            self._log("✅ ¡Procesamiento de lote completado!")

        return all_results

    def stop(self):
        self.stop_processing = True

class OutputHandler:
    """Exporta resultados en varios formatos."""
    def __init__(self, carpeta_salida: str | Path):
        self.carpeta = Path(carpeta_salida)
        self.carpeta.mkdir(parents=True, exist_ok=True)

    def exportar(self, resultados: list, formato: str = "JSON") -> Path:
        formato = formato.upper()
        if formato == "CSV":
            return self._exportar_csv(resultados)
        if formato == "XML":
            return self._exportar_xml(resultados)
        return self._exportar_json(resultados)

    def _exportar_json(self, resultados: list) -> Path:
        from datetime import datetime
        import json
        archivo = self.carpeta / f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        return archivo

    def _exportar_csv(self, resultados: list) -> Path:
        from datetime import datetime
        import csv
        archivo = self.carpeta / f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        campos = resultados[0].keys() if resultados else []
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for r in resultados:
                writer.writerow(r)
        return archivo

    def _exportar_xml(self, resultados: list) -> Path:
        from datetime import datetime
        import xml.etree.ElementTree as ET
        archivo = self.carpeta / f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        root = ET.Element("resultados")
        for r in resultados:
            item = ET.SubElement(root, "imagen")
            for k, v in r.items():
                ET.SubElement(item, k).text = str(v)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(archivo, encoding="utf-8", xml_declaration=True)
        return archivo
