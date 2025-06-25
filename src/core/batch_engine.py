"""
Orquestador de procesamiento por lotes con Florence-2
"""
import os
from pathlib import Path
import shutil
from typing import Callable, List
from concurrent.futures import ThreadPoolExecutor, as_completed


class BatchEngine:
    def __init__(self, image_processor, status_callback: Callable = None):
        self.image_processor = image_processor
        self.status_callback = status_callback
        self.stop_processing = False

    def _log(self, message):
        if self.status_callback:
            self.status_callback('log', message)

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

        self._log(
            f"📂 Se encontraron {len(image_paths)} imágenes. Iniciando procesamiento..."
        )
        resultados: List[dict | None] = [None] * len(image_paths)

        def procesar(idx: int, path: Path):
            if self.stop_processing:
                return idx, None

            self._log(f"🖼️ Procesando: {path.name}")

            res = self.image_processor.procesar_imagen(str(path))
            res['archivo_original'] = path.name
            res['ruta_original'] = str(path)

            if not res.get("error"):
                kws = self.image_processor.extraer_keywords(res)
                res['keywords'] = kws

                descripcion = res.get("descripcion", "").strip()
                if descripcion:
                    nuevo_nombre = (
                        descripcion.split('.')[0][:70]
                        .replace(' ', '_')
                        .replace('/', '-')
                        + path.suffix.lower()
                    )
                    nuevo_path = path.parent / nuevo_nombre
                    try:
                        shutil.move(str(path), str(nuevo_path))
                        res['archivo_renombrado'] = nuevo_nombre
                        res['ruta_renombrada'] = str(nuevo_path)
                        self._log(f"  ➡ Archivo renombrado a: {nuevo_nombre}")
                    except Exception as e:
                        self._log(f"  ⚠️ No se pudo renombrar: {e}")

                self._log(f"  ✍️ Descripción: {descripcion[:80]}...")
                self._log(f"  🌐 Keywords: {', '.join(kws)}")
            else:
                self._log(f"  ❌ Error: {res['error']}")

            if self.status_callback:
                self.status_callback('progress', (idx + 1, len(image_paths)))

            return idx, res

        executor = ThreadPoolExecutor(max_workers=4)
        futures = [executor.submit(procesar, i, p) for i, p in enumerate(image_paths)]

        try:
            for fut in as_completed(futures):
                idx, res = fut.result()
                if res is not None:
                    resultados[idx] = res
                if self.stop_processing:
                    self._log("⏹️ Procesamiento detenido por el usuario.")
                    for f in futures:
                        f.cancel()
                    break
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        processed = [r for r in resultados if r is not None]
        if not self.stop_processing:
            self._log("✅ ¡Procesamiento de lote completado!")

        return processed

    def stop(self):
        self.stop_processing = True
