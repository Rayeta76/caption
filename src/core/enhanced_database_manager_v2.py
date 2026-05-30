"""
Enhanced Database Manager v2.0 - Con FTS5 y WebP Thumbnails
StockPrep Pro v2.0 - Optimizado para galería tipo web de stock

Mejoras implementadas:
- Búsqueda FTS5 para búsquedas súper rápidas con triggers de SQLite para sincronización
- Thumbnails WebP en BLOB para rendimiento óptimo
- Vista ampliada y navegación mejorada
- Patrón Singleton thread-safe heredado de EnhancedDatabaseManager
- Hereda todos los métodos base de EnhancedDatabaseManager
"""

import sqlite3
import os
import json
import io
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from PIL import Image, ImageOps

from src.core.enhanced_database_manager import EnhancedDatabaseManager
from src.utils.bilingual_metadata import normalize_bilingual_results

class EnhancedDatabaseManagerV2(EnhancedDatabaseManager):
    """
    Sistema avanzado de gestión de base de datos SQLite con FTS5 y WebP
    Optimizado para galería tipo web de stock y heredero de la base v1.0
    """
    _instances = {}
    _lock = threading.Lock()
    
    def __init__(self, db_path: str = "stockprep_images.db"):
        """
        Inicializar el gestor de base de datos v2.0
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        if getattr(self, '_initialized', False):
            return
        super().__init__(db_path)
        self._initialized = True
    
    def _init_database(self):
        """Inicializar la base de datos con FTS5 y soporte WebP"""
        try:
            # Primero llamamos al inicializador base para asegurar la estructura básica de v1
            super()._init_database()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Habilitar FTS5
                cursor.execute("PRAGMA compile_options")
                compile_options = [row[0] for row in cursor.fetchall()]
                if 'ENABLE_FTS5' not in compile_options:
                    self.logger.warning("FTS5 no está habilitado en esta compilación de SQLite")
                
                # Crear tabla FTS5 para búsqueda súper rápida
                cursor.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS imagenes_fts USING fts5(
                        nombre_original,
                        titulo,
                        descripcion,
                        caption,
                        keywords,
                        etiquetas,
                        content='imagenes',
                        content_rowid='id'
                    )
                ''')
                
                # Crear tabla de estadísticas de procesamiento si no existe
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS estadisticas_procesamiento (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha DATE DEFAULT (date('now')),
                        imagenes_procesadas INTEGER DEFAULT 0,
                        tiempo_promedio_segundos REAL DEFAULT 0,
                        modelo_usado TEXT,
                        errores_encontrados INTEGER DEFAULT 0,
                        UNIQUE(fecha, modelo_usado)
                    )
                ''')
                
                # Asegurar columnas específicas de v2 en 'imagenes'
                self._ensure_schema_columns(cursor)

                # Crear índices optimizados para galería
                indices = [
                    "CREATE INDEX IF NOT EXISTS idx_thumbnail_size ON imagenes(thumbnail_size)",
                ]
                
                for indice in indices:
                    try:
                        cursor.execute(indice)
                    except sqlite3.OperationalError:
                        pass
                
                # Verificar soporte de funciones JSON en SQLite para los triggers
                self._has_sqlite_triggers = False
                try:
                    cursor.execute("SELECT json_valid('[]')")
                    self._has_sqlite_triggers = True
                except sqlite3.OperationalError:
                    self.logger.warning("Funciones JSON de SQLite no disponibles en esta versión. Se usará sincronización FTS5 manual.")

                if self._has_sqlite_triggers:
                    # Crear triggers para sincronización automática FTS5 (INSERT, UPDATE y DELETE)
                    cursor.execute('''
                        CREATE TRIGGER IF NOT EXISTS imagenes_ai AFTER INSERT ON imagenes BEGIN
                            INSERT INTO imagenes_fts(rowid, nombre_original, titulo, descripcion, caption, keywords, etiquetas)
                            VALUES (
                                new.id,
                                new.nombre_original,
                                new.titulo,
                                new.descripcion,
                                new.caption,
                                CASE WHEN json_valid(new.keywords) THEN (SELECT group_concat(value, ' ') FROM json_each(new.keywords)) ELSE '' END,
                                CASE WHEN json_valid(new.etiquetas) THEN (SELECT group_concat(value, ' ') FROM json_each(new.etiquetas)) ELSE '' END
                            );
                        END;
                    ''')
                    
                    cursor.execute('''
                        CREATE TRIGGER IF NOT EXISTS imagenes_au AFTER UPDATE ON imagenes BEGIN
                            INSERT OR REPLACE INTO imagenes_fts(rowid, nombre_original, titulo, descripcion, caption, keywords, etiquetas)
                            VALUES (
                                new.id,
                                new.nombre_original,
                                new.titulo,
                                new.descripcion,
                                new.caption,
                                CASE WHEN json_valid(new.keywords) THEN (SELECT group_concat(value, ' ') FROM json_each(new.keywords)) ELSE '' END,
                                CASE WHEN json_valid(new.etiquetas) THEN (SELECT group_concat(value, ' ') FROM json_each(new.etiquetas)) ELSE '' END
                            );
                        END;
                    ''')
                    
                    cursor.execute('''
                        CREATE TRIGGER IF NOT EXISTS imagenes_ad AFTER DELETE ON imagenes BEGIN
                            DELETE FROM imagenes_fts WHERE rowid = old.id;
                        END;
                    ''')

                # Migrar datos existentes si es necesario
                self._migrate_existing_data(cursor)
                
                conn.commit()
                self.logger.info(f"Base de datos v2.0 inicializada correctamente: {self.db_path}")
                
        except Exception as e:
            self.logger.error(f"Error al inicializar la base de datos v2.0: {e}")
            raise
            
    def _ensure_schema_columns(self, cursor):
        """Añade columnas v2 a bases de datos creadas con el gestor v1."""
        cursor.execute("PRAGMA table_info(imagenes)")
        columnas = {column[1] for column in cursor.fetchall()}
        nuevas = {
            "thumbnail_webp": "BLOB",
            "thumbnail_size": "INTEGER",
            "caption_en": "TEXT",
            "caption_es": "TEXT",
            "keywords_en": "TEXT",
            "keywords_es": "TEXT",
            "visual_attributes": "TEXT",
        }
        for columna, tipo in nuevas.items():
            if columna not in columnas:
                cursor.execute(f"ALTER TABLE imagenes ADD COLUMN {columna} {tipo}")

        cursor.execute(
            """
            UPDATE imagenes
            SET
                caption_en = COALESCE(NULLIF(caption_en, ''), caption),
                keywords_en = COALESCE(NULLIF(keywords_en, ''), keywords)
            WHERE (caption_en IS NULL OR caption_en = '' OR keywords_en IS NULL OR keywords_en = '')
            """
        )
 
    def _migrate_existing_data(self, cursor):
        """Migrar datos existentes y crear thumbnails WebP"""
        try:
            cursor.execute("PRAGMA table_info(imagenes)")
            columnas = {column[1] for column in cursor.fetchall()}
            if "thumbnail_webp" not in columnas:
                return

            # Verificar si hay datos existentes sin thumbnails
            cursor.execute("SELECT COUNT(*) FROM imagenes WHERE thumbnail_webp IS NULL")
            count = cursor.fetchone()[0]
            
            if count > 0:
                self.logger.info(f"Migrando {count} imágenes existentes a formato v2.0...")
                
                # Obtener imágenes sin thumbnails
                cursor.execute("SELECT id, ruta_completa FROM imagenes WHERE thumbnail_webp IS NULL")
                imagenes_sin_thumbnail = cursor.fetchall()
                
                for imagen_id, ruta_completa in imagenes_sin_thumbnail:
                    try:
                        if Path(ruta_completa).exists():
                            # Crear thumbnail WebP
                            thumbnail_webp = self._create_webp_thumbnail(ruta_completa)
                            if thumbnail_webp:
                                cursor.execute(
                                    "UPDATE imagenes SET thumbnail_webp = ?, thumbnail_size = ? WHERE id = ?",
                                    (thumbnail_webp, len(thumbnail_webp), imagen_id)
                                )
                                
                                # Si los triggers no están activos, actualizamos FTS5 manualmente
                                if not getattr(self, '_has_sqlite_triggers', False):
                                    self._update_fts5(cursor, imagen_id)
                                
                    except Exception as e:
                        self.logger.warning(f"Error migrando imagen {ruta_completa}: {e}")
                
                self.logger.info("Migración completada")
                
        except Exception as e:
            self.logger.error(f"Error en migración: {e}")
            
    def _create_webp_thumbnail(self, image_path: str, size: Tuple[int, int] = (300, 300)) -> Optional[bytes]:
        """
        Crear thumbnail WebP optimizado para galería
        
        Args:
            image_path: Ruta a la imagen
            size: Tamaño del thumbnail (ancho, alto)
            
        Returns:
            Bytes del thumbnail WebP o None si hay error
        """
        try:
            with Image.open(image_path) as img:
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Crear thumbnail manteniendo proporción
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Aplicar optimizaciones
                img = ImageOps.exif_transpose(img)  # Corregir orientación EXIF
                
                # Convertir a WebP con compresión optimizada
                webp_buffer = io.BytesIO()
                img.save(webp_buffer, format='WebP', quality=85, optimize=True)
                
                return webp_buffer.getvalue()
                
        except Exception as e:
            self.logger.warning(f"Error creando thumbnail WebP para {image_path}: {e}")
            return None
            
    def _update_fts5(self, cursor, imagen_id: int):
        """Actualizar índice FTS5 para una imagen manualmente (como fallback)"""
        try:
            # Obtener datos de la imagen
            cursor.execute("""
                SELECT nombre_original, titulo, descripcion, caption, keywords, etiquetas
                FROM imagenes WHERE id = ?
            """, (imagen_id,))
            
            row = cursor.fetchone()
            if row:
                nombre_original, titulo, descripcion, caption, keywords, etiquetas = row
                
                # Preparar datos para FTS5
                keywords_text = ""
                etiquetas_text = ""
                
                try:
                    if keywords:
                        keywords_list = json.loads(keywords)
                        keywords_text = " ".join(keywords_list)
                except:
                    pass
                
                try:
                    if etiquetas:
                        etiquetas_list = json.loads(etiquetas)
                        etiquetas_text = " ".join(etiquetas_list)
                except:
                    pass
                
                # Insertar o actualizar en FTS5
                cursor.execute("""
                    INSERT OR REPLACE INTO imagenes_fts(
                        rowid, nombre_original, titulo, descripcion, caption, keywords, etiquetas
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    imagen_id,
                    nombre_original or "",
                    titulo or "",
                    descripcion or "",
                    caption or "",
                    keywords_text,
                    etiquetas_text
                ))
                
        except Exception as e:
            self.logger.warning(f"Error actualizando FTS5 para imagen {imagen_id}: {e}")
            
    def insertar_imagen_automatica(self, imagen_path: str, output_dir: str = None) -> bool:
        """
        Insertar imagen con procesamiento automático y thumbnail WebP
        
        Args:
            imagen_path: Ruta completa a la imagen
            output_dir: Directorio donde buscar los archivos TXT (opcional)
            
        Returns:
            bool: True si se insertó correctamente
        """
        try:
            imagen_path = Path(imagen_path)
            if not imagen_path.exists():
                self.logger.error(f"La imagen no existe: {imagen_path}")
                return False
            
            # Determinar directorio de salida
            if output_dir is None:
                output_dir = imagen_path.parent
            else:
                output_dir = Path(output_dir)
            
            # Obtener nombre base de la imagen (sin extensión)
            nombre_base = imagen_path.stem
            
            # Buscar archivos de procesamiento
            caption_file = output_dir / f"{nombre_base}_caption.txt"
            caption_es_file = output_dir / f"{nombre_base}_caption_es.txt"
            keywords_file = output_dir / f"{nombre_base}_keywords.txt"
            keywords_es_file = output_dir / f"{nombre_base}_keywords_es.txt"
            objects_file = output_dir / f"{nombre_base}_objects.txt"
            
            # Leer contenido de archivos
            caption = self._leer_archivo_txt(caption_file) if caption_file.exists() else None
            caption_es = self._leer_archivo_txt(caption_es_file) if caption_es_file.exists() else None
            keywords = self._leer_keywords_txt(keywords_file) if keywords_file.exists() else []
            keywords_es = self._leer_keywords_txt(keywords_es_file) if keywords_es_file.exists() else []
            objetos = self._leer_objects_txt(objects_file) if objects_file.exists() else []
            
            # Obtener metadatos de la imagen
            metadatos = self._obtener_metadatos_imagen(imagen_path)
            
            # Crear thumbnail WebP
            thumbnail_webp = self._create_webp_thumbnail(str(imagen_path))
            
            # Determinar estado basado en archivos encontrados
            if caption or keywords or objetos:
                estado = 'completed'
                modelo_usado = 'Florence-2'
                fecha_procesamiento = datetime.now()
            else:
                estado = 'pending'
                modelo_usado = None
                fecha_procesamiento = None
            
            # Insertar en base de datos
            return self._insertar_imagen_db(
                imagen_path=str(imagen_path),
                metadatos=metadatos,
                caption=caption,
                caption_en=caption,
                caption_es=caption_es,
                keywords=keywords,
                keywords_en=keywords,
                keywords_es=keywords_es,
                objetos=objetos,
                thumbnail_webp=thumbnail_webp,
                estado=estado,
                modelo_usado=modelo_usado,
                fecha_procesamiento=fecha_procesamiento
            )
            
        except Exception as e:
            self.logger.error(f"Error en inserción automática: {e}")
            return False
            
    def _insertar_imagen_db(self, imagen_path: str, metadatos: Dict, **kwargs) -> bool:
        """Insertar imagen en la base de datos con thumbnail WebP"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Preparar datos
                imagen_path = Path(imagen_path)
                normalized = normalize_bilingual_results(kwargs)
                keywords_json = json.dumps(normalized.get('keywords', []), ensure_ascii=False)
                keywords_en_json = json.dumps(normalized.get('keywords_en', []), ensure_ascii=False)
                keywords_es_json = json.dumps(normalized.get('keywords_es', []), ensure_ascii=False)
                visual_attributes_json = json.dumps(kwargs.get('visual_attributes', {}), ensure_ascii=False)
                objetos_json = json.dumps(kwargs.get('objetos', []), ensure_ascii=False)
                etiquetas_json = json.dumps(kwargs.get('etiquetas', []), ensure_ascii=False)
                metadatos_exif_json = json.dumps(metadatos.get('exif', {}), ensure_ascii=False)
                thumbnail_webp = kwargs.get('thumbnail_webp')
                thumbnail_size = len(thumbnail_webp) if thumbnail_webp else 0
                
                # Insertar imagen
                cursor.execute('''
                    INSERT OR REPLACE INTO imagenes (
                        nombre_original, nombre_renombrado, ruta_completa, ruta_salida,
                        tamano_bytes, ancho, alto, formato, hash_md5,
                        titulo, descripcion, caption, keywords,
                        caption_en, caption_es, keywords_en, keywords_es,
                        visual_attributes, objetos_detectados,
                        thumbnail_webp, thumbnail_size,
                        estado, modelo_ia_usado, fecha_procesamiento,
                        metadatos_exif, notas, etiquetas
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    imagen_path.name,
                    kwargs.get('nombre_renombrado'),
                    str(imagen_path),
                    kwargs.get('ruta_salida'),
                    metadatos['tamano_bytes'],
                    metadatos['ancho'],
                    metadatos['alto'],
                    metadatos['formato'],
                    metadatos.get('hash_md5'),
                    kwargs.get('titulo'),
                    normalized.get('descripcion'),
                    normalized.get('caption'),
                    keywords_json,
                    normalized.get('caption_en'),
                    normalized.get('caption_es'),
                    keywords_en_json,
                    keywords_es_json,
                    visual_attributes_json,
                    objetos_json,
                    thumbnail_webp,
                    thumbnail_size,
                    kwargs.get('estado', 'pending'),
                    kwargs.get('modelo_usado'),
                    kwargs.get('fecha_procesamiento'),
                    metadatos_exif_json,
                    kwargs.get('notes', kwargs.get('notas')),
                    etiquetas_json
                ))
                
                imagen_id = cursor.lastrowid
                
                # Fallback manual en caso de que los triggers no estén soportados
                if not getattr(self, '_has_sqlite_triggers', False):
                    self._update_fts5(cursor, imagen_id)
                
                # Registrar en historial
                self._registrar_historial(cursor, imagen_id, 'insercion', None, kwargs.get('estado', 'pending'))
                
                conn.commit()
                self.logger.info(f"Imagen insertada correctamente con thumbnail WebP: {imagen_path.name}")
                return True
                
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"La imagen ya existe en la base de datos: {imagen_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error al insertar imagen: {e}")
            return False

    def actualizar_campos_editables(self, imagen_id: int, data: Dict) -> bool:
        """Actualiza los campos editables por el usuario para un registro y actualiza FTS5."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                etiquetas_json = json.dumps(data.get('etiquetas', []), ensure_ascii=False)
                
                cursor.execute(
                    "UPDATE imagenes SET titulo = ?, descripcion = ?, etiquetas = ? WHERE id = ?",
                    (data.get('titulo'), data.get('descripcion'), etiquetas_json, imagen_id)
                )
                
                # Fallback manual en caso de que los triggers no estén soportados
                if not getattr(self, '_has_sqlite_triggers', False):
                    self._update_fts5(cursor, imagen_id)
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error actualizando campos editables para ID {imagen_id}: {e}")
            return False
            
    def buscar_imagenes_fts5(self, query: str, limite: int = 100) -> List[Dict]:
        """
        Búsqueda súper rápida usando FTS5
        
        Args:
            query: Término de búsqueda
            limite: Número máximo de resultados
            
        Returns:
            Lista de diccionarios con datos de imágenes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Búsqueda FTS5
                cursor.execute('''
                    SELECT i.*
                    FROM imagenes i
                    INNER JOIN imagenes_fts ON imagenes_fts.rowid = i.id
                    WHERE imagenes_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                ''', (query, limite))
                
                resultados = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                imagenes = []
                for row in resultados:
                    imagen = dict(row)
                    # Parsear JSON fields
                    try:
                        imagen['keywords'] = json.loads(imagen['keywords'] or '[]')
                        if 'keywords_en' in imagen:
                            imagen['keywords_en'] = json.loads(imagen['keywords_en'] or '[]')
                        if 'keywords_es' in imagen:
                            imagen['keywords_es'] = json.loads(imagen['keywords_es'] or '[]')
                        if 'visual_attributes' in imagen:
                            imagen['visual_attributes'] = json.loads(imagen['visual_attributes'] or '{}')
                        imagen['objetos_detectados'] = json.loads(imagen['objetos_detectados'] or '[]')
                        imagen['etiquetas'] = json.loads(imagen['etiquetas'] or '[]')
                        imagen['metadatos_exif'] = json.loads(imagen['metadatos_exif'] or '{}')
                    except json.JSONDecodeError:
                        pass
                    
                    # Asegurar compatibilidad con la clave 'file_path'
                    if 'ruta_completa' in imagen:
                        imagen['file_path'] = imagen['ruta_completa']
                    
                    imagenes.append(imagen)
                
                return imagenes
                
        except Exception as e:
            self.logger.error(f"Error en búsqueda FTS5: {e}")
            return []
            
    def obtener_thumbnail_webp(self, imagen_id: int) -> Optional[bytes]:
        """
        Obtener thumbnail WebP de una imagen
        
        Args:
            imagen_id: ID de la imagen
            
        Returns:
            Bytes del thumbnail WebP o None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT thumbnail_webp FROM imagenes WHERE id = ?", (imagen_id,))
                result = cursor.fetchone()
                return result[0] if result and result[0] else None
                
        except Exception as e:
            self.logger.error(f"Error obteniendo thumbnail WebP: {e}")
            return None

    def insertar_imagen_para_procesar(self, imagen_path: str) -> Optional[int]:
        """
        Inserta una entrada mínima para una imagen que se va a procesar,
        incluyendo thumbnail WebP para la galería web.
        """
        try:
            imagen_path_obj = Path(imagen_path)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                metadatos = self._obtener_metadatos_imagen(imagen_path_obj)
                thumbnail_webp = self._create_webp_thumbnail(str(imagen_path_obj))
                cursor.execute(
                    """
                    INSERT INTO imagenes (
                        nombre_original, ruta_completa, estado, tamano_bytes,
                        ancho, alto, formato, hash_md5, metadatos_exif,
                        thumbnail_webp, thumbnail_size
                    )
                    VALUES (?, ?, 'processing', ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        imagen_path_obj.name,
                        str(imagen_path_obj),
                        metadatos['tamano_bytes'],
                        metadatos['ancho'],
                        metadatos['alto'],
                        metadatos['formato'],
                        metadatos.get('hash_md5'),
                        json.dumps(metadatos.get('exif', {}), ensure_ascii=False),
                        thumbnail_webp,
                        len(thumbnail_webp) if thumbnail_webp else 0,
                    )
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            self.logger.warning(f"La imagen {imagen_path} ya existe, no se insertará de nuevo.")
            return None
        except Exception as e:
            self.logger.error(f"Error en inserción para procesar v2: {e}")
            return None
            
    def obtener_imagen_para_vista_ampliada(self, imagen_id: int) -> Optional[Dict]:
        """
        Obtener datos completos de una imagen para vista ampliada
        
        Args:
            imagen_id: ID de la imagen
            
        Returns:
            Diccionario con datos completos de la imagen
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM imagenes WHERE id = ?", (imagen_id,))
                row = cursor.fetchone()
                
                if row:
                    imagen = dict(row)
                    # Parsear JSON fields
                    try:
                        imagen['keywords'] = json.loads(imagen['keywords'] or '[]')
                        if 'keywords_en' in imagen:
                            imagen['keywords_en'] = json.loads(imagen['keywords_en'] or '[]')
                        if 'keywords_es' in imagen:
                            imagen['keywords_es'] = json.loads(imagen['keywords_es'] or '[]')
                        if 'visual_attributes' in imagen:
                            imagen['visual_attributes'] = json.loads(imagen['visual_attributes'] or '{}')
                        imagen['objetos_detectados'] = json.loads(imagen['objetos_detectados'] or '[]')
                        imagen['etiquetas'] = json.loads(imagen['etiquetas'] or '[]')
                        imagen['metadatos_exif'] = json.loads(imagen['metadatos_exif'] or '{}')
                    except json.JSONDecodeError:
                        pass
                    
                    # Asegurar compatibilidad
                    if 'ruta_completa' in imagen:
                        imagen['file_path'] = imagen['ruta_completa']
                    
                    return imagen
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error obteniendo imagen para vista ampliada: {e}")
            return None
            
    def buscar_imagenes_por_filtros(self, filtros: Dict = None, limite: int = 100) -> List[Dict]:
        """
        Búsqueda avanzada con filtros múltiples
        
        Args:
            filtros: Diccionario con filtros de búsqueda
            limite: Número máximo de resultados
            
        Returns:
            Lista de diccionarios con datos de imágenes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Construir consulta
                query = "SELECT * FROM imagenes WHERE 1=1"
                params = []
                
                if filtros:
                    if 'estado' in filtros:
                        query += " AND estado = ?"
                        params.append(filtros['estado'])
                    
                    if 'formato' in filtros:
                        query += " AND formato = ?"
                        params.append(filtros['formato'])
                    
                    if 'modelo_ia' in filtros:
                        query += " AND modelo_ia_usado = ?"
                        params.append(filtros['modelo_ia'])
                    
                    if 'fecha_desde' in filtros:
                        query += " AND fecha_procesamiento >= ?"
                        params.append(filtros['fecha_desde'])
                    
                    if 'fecha_hasta' in filtros:
                        query += " AND fecha_procesamiento <= ?"
                        params.append(filtros['fecha_hasta'])
                    
                    if 'tamano_min' in filtros:
                        query += " AND tamano_bytes >= ?"
                        params.append(filtros['tamano_min'])
                    
                    if 'tamano_max' in filtros:
                        query += " AND tamano_bytes <= ?"
                        params.append(filtros['tamano_max'])
                    
                    if 'tiene_thumbnail' in filtros:
                        if filtros['tiene_thumbnail']:
                            query += " AND thumbnail_webp IS NOT NULL"
                        else:
                            query += " AND thumbnail_webp IS NULL"
                
                query += " ORDER BY fecha_actualizacion DESC LIMIT ?"
                params.append(limite)
                
                cursor.execute(query, params)
                resultados = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                imagenes = []
                for row in resultados:
                    imagen = dict(row)
                    # Parsear JSON fields
                    try:
                        imagen['keywords'] = json.loads(imagen['keywords'] or '[]')
                        if 'keywords_en' in imagen:
                            imagen['keywords_en'] = json.loads(imagen['keywords_en'] or '[]')
                        if 'keywords_es' in imagen:
                            imagen['keywords_es'] = json.loads(imagen['keywords_es'] or '[]')
                        if 'visual_attributes' in imagen:
                            imagen['visual_attributes'] = json.loads(imagen['visual_attributes'] or '{}')
                        imagen['objetos_detectados'] = json.loads(imagen['objetos_detectados'] or '[]')
                        imagen['etiquetas'] = json.loads(imagen['etiquetas'] or '[]')
                        imagen['metadatos_exif'] = json.loads(imagen['metadatos_exif'] or '{}')
                    except json.JSONDecodeError:
                        pass
                    
                    # Asegurar compatibilidad
                    if 'ruta_completa' in imagen:
                        imagen['file_path'] = imagen['ruta_completa']
                    
                    imagenes.append(imagen)
                
                return imagenes
                
        except Exception as e:
            self.logger.error(f"Error en búsqueda por filtros: {e}")
            return []
            
    def obtener_estadisticas_galeria(self) -> Dict:
        """
        Obtener estadísticas específicas para la galería
        
        Returns:
            Diccionario con estadísticas de galería
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                estadisticas = {}
                
                # Estadísticas generales
                cursor.execute("SELECT COUNT(*) FROM imagenes")
                estadisticas['total_imagenes'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM imagenes WHERE thumbnail_webp IS NOT NULL")
                estadisticas['imagenes_con_thumbnail'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM imagenes WHERE estado = 'completed'")
                estadisticas['imagenes_procesadas'] = cursor.fetchone()[0]
                
                # Estadísticas de tamaño de thumbnails
                cursor.execute("SELECT AVG(thumbnail_size) FROM imagenes WHERE thumbnail_webp IS NOT NULL")
                avg_thumbnail_size = cursor.fetchone()[0]
                estadisticas['tamano_promedio_thumbnail'] = avg_thumbnail_size or 0
                
                # Estadísticas por formato
                cursor.execute("""
                    SELECT formato, COUNT(*) as cantidad 
                    FROM imagenes 
                    GROUP BY formato 
                    ORDER BY cantidad DESC
                """)
                estadisticas['por_formato'] = dict(cursor.fetchall())
                
                return estadisticas
                
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas de galería: {e}")
            return {}

# Función de utilidad para crear instancia
def crear_base_datos_v2(db_path: str = "stockprep_images.db") -> EnhancedDatabaseManagerV2:
    """
    Crear una nueva instancia del gestor de base de datos v2.0
    
    Args:
        db_path: Ruta al archivo de base de datos
        
    Returns:
        Instancia del gestor de base de datos v2.0
    """
    return EnhancedDatabaseManagerV2(db_path)

if __name__ == "__main__":
    # Ejemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # Crear gestor de base de datos v2.0
    db_manager = EnhancedDatabaseManagerV2("test_stockprep_v2.db")
    
    # Ejemplo de búsqueda FTS5
    imagenes = db_manager.buscar_imagenes_fts5("paisaje", limite=10)
    print(f"Encontradas {len(imagenes)} imágenes con búsqueda FTS5")
    
    # Ejemplo de estadísticas de galería
    stats = db_manager.obtener_estadisticas_galeria()
    print("Estadísticas de galería:")
    for clave, valor in stats.items():
        print(f"  {clave}: {valor}")
