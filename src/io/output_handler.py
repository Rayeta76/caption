"""
Orquestador de procesamiento por lotes con Florence-2 (versión salida configurada + exportación .txt)
Incluye lógica para generar rutas únicas y evitar sobrescribir archivos.
"""
import os
import shutil
import yaml
from pathlib import Path
from typing import Callable, List


class BatchEngine:
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

    def _generar_ruta_unica(self, ruta_base: Path) -> Path:
        """Genera una ruta única para evitar sobrescribir archivos existentes.
        
        Args:
            ruta_base: La ruta base deseada para el archivo
            
        Returns:
            Path: Una ruta única que no existe en el sistema de archivos
        """
        if not ruta_base.exists():
            return ruta_base
        
        contador = 1
        nombre_base = ruta_base.stem
        extension = ruta_base.suffix
        directorio = ruta_base.parent
        
        while True:
            nuevo_nombre = f"{nombre_base}_{contador}{extension}"
            nueva_ruta = directorio / nuevo_nombre
            if not nueva_ruta.exists():
                return nueva_ruta
            contador += 1

    def _guardar_txt(self, resultado: dict):
        """Guarda un archivo TXT descriptivo para la imagen procesada."""
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
        ruta_txt_base = Path(self.output_dir) / nombre_txt
        ruta_txt_unica = self._generar_ruta_unica(ruta_txt_base)

        try:
            with open(ruta_txt_unica, "w", encoding="utf-8") as f:
                f.write("\n".join(txt))
            self._log(f"  📄 TXT guardado: {ruta_txt_unica.name}")
        except Exception as e:
            self._log(f"⚠️ No se pudo guardar el .txt: {e}")

    def _generar_nombre_archivo(self, descripcion: str, extension: str) -> str:
        """Genera un nombre de archivo válido basado en la descripción."""
        # Limpiar la descripción para crear un nombre de archivo válido
        nombre_limpio = descripcion.split('.')[0][:70]
        # Reemplazar caracteres problemáticos
        caracteres_invalidos = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in caracteres_invalidos:
            nombre_limpio = nombre_limpio.replace(char, '-')
        
        # Reemplazar espacios múltiples y limpiar
        nombre_limpio = ' '.join(nombre_limpio.split())
        nombre_limpio = nombre_limpio.replace(' ', '_')
        
        # Asegurar que no esté vacío
        if not nombre_limpio:
            nombre_limpio = "imagen_sin_descripcion"
            
        return nombre_limpio + extension.lower()

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
                keywords = self.image_processor.extraer_keywords(resultado)
                resultado['keywords'] = keywords

                descripcion = resultado.get("descripcion", "").strip()
                if descripcion:
                    # Generar nombre de archivo válido
                    nuevo_nombre = self._generar_nombre_archivo(descripcion, path.suffix)
                    
                    # Generar ruta única para evitar sobrescribir
                    nuevo_path_base = Path(self.output_dir) / nuevo_nombre
                    nuevo_path_unico = self._generar_ruta_unica(nuevo_path_base)
                    
                    try:
                        shutil.copy(str(path), str(nuevo_path_unico))
                        resultado['archivo_renombrado'] = nuevo_path_unico.name
                        resultado['ruta_renombrada'] = str(nuevo_path_unico)
                        
                        # Guardar archivo TXT si está habilitado
                        if self.exportar_txt:
                            self._guardar_txt(resultado)
                            
                        self._log(f"  ➡ Copiado como: {nuevo_path_unico.name}")
                    except Exception as e:
                        self._log(f"  ⚠️ No se pudo copiar: {e}")
                        # En caso de error, mantener información del archivo original
                        resultado['archivo_renombrado'] = path.name
                        resultado['ruta_renombrada'] = str(path)

                self._log(f"  ✍️ Descripción: {descripcion[:80]}...")
                self._log(f"  🌐 Keywords: {', '.join(keywords)}")
            else:
                self._log(f"  ❌ Error: {resultado['error']}")
                # Para archivos con error, mantener información básica
                resultado['archivo_renombrado'] = path.name
                resultado['ruta_renombrada'] = str(path)

            all_results.append(resultado)

        if not self.stop_processing:
            self._log("✅ ¡Procesamiento de lote completado!")

        return all_results

    def stop(self):
        """Detiene el procesamiento en curso."""
        self.stop_processing = True


class OutputHandler:
    """Exporta resultados en varios formatos."""
    
    def __init__(self, carpeta_salida: str | Path):
        self.carpeta = Path(carpeta_salida)
        self.carpeta.mkdir(parents=True, exist_ok=True)

    def _generar_nombre_archivo_unico(self, nombre_base: str, extension: str) -> Path:
        """Genera un nombre de archivo único en la carpeta de salida."""
        archivo_base = self.carpeta / f"{nombre_base}{extension}"
        
        if not archivo_base.exists():
            return archivo_base
            
        contador = 1
        while True:
            nuevo_nombre = f"{nombre_base}_{contador}{extension}"
            nuevo_archivo = self.carpeta / nuevo_nombre
            if not nuevo_archivo.exists():
                return nuevo_archivo
            contador += 1

    def exportar(self, resultados: list, formato: str = "JSON") -> Path:
        """Exporta los resultados en el formato especificado.
        
        Args:
            resultados: Lista de diccionarios con los resultados del procesamiento
            formato: Formato de exportación ("JSON", "CSV", "XML")
            
        Returns:
            Path: Ruta del archivo generado
        """
        formato = formato.upper()
        if formato == "CSV":
            return self._exportar_csv(resultados)
        elif formato == "XML":
            return self._exportar_xml(resultados)
        else:
            return self._exportar_json(resultados)

    def _exportar_json(self, resultados: list) -> Path:
        """Exporta los resultados en formato JSON."""
        from datetime import datetime
        import json
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo = self._generar_nombre_archivo_unico(f"resultados_{timestamp}", ".json")
        
        try:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Error al exportar JSON: {e}")
            
        return archivo

    def _exportar_csv(self, resultados: list) -> Path:
        """Exporta los resultados en formato CSV."""
        from datetime import datetime
        import csv
        
        if not resultados:
            raise ValueError("No hay resultados para exportar")
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo = self._generar_nombre_archivo_unico(f"resultados_{timestamp}", ".csv")
        
        # Obtener todos los campos únicos de todos los resultados
        campos = set()
        for resultado in resultados:
            campos.update(resultado.keys())
        campos = sorted(list(campos))
        
        try:
            with open(archivo, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                for resultado in resultados:
                    # Convertir listas y objetos complejos a strings
                    fila = {}
                    for campo in campos:
                        valor = resultado.get(campo, "")
                        if isinstance(valor, (list, dict)):
                            fila[campo] = str(valor)
                        else:
                            fila[campo] = valor
                    writer.writerow(fila)
        except Exception as e:
            raise Exception(f"Error al exportar CSV: {e}")
            
        return archivo

    def _exportar_xml(self, resultados: list) -> Path:
        """Exporta los resultados en formato XML."""
        from datetime import datetime
        import xml.etree.ElementTree as ET
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo = self._generar_nombre_archivo_unico(f"resultados_{timestamp}", ".xml")
        
        try:
            root = ET.Element("resultados")
            root.set("timestamp", timestamp)
            root.set("total", str(len(resultados)))
            
            for i, resultado in enumerate(resultados):
                item = ET.SubElement(root, "imagen")
                item.set("id", str(i + 1))
                
                for clave, valor in resultado.items():
                    elemento = ET.SubElement(item, clave.replace(" ", "_"))
                    if isinstance(valor, (list, dict)):
                        elemento.text = str(valor)
                    else:
                        elemento.text = str(valor) if valor is not None else ""
            
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            tree.write(archivo, encoding="utf-8", xml_declaration=True)
        except Exception as e:
            raise Exception(f"Error al exportar XML: {e}")
            
        return archivo