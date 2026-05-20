"""
Enhanced Database Manager v2.0 - Con FTS5 y WebP Thumbnails
StockPrep Pro v2.0 - Optimizado para galería tipo web de stock

Mejoras implementadas:
- Búsqueda FTS5 para búsquedas súper rápidas
- Thumbnails WebP en BLOB para rendimiento óptimo
- Vista ampliada y navegación mejorada
- Experiencia tipo web de stock
"""

import sqlite3
import os
import json
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from PIL import Image, ImageOps

class EnhancedDatabaseManagerV2:
    """
    Sistema avanzado de gestión de base de datos SQLite con FTS5 y WebP
    Optimizado para galería tipo web de stock
    
    Funcionalidades:
    - Búsqueda FTS5 instantánea
    - Thumbnails WebP en BLOB
    - Vista ampliada de imágenes
    - Navegación intuitiva
    - Experiencia tipo web de stock
    """
    
    def __init__(self, db_path: str = "stockprep_images.db"):
        """
        Inicializar el gestor de base de datos v2.0
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Inicializar la base de datos con FTS5 y soporte WebP"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Habilitar FTS5
                cursor.execute("PRAGMA compile_options")
                compile_options = [row[0] for row in cursor.fetchall()]
                if 'ENABLE_FTS5' not in compile_options:
                    self.logger.warning("FTS5 no está habilitado en esta compilación de SQLite")
                
                # Crear tabla principal de imágenes (mejorada)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS imagenes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_original TEXT NOT NULL,
                        nombre_renombrado TEXT,
                        ruta_completa TEXT NOT NULL UNIQUE,
                        ruta_salida TEXT,
                        tamano_bytes INTEGER,
                        ancho INTEGER,
                        alto INTEGER,
                        formato TEXT,
                        hash_md5 TEXT,
                        
                        -- Contenido procesado por IA
                        titulo TEXT,
                        descripcion TEXT,
                        caption TEXT,
                        keywords TEXT, -- JSON array
                        objetos_detectados TEXT, -- JSON array con posiciones
                        
                        -- Thumbnails WebP en BLOB
                        thumbnail_webp BLOB, -- Thumbnail WebP comprimido
                        thumbnail_size INTEGER, -- Tamaño del thumbnail en bytes
                        
                        -- Estados y tracking
                        estado TEXT DEFAULT 'pending', -- pending/processing/completed/error
                        modelo_ia_usado TEXT,
                        version_modelo TEXT,
                        confianza_promedio REAL,
                        
                        -- Timestamps
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_procesamiento TIMESTAMP,
                        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                        -- Metadatos adicionales
                        metadatos_exif TEXT, -- JSON
                        notas TEXT,
                        etiquetas TEXT -- JSON array para categorización manual
                    )
                ''')
                
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
                
                # Crear tabla de historial de procesamiento
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS historial_procesamiento (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        imagen_id INTEGER,
                        accion TEXT NOT NULL,
                        estado_anterior TEXT,
                        estado_nuevo TEXT,
                        detalles TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (imagen_id) REFERENCES imagenes (id)
                    )
                ''')
                
                # Crear tabla de estadísticas de procesamiento
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
                
                # Crear índices optimizados para galería
                indices = [
                    "CREATE INDEX IF NOT EXISTS idx_nombre_original ON imagenes(nombre_original)",
                    "CREATE INDEX IF NOT EXISTS idx_estado ON imagenes(estado)",
                    "CREATE INDEX IF NOT EXISTS idx_fecha_procesamiento ON imagenes(fecha_procesamiento)",
                    "CREATE INDEX IF NOT EXISTS idx_modelo_ia ON imagenes(modelo_ia_usado)",
                    "CREATE INDEX IF NOT EXISTS idx_ruta_completa ON imagenes(ruta_completa)",
                    "CREATE INDEX IF NOT EXISTS idx_formato ON imagenes(formato)",
                    "CREATE INDEX IF NOT EXISTS idx_tamano ON imagenes(tamano_bytes)",
                    "CREATE INDEX IF NOT EXISTS idx_thumbnail_size ON imagenes(thumbnail_size)",
                    "CREATE INDEX IF NOT EXISTS idx_historial_imagen ON historial_procesamiento(imagen_id)",
                    "CREATE INDEX IF NOT EXISTS idx_historial_timestamp ON historial_procesamiento(timestamp)"
                ]
                
                for indice in indices:
                    cursor.execute(indice)
                
                self._ensure_schema_columns(cursor)
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
        }
        for columna, tipo in nuevas.items():
            if columna not in columnas:
                cursor.execute(f"ALTER TABLE imagenes ADD COLUMN {columna} {tipo}")

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
                                
                                # Actualizar FTS5
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
        """Actualizar índice FTS5 para una imagen"""
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
                    INSERT INTO imagenes_fts(
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
            keywords_file = output_dir / f"{nombre_base}_keywords.txt"
            objects_file = output_dir / f"{nombre_base}_objects.txt"
            
            # Leer contenido de archivos
            caption = self._leer_archivo_txt(caption_file) if caption_file.exists() else None
            keywords = self._leer_keywords_txt(keywords_file) if keywords_file.exists() else []
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
                keywords=keywords,
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
                keywords_json = json.dumps(kwargs.get('keywords', []), ensure_ascii=False)
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
                        titulo, descripcion, caption, keywords, objetos_detectados,
                        thumbnail_webp, thumbnail_size,
                        estado, modelo_ia_usado, fecha_procesamiento,
                        metadatos_exif, notas, etiquetas
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    kwargs.get('descripcion'),
                    kwargs.get('caption'),
                    keywords_json,
                    objetos_json,
                    thumbnail_webp,
                    thumbnail_size,
                    kwargs.get('estado', 'pending'),
                    kwargs.get('modelo_usado'),
                    kwargs.get('fecha_procesamiento'),
                    metadatos_exif_json,
                    kwargs.get('notas'),
                    etiquetas_json
                ))
                
                imagen_id = cursor.lastrowid
                
                # Actualizar FTS5
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
                    SELECT i.*, fts.rank AS rank
                    FROM imagenes_fts fts
                    JOIN imagenes i ON i.id = fts.rowid
                    WHERE fts MATCH ?
                    ORDER BY fts.rank
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
    
    # Métodos auxiliares (reutilizados del manager original)
    def _obtener_metadatos_imagen(self, imagen_path: Path) -> Dict:
        """Obtener metadatos completos de una imagen"""
        try:
            metadatos = {
                'tamano_bytes': imagen_path.stat().st_size,
                'formato': imagen_path.suffix.lower().replace('.', ''),
                'hash_md5': None,
                'ancho': 0,
                'alto': 0,
                'exif': {}
            }
            
            # Obtener dimensiones con PIL
            try:
                with Image.open(imagen_path) as img:
                    metadatos['ancho'] = img.width
                    metadatos['alto'] = img.height
                    
                    # Obtener datos EXIF si existen
                    if hasattr(img, '_getexif') and img._getexif():
                        metadatos['exif'] = dict(img._getexif())
            except Exception as e:
                self.logger.warning(f"No se pudieron obtener dimensiones de {imagen_path}: {e}")
            
            # Calcular hash MD5 si es necesario
            try:
                import hashlib
                with open(imagen_path, 'rb') as f:
                    metadatos['hash_md5'] = hashlib.md5(f.read()).hexdigest()
            except Exception as e:
                self.logger.warning(f"No se pudo calcular hash MD5 de {imagen_path}: {e}")
            
            return metadatos
            
        except Exception as e:
            self.logger.error(f"Error al obtener metadatos de {imagen_path}: {e}")
            return {
                'tamano_bytes': 0,
                'formato': '',
                'hash_md5': None,
                'ancho': 0,
                'alto': 0,
                'exif': {}
            }
    
    def _leer_archivo_txt(self, archivo_path: Path) -> Optional[str]:
        """Leer contenido de archivo de texto"""
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
                return contenido if contenido else None
        except Exception as e:
            self.logger.warning(f"No se pudo leer {archivo_path}: {e}")
            return None
    
    def _leer_keywords_txt(self, archivo_path: Path) -> List[str]:
        """Leer keywords desde archivo de texto (una por línea)"""
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f.readlines() if line.strip()]
                return keywords
        except Exception as e:
            self.logger.warning(f"No se pudieron leer keywords de {archivo_path}: {e}")
            return []
    
    def _leer_objects_txt(self, archivo_path: Path) -> List[Dict]:
        """Leer objetos detectados desde archivo de texto"""
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
                
                # Intentar parsear como JSON primero
                try:
                    objetos = json.loads(contenido)
                    if isinstance(objetos, list):
                        return objetos
                except json.JSONDecodeError:
                    pass
                
                # Si no es JSON, parsear línea por línea
                objetos = []
                for line in contenido.split('\n'):
                    line = line.strip()
                    if line:
                        # Formato esperado: "objeto: x1,y1,x2,y2" o solo "objeto"
                        if ':' in line:
                            nombre, coords = line.split(':', 1)
                            coords = coords.strip()
                            try:
                                coords_list = [float(x.strip()) for x in coords.split(',')]
                                if len(coords_list) == 4:
                                    objetos.append({
                                        'nombre': nombre.strip(),
                                        'bbox': coords_list,
                                        'confianza': 1.0
                                    })
                                else:
                                    objetos.append({'nombre': nombre.strip()})
                            except ValueError:
                                objetos.append({'nombre': nombre.strip()})
                        else:
                            objetos.append({'nombre': line})
                
                return objetos
                
        except Exception as e:
            self.logger.warning(f"No se pudieron leer objetos de {archivo_path}: {e}")
            return []
    
    def _registrar_historial(self, cursor, imagen_id: int, accion: str, 
                           estado_anterior: str, estado_nuevo: str, detalles: str = None):
        """Registrar acción en el historial"""
        try:
            cursor.execute('''
                INSERT INTO historial_procesamiento 
                (imagen_id, accion, estado_anterior, estado_nuevo, detalles)
                VALUES (?, ?, ?, ?, ?)
            ''', (imagen_id, accion, estado_anterior, estado_nuevo, detalles))
        except Exception as e:
            self.logger.warning(f"Error al registrar historial: {e}")
    
    def cerrar_conexion(self):
        """Cerrar conexión a la base de datos"""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar_conexion()


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

