"""
Orquestador de procesamiento por lotes con Florence-2
"""
import os
from pathlib import Path
import shutil
from typing import Callable, List


class BatchEngine:
    def __init__(self, image_processor, status_callback: Callable = None):
        self.image_processor = image_processor
        self.status_callback = status_callback
        self.stop_processing = False

    def _log(self, message):
        if self.status_callback:
            self.status_callback('log', message)

    def _get_unique_path(self, target: Path) -> Path:
        """Return a unique file path to avoid overwriting existing files."""
        counter = 1
        candidate = target
        while candidate.exists():
            candidate = target.with_name(f"{target.stem}_{counter}{target.suffix}")
            counter += 1
        return candidate

    def run(self, image_folder_path: str) -> List[dict]:
        """Procesa todas las imágenes compatibles en una carpeta."""
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
                # Extraer keywords
                keywords = self.image_processor.extraer_keywords(resultado)
                resultado['keywords'] = keywords

                # Renombrar archivo si hay descripción
                descripcion = resultado.get("descripcion", "").strip()
                if descripcion:
                    nuevo_nombre = descripcion.split('.')[0][:70].replace(' ', '_').replace('/', '-') + path.suffix.lower()
                    nuevo_path = path.parent / nuevo_nombre
                    nuevo_path = self._get_unique_path(nuevo_path)
                    try:
                        shutil.move(str(path), str(nuevo_path))
                        resultado['archivo_renombrado'] = nuevo_path.name
                        resultado['ruta_renombrada'] = str(nuevo_path)
                        self._log(f"  ➡ Archivo renombrado a: {nuevo_path.name}")
                    except Exception as e:
                        self._log(f"  ⚠️ No se pudo renombrar: {e}")

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

