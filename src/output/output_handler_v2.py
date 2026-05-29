#!/usr/bin/env python3
"""
OutputHandlerV2 - Sistema integrado de manejo de salidas con base de datos SQLite
Integra el EnhancedDatabaseManager para StockPrep Pro v2.0
"""

import os
import sys
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import shutil
import yaml
import piexif
import piexif.helper
from iptcinfo3 import IPTCInfo
import logging

iptc_logger = logging.getLogger('iptcinfo')
iptc_logger.setLevel(logging.ERROR)

# Importar el sistema de base de datos avanzado
sys.path.append(str(Path(__file__).parent.parent))
try:
    from core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2 as EnhancedDatabaseManager
except Exception:
    from core.enhanced_database_manager import EnhancedDatabaseManager

class OutputHandlerV2:
    """
    Manejador de salidas integrado con base de datos SQLite avanzada
    
    Funcionalidades:
    - Guardado automático en base de datos
    - Generación de archivos TXT individuales
    - Exportación masiva (JSON, CSV, XML)
    - Copia y renombrado de imágenes
    - Tracking completo de procesamiento
    """
    
    def __init__(self, output_directory: str = "output", db_path: str = "stockprep_images.db"):
        """
        Inicializar el manejador de salidas
        
        Args:
            output_directory: Directorio base de salida
            db_path: Ruta a la base de datos SQLite
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Inicializar base de datos avanzada
        self.db_manager = EnhancedDatabaseManager(db_path)
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Configuración por defecto
        self.copy_and_rename = True
        self.generate_txt_files = True      # TXT resumen por imagen
        self.generate_individual_files = True  # caption/keywords/objects

        # Cargar configuración desde config/settings.yaml si existe
        try:
            project_root = Path(__file__).resolve().parents[2]
            settings_path = project_root / "config" / "settings.yaml"
            if settings_path.is_file():
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = yaml.safe_load(f) or {}

                # Ruta de salida
                ruta_salida = settings.get("ruta_salida") or settings.get("salida", {}).get("ruta")
                if ruta_salida:
                    self.set_output_directory(str(ruta_salida))

                # Flags de TXT y renombrado
                exportar_txt = settings.get("exportar_txt")
                if exportar_txt is None:
                    exportar_txt = settings.get("salida", {}).get("exportar_txt")
                if isinstance(exportar_txt, bool):
                    self.generate_txt_files = exportar_txt

                copiar_renombrar = settings.get("copiar_renombrar")
                if copiar_renombrar is None:
                    copiar_renombrar = settings.get("salida", {}).get("copiar_renombrar")
                if isinstance(copiar_renombrar, bool):
                    self.copy_and_rename = copiar_renombrar
        except Exception as e:
            # No bloquear si la config falla
            self.logger = logging.getLogger(__name__)
            self.logger.warning(f"No se pudo cargar config/settings.yaml: {e}")
        
        self.logger.info(f"OutputHandlerV2 inicializado - Directorio: {self.output_directory}")
    
    def set_output_directory(self, directory: str):
        """Establecer nuevo directorio de salida"""
        self.output_directory = Path(directory)
        self.output_directory.mkdir(exist_ok=True)
        self.logger.info(f"Directorio de salida cambiado a: {self.output_directory}")
    
    def save_results(self, image_path: str, results: Dict, copy_rename: bool = True, embed_metadata: bool = True) -> bool:
        """
        Guardar resultados completos de procesamiento
        
        Args:
            image_path: Ruta a la imagen original
            results: Resultados del procesamiento IA
            copy_rename: Si copiar y renombrar la imagen
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            image_path = Path(image_path)
            
            # 1. Obtener o crear el registro en la BD para obtener un ID
            imagen_id = self.db_manager.obtener_o_crear_registro_id(str(image_path))
            if imagen_id is None:
                self.logger.error(f"No se pudo obtener o crear un registro para {image_path.name}, abortando guardado.")
                return False

            # Normalizar claves para compatibilidad (objects -> objetos_detectados)
            try:
                if isinstance(results, dict) and 'objetos_detectados' not in results and 'objects' in results:
                    results['objetos_detectados'] = results['objects']
            except Exception:
                # No bloquear flujo por un error de normalización
                pass

            # 2. Generar archivos TXT individuales (opcional)
            if self.generate_individual_files:
                self._generate_individual_txt_files(image_path, results)
            
            # 3. Copiar y renombrar imagen si es necesario
            renamed_file, output_path = None, None
            if copy_rename and self.copy_and_rename:
                renamed_file, output_path = self._copy_and_rename_image(image_path, results)
            
            # Inyectar metadatos EXIF/IPTC (Fase 4)
            target_image = output_path if output_path else str(image_path)
            if embed_metadata and target_image:
                self._inyectar_metadatos_imagen(target_image, results, original_image_path=str(image_path))
            
            # 4. Actualizar el registro de la BD con todos los resultados
            db_success = self.db_manager.actualizar_procesamiento_completo(
                imagen_id, results, renamed_file, output_path
            )
            
            # 5. Generar archivo TXT resumen (opcional)
            if self.generate_txt_files:
                self._generate_summary_txt(image_path, results)
            
            if db_success:
                self.logger.info(f"Resultados guardados exitosamente para: {image_path.name}")
            else:
                self.logger.warning(f"Fallo al actualizar el registro en la BD para: {image_path.name}")
            
            return db_success
            
        except Exception as e:
            self.logger.error(f"Error guardando resultados: {e}")
            return False
    
    def _save_to_database(self, image_path: Path, results: Dict) -> bool:
        """Guardar resultados en la base de datos SQLite"""
        try:
            # Preparar datos para la base de datos
            caption = results.get('descripcion') or results.get('caption', '')
            
            # Extraer keywords
            keywords = results.get('keywords', [])
            if isinstance(keywords, str):
                keywords = [kw.strip() for kw in keywords.split(',') if kw.strip()]
            
            # Procesar objetos detectados
            objetos = []
            objects_data = results.get('objects', results.get('objetos', {}))
            if isinstance(objects_data, dict):
                labels = objects_data.get('labels', [])
                bboxes = objects_data.get('bboxes', [])
                scores = objects_data.get('scores', [])
                
                for i, label in enumerate(labels):
                    obj = {'nombre': label}
                    if i < len(bboxes):
                        obj['bbox'] = bboxes[i]
                    if i < len(scores):
                        obj['confianza'] = scores[i]
                    objetos.append(obj)
            elif isinstance(objects_data, list):
                objetos = objects_data
            
            # Insertar en base de datos con detección automática
            success = self.db_manager.insertar_imagen_automatica(
                str(image_path), 
                str(self.output_directory)
            )
            
            # Si la inserción automática no encontró archivos, insertar manualmente
            if not success:
                success = self.db_manager.insertar_imagen_manual(
                    str(image_path),
                    caption=caption,
                    keywords=keywords,
                    objetos=objetos,
                    titulo=results.get('titulo'),
                    descripcion=results.get('descripcion'),
                    estado='completed',
                    modelo_usado='Florence-2',
                    notas=f"Procesado con OutputHandlerV2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error guardando en base de datos: {e}")
            return False
    
    def _generate_individual_txt_files(self, image_path: Path, results: Dict) -> bool:
        """Generar archivos TXT individuales (caption, keywords, objects)"""
        try:
            nombre_base = image_path.stem
            
            # Archivo caption
            caption = results.get('descripcion') or results.get('caption', '')
            if caption:
                caption_file = self.output_directory / f"{nombre_base}_caption.txt"
                with open(caption_file, 'w', encoding='utf-8') as f:
                    f.write(caption.strip())
            
            # Archivo keywords
            keywords = results.get('keywords', [])
            if isinstance(keywords, str):
                keywords = [kw.strip() for kw in keywords.split(',') if kw.strip()]
            
            if keywords:
                keywords_file = self.output_directory / f"{nombre_base}_keywords.txt"
                with open(keywords_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(keywords))
            
            # Archivo objects
            objects_data = results.get('objects', results.get('objetos', {}))
            if objects_data:
                objects_file = self.output_directory / f"{nombre_base}_objects.txt"
                
                # Procesar objetos según formato
                objetos_procesados = []
                if isinstance(objects_data, dict):
                    labels = objects_data.get('labels', [])
                    bboxes = objects_data.get('bboxes', [])
                    scores = objects_data.get('scores', [])
                    
                    for i, label in enumerate(labels):
                        obj = {'nombre': label}
                        if i < len(bboxes):
                            obj['bbox'] = bboxes[i]
                        if i < len(scores):
                            obj['confianza'] = scores[i]
                        objetos_procesados.append(obj)
                elif isinstance(objects_data, list):
                    objetos_procesados = objects_data
                
                if objetos_procesados:
                    with open(objects_file, 'w', encoding='utf-8') as f:
                        json.dump(objetos_procesados, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error generando archivos TXT individuales: {e}")
            return False
    
    def _copy_and_rename_image(self, image_path: Path, results: Dict) -> tuple[Optional[str], Optional[str]]:
        """
        Copia y renombra la imagen basado en la descripción.
        Devuelve siempre una tupla (nombre_renombrado, ruta_salida) o (None, None).
        """
        try:
            if not image_path.exists():
                self.logger.warning(f"Imagen no existe: {image_path}")
                return None, None
            
            # Obtener descripción para el nombre
            descripcion = results.get('descripcion') or results.get('caption', '')
            if not descripcion:
                # Si no hay descripción, no se renombra, pero se puede copiar si se desea.
                # Por ahora, simplemente no hacemos nada si no hay descripción.
                self.logger.info(f"No hay descripción para {image_path.name}, no se copiará ni renombrará.")
                return None, None

            # Limpiar descripción para nombre de archivo
            nombre_limpio = descripcion.split('.')[0][:70]
            nombre_limpio = self._clean_filename(nombre_limpio)
            nuevo_nombre = f"{nombre_limpio}{image_path.suffix.lower()}"
            
            # Ruta de destino
            destino = self.output_directory / nuevo_nombre
            
            # Evitar sobreescribir archivos
            counter = 1
            original_destino = destino
            while destino.exists():
                stem = original_destino.stem
                suffix = original_destino.suffix
                destino = self.output_directory / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Copiar archivo
            shutil.copy2(str(image_path), str(destino))
            
            # Actualizar resultados con el nuevo nombre
            results['renamed_file'] = destino.name
            results['output_path'] = str(destino)
            
            self.logger.info(f"Imagen copiada: {image_path.name} -> {destino.name}")
            return destino.name, str(destino)
            
        except Exception as e:
            self.logger.error(f"Error copiando imagen: {e}")
            return None, None
    
    def _generate_summary_txt(self, image_path: Path, results: Dict) -> bool:
        """Generar archivo TXT resumen con toda la información"""
        try:
            nombre_base = image_path.stem
            txt_file = self.output_directory / f"{nombre_base}_resumen.txt"
            
            # Construir contenido del resumen
            lineas = []
            lineas.append(f"📸 STOCKPREP PRO v2.0 - ANÁLISIS DE IMAGEN")
            lineas.append("=" * 50)
            lineas.append(f"📄 Archivo: {image_path.name}")
            lineas.append(f"📅 Procesado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lineas.append("")
            
            # Descripción/Caption
            descripcion = results.get('descripcion') or results.get('caption', '')
            if descripcion:
                lineas.append("📝 DESCRIPCIÓN:")
                lineas.append(descripcion)
                lineas.append("")
            
            # Keywords
            keywords = results.get('keywords', [])
            if isinstance(keywords, str):
                keywords = [kw.strip() for kw in keywords.split(',') if kw.strip()]
            
            if keywords:
                lineas.append("🏷️ PALABRAS CLAVE:")
                for keyword in keywords:
                    lineas.append(f"  • {keyword}")
                lineas.append("")
            
            # Objetos detectados
            objects_data = results.get('objects', results.get('objetos', {}))
            if objects_data:
                lineas.append("🔍 OBJETOS DETECTADOS:")
                
                if isinstance(objects_data, dict):
                    labels = objects_data.get('labels', [])
                    scores = objects_data.get('scores', [])
                    
                    for i, label in enumerate(labels):
                        confidence = f" ({scores[i]:.2f})" if i < len(scores) else ""
                        lineas.append(f"  • {label}{confidence}")
                elif isinstance(objects_data, list):
                    for obj in objects_data:
                        if isinstance(obj, dict):
                            nombre = obj.get('nombre', 'objeto')
                            confianza = obj.get('confianza', 0)
                            lineas.append(f"  • {nombre} ({confianza:.2f})")
                        else:
                            lineas.append(f"  • {obj}")
                lineas.append("")
            
            # Información técnica
            if results.get('renamed_file'):
                lineas.append("📋 INFORMACIÓN TÉCNICA:")
                lineas.append(f"  📤 Archivo de salida: {results['renamed_file']}")
                lineas.append("")
            
            # Escribir archivo
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lineas))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error generando resumen TXT: {e}")
            return False
    
    def _clean_filename(self, filename: str) -> str:
        """Limpiar nombre de archivo de caracteres problemáticos"""
        # Caracteres problemáticos en nombres de archivo
        problematic_chars = '<>:"/\\|?*'
        
        # Reemplazar caracteres problemáticos
        for char in problematic_chars:
            filename = filename.replace(char, '_')
        
        # Reemplazar múltiples espacios y guiones bajos
        filename = ' '.join(filename.split())
        filename = filename.replace(' ', '_')
        filename = filename.replace('__', '_')
        
        # Remover caracteres al inicio y final
        filename = filename.strip('_-. ')
        
        # Limitar longitud
        if len(filename) > 60:
            filename = filename[:60]
        
        return filename
    
    def get_export_summary(self, image_path: str) -> Dict:
        """Obtener resumen de archivos exportados para una imagen"""
        try:
            image_path = Path(image_path)
            nombre_base = image_path.stem
            
            files_created = {}
            
            # Verificar archivos individuales
            caption_file = self.output_directory / f"{nombre_base}_caption.txt"
            files_created['caption'] = {
                'path': str(caption_file),
                'exists': caption_file.exists()
            }
            
            keywords_file = self.output_directory / f"{nombre_base}_keywords.txt"
            files_created['keywords'] = {
                'path': str(keywords_file),
                'exists': keywords_file.exists()
            }
            
            objects_file = self.output_directory / f"{nombre_base}_objects.txt"
            files_created['objects'] = {
                'path': str(objects_file),
                'exists': objects_file.exists()
            }
            
            resumen_file = self.output_directory / f"{nombre_base}_resumen.txt"
            files_created['resumen'] = {
                'path': str(resumen_file),
                'exists': resumen_file.exists()
            }
            
            return {
                'files_created': files_created,
                'output_directory': str(self.output_directory)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de exportación: {e}")
            return {}
    
    def export_to_json(self, file_path: str, data: Dict = None) -> bool:
        """Exportar datos a formato JSON"""
        try:
            if data is None:
                # Obtener datos de la base de datos
                data = self.db_manager.buscar_imagenes(limite=10000)
            
            export_data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_images': len(data) if isinstance(data, list) else len(data.get('images', [])),
                    'source': 'StockPrep Pro v2.0',
                    'database_version': '2.0'
                },
                'data': data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Datos exportados a JSON: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando a JSON: {e}")
            return False
    
    def export_to_csv(self, file_path: str, data: List[Dict] = None) -> bool:
        """Exportar datos a formato CSV"""
        try:
            if data is None:
                # Obtener datos de la base de datos
                data = self.db_manager.buscar_imagenes(limite=10000)
            
            if not data:
                self.logger.warning("No hay datos para exportar")
                return False
            
            # Determinar campos para CSV
            campos = set()
            for item in data:
                campos.update(item.keys())
            
            campos = sorted(list(campos))
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                
                for item in data:
                    # Convertir listas/dicts a strings para CSV
                    row = {}
                    for campo in campos:
                        valor = item.get(campo, '')
                        if isinstance(valor, (list, dict)):
                            row[campo] = json.dumps(valor, ensure_ascii=False)
                        else:
                            row[campo] = valor
                    writer.writerow(row)
            
            self.logger.info(f"Datos exportados a CSV: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando a CSV: {e}")
            return False
    
    def export_to_xml(self, file_path: str, data: List[Dict] = None) -> bool:
        """Exportar datos a formato XML"""
        try:
            if data is None:
                # Obtener datos de la base de datos
                data = self.db_manager.buscar_imagenes(limite=10000)
            
            # Crear estructura XML
            root = ET.Element("stockprep_export")
            
            # Metadata
            metadata = ET.SubElement(root, "metadata")
            ET.SubElement(metadata, "export_date").text = datetime.now().isoformat()
            ET.SubElement(metadata, "total_images").text = str(len(data))
            ET.SubElement(metadata, "source").text = "StockPrep Pro v2.0"
            
            # Datos
            images_elem = ET.SubElement(root, "images")
            
            for item in data:
                image_elem = ET.SubElement(images_elem, "image")
                
                for key, value in item.items():
                    elem = ET.SubElement(image_elem, key)
                    if isinstance(value, (list, dict)):
                        elem.text = json.dumps(value, ensure_ascii=False)
                    else:
                        elem.text = str(value) if value is not None else ""
            
            # Escribir archivo
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            self.logger.info(f"Datos exportados a XML: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando a XML: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Obtener estadísticas de la base de datos"""
        try:
            return self.db_manager.obtener_estadisticas()
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def search_images(self, filters: Dict = None, limit: int = 100) -> List[Dict]:
        """Buscar imágenes en la base de datos"""
        try:
            return self.db_manager.buscar_imagenes(filters, limit)
        except Exception as e:
            self.logger.error(f"Error buscando imágenes: {e}")
            return []
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """Limpiar archivos antiguos"""
        try:
            # Limpiar registros antiguos de la base de datos
            deleted_records = self.db_manager.limpiar_registros_antiguos(days)
            
            # Aquí se podría agregar lógica para limpiar archivos físicos antiguos
            # if needed...
            
            return deleted_records
        except Exception as e:
            self.logger.error(f"Error limpiando archivos antiguos: {e}")
            return 0
    
    def close(self):
        """Cerrar conexiones y limpiar recursos"""
        try:
            self.db_manager.cerrar_conexion()
            self.logger.info("OutputHandlerV2 cerrado correctamente")
        except Exception as e:
            self.logger.error(f"Error cerrando OutputHandlerV2: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _inyectar_metadatos_imagen(self, image_path: str, results: Dict, original_image_path: str = None):
        """Inyecta Caption y Keywords en los metadatos EXIF e IPTC (Fase 4)"""
        try:
            caption = results.get('descripcion') or results.get('caption', '')
            keywords = results.get('keywords', [])
            if isinstance(keywords, str):
                keywords = [k.strip() for k in keywords.split(',') if k.strip()]
            
            if not caption and not keywords:
                return
            
            str_path = str(image_path)
            original_name = Path(original_image_path).name if original_image_path else Path(image_path).name
            ai_origin = {}
            try:
                from src.utils.ai_origin import detect_ai_origin
                ai_origin = detect_ai_origin(
                    image_path=original_image_path or image_path,
                    original_name=original_name,
                )
            except Exception:
                ai_origin = {"is_ai_generated": False, "generator": "Desconocido", "source_name": original_name}
            
            # --- 1. Guardar IPTC (Estándar microstock) ---
            try:
                info = IPTCInfo(str_path, force=True)
                if caption:
                    info['caption/abstract'] = caption.encode('utf-8')
                if keywords:
                    info['keywords'] = [k.encode('utf-8') for k in keywords]
                info.save()
                # Eliminar backup de IPTCInfo
                backup_file = Path(str_path + '~')
                if backup_file.exists():
                    backup_file.unlink()
            except Exception as e:
                self.logger.warning(f"No se pudo guardar IPTC en {Path(image_path).name}: {e}")

            # --- 2. Guardar EXIF (XPKeywords para Windows y ImageDescription) ---
            try:
                try:
                    exif_dict = piexif.load(str_path)
                except Exception:
                    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}}
                
                if caption:
                    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = caption.encode('utf-8')
                    exif_dict["0th"][0x9c9b] = caption.encode("utf-16le") # XPTitle
                if keywords:
                    xp_kw = ";".join(keywords).encode("utf-16le")
                    exif_dict["0th"][0x9c9e] = xp_kw # XPKeywords
                provenance_note = (
                    f"StockPrep original filename: {original_name}; "
                    f"image origin: {ai_origin.get('generator', 'Desconocido')}"
                )
                exif_dict["0th"][0x9c9c] = provenance_note.encode("utf-16le") # XPComment
                
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, str_path)
            except Exception as e:
                self.logger.warning(f"No se pudo guardar EXIF en {Path(image_path).name}: {e}")
                
            self.logger.info(f"Metadatos EXIF/IPTC inyectados correctamente en {Path(image_path).name}")
        except Exception as e:
            self.logger.error(f"Error inyectando metadatos en {image_path}: {e}")


# Funciones de utilidad para integración fácil
def create_output_handler(output_dir: str = "output", db_path: str = "stockprep_database.db") -> OutputHandlerV2:
    """
    Crear una nueva instancia del manejador de salidas
    
    Args:
        output_dir: Directorio de salida
        db_path: Ruta a la base de datos
        
    Returns:
        Instancia del manejador de salidas
    """
    return OutputHandlerV2(output_dir, db_path)


if __name__ == "__main__":
    # Ejemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # Crear manejador de salidas
    handler = OutputHandlerV2("test_output", "test_database.db")
    
    # Ejemplo de resultados simulados
    resultados_ejemplo = {
        'descripcion': 'Una hermosa imagen de paisaje con montañas',
        'keywords': ['paisaje', 'montañas', 'naturaleza'],
        'objetos': {
            'labels': ['montaña', 'cielo', 'árbol'],
            'scores': [0.95, 0.88, 0.76],
            'bboxes': [[10, 20, 100, 150], [0, 0, 400, 100], [200, 300, 250, 400]]
        }
    }
    
    # Guardar resultados
    success = handler.save_results("test_image.jpg", resultados_ejemplo)
    print(f"Guardado exitoso: {success}")
    
    # Obtener estadísticas
    stats = handler.get_database_stats()
    print(f"Estadísticas: {stats}")
    
    # Cerrar
    handler.close() 
