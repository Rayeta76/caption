"# Enhanced Database Manager" 

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from PIL import Image

class EnhancedDatabaseManager:
    """
    Sistema avanzado de gestión de base de datos SQLite para StockPrep Pro v2.0
    
    Funcionalidades:
    - Gestión completa de metadatos de imágenes
    - Tracking de procesamiento IA (Florence-2)
    - Estados de procesamiento
    - Búsquedas avanzadas con índices
    - Inserción automática desde archivos TXT
    - Inserción manual de imágenes
    - Estadísticas y reportes
    """
    
    def __init__(self, db_path: str = "stockprep_images.db"):
        """
        Inicializar el gestor de base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Inicializar la base de datos y crear tablas si no existen"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Crear tabla principal de imágenes
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS imagenes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_original TEXT NOT NULL,
                        nombre_renombrado TEXT,
                        ruta_completa TEXT NOT NULL UNIQUE,
                        ruta_relativa TEXT,
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
                
                # Crear índices para búsquedas eficientes
                indices = [
                    "CREATE INDEX IF NOT EXISTS idx_nombre_original ON imagenes(nombre_original)",
                    "CREATE INDEX IF NOT EXISTS idx_estado ON imagenes(estado)",
                    "CREATE INDEX IF NOT EXISTS idx_fecha_procesamiento ON imagenes(fecha_procesamiento)",
                    "CREATE INDEX IF NOT EXISTS idx_modelo_ia ON imagenes(modelo_ia_usado)",
                    "CREATE INDEX IF NOT EXISTS idx_ruta_completa ON imagenes(ruta_completa)",
                    "CREATE INDEX IF NOT EXISTS idx_formato ON imagenes(formato)",
                    "CREATE INDEX IF NOT EXISTS idx_tamano ON imagenes(tamano_bytes)",
                    "CREATE INDEX IF NOT EXISTS idx_historial_imagen ON historial_procesamiento(imagen_id)",
                    "CREATE INDEX IF NOT EXISTS idx_historial_timestamp ON historial_procesamiento(timestamp)"
                ]
                
                for indice in indices:
                    cursor.execute(indice)
                
                conn.commit()
                self.logger.info(f"Base de datos inicializada correctamente: {self.db_path}")
                
        except Exception as e:
            self.logger.error(f"Error al inicializar la base de datos: {e}")
            raise
    
    def insertar_imagen_automatica(self, imagen_path: str, output_dir: str = None) -> bool:
        """
        Insertar imagen con procesamiento automático desde archivos TXT
        
        Busca automáticamente los archivos:
        - nombre_base_caption.txt
        - nombre_base_keywords.txt  
        - nombre_base_objects.txt
        
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
                estado=estado,
                modelo_usado=modelo_usado,
                fecha_procesamiento=fecha_procesamiento
            )
            
        except Exception as e:
            self.logger.error(f"Error en inserción automática: {e}")
            return False
    
    def insertar_imagen_manual(self, imagen_path: str, **kwargs) -> bool:
        """
        Insertar imagen manualmente con datos opcionales
        
        Args:
            imagen_path: Ruta a la imagen
            **kwargs: Datos opcionales (titulo, descripcion, caption, keywords, etc.)
            
        Returns:
            bool: True si se insertó correctamente
        """
        try:
            imagen_path = Path(imagen_path)
            if not imagen_path.exists():
                self.logger.error(f"La imagen no existe: {imagen_path}")
                return False
            
            # Obtener metadatos de la imagen
            metadatos = self._obtener_metadatos_imagen(imagen_path)
            
            # Extraer datos opcionales
            caption = kwargs.get('caption')
            keywords = kwargs.get('keywords', [])
            objetos = kwargs.get('objetos', [])
            titulo = kwargs.get('titulo')
            descripcion = kwargs.get('descripcion')
            estado = kwargs.get('estado', 'pending')
            modelo_usado = kwargs.get('modelo_usado')
            notas = kwargs.get('notas')
            etiquetas = kwargs.get('etiquetas', [])
            
            return self._insertar_imagen_db(
                imagen_path=str(imagen_path),
                metadatos=metadatos,
                caption=caption,
                keywords=keywords,
                objetos=objetos,
                titulo=titulo,
                descripcion=descripcion,
                estado=estado,
                modelo_usado=modelo_usado,
                notas=notas,
                etiquetas=etiquetas
            )
            
        except Exception as e:
            self.logger.error(f"Error en inserción manual: {e}")
            return False
    
    def _insertar_imagen_db(self, imagen_path: str, metadatos: Dict, **kwargs) -> bool:
        """Insertar imagen en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Preparar datos
                imagen_path = Path(imagen_path)
                keywords_json = json.dumps(kwargs.get('keywords', []), ensure_ascii=False)
                objetos_json = json.dumps(kwargs.get('objetos', []), ensure_ascii=False)
                etiquetas_json = json.dumps(kwargs.get('etiquetas', []), ensure_ascii=False)
                metadatos_exif_json = json.dumps(metadatos.get('exif', {}), ensure_ascii=False)
                
                # Insertar imagen
                cursor.execute('''
                    INSERT OR REPLACE INTO imagenes (
                        nombre_original, ruta_completa, ruta_relativa,
                        tamano_bytes, ancho, alto, formato, hash_md5,
                        titulo, descripcion, caption, keywords, objetos_detectados,
                        estado, modelo_ia_usado, fecha_procesamiento,
                        metadatos_exif, notas, etiquetas
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    imagen_path.name,
                    str(imagen_path),
                    str(imagen_path.relative_to(Path.cwd())) if imagen_path.is_relative_to(Path.cwd()) else str(imagen_path),
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
                    kwargs.get('estado', 'pending'),
                    kwargs.get('modelo_usado'),
                    kwargs.get('fecha_procesamiento'),
                    metadatos_exif_json,
                    kwargs.get('notas'),
                    etiquetas_json
                ))
                
                imagen_id = cursor.lastrowid
                
                # Registrar en historial
                self._registrar_historial(cursor, imagen_id, 'insercion', None, kwargs.get('estado', 'pending'))
                
                conn.commit()
                self.logger.info(f"Imagen insertada correctamente: {imagen_path.name}")
                return True
                
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"La imagen ya existe en la base de datos: {imagen_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error al insertar imagen: {e}")
            return False
    
    def actualizar_procesamiento_ia(self, imagen_id: int, caption: str = None, 
                                  keywords: List[str] = None, objetos: List[Dict] = None,
                                  modelo_usado: str = "Florence-2", confianza: float = None) -> bool:
        """
        Actualizar imagen con resultados de procesamiento IA
        
        Args:
            imagen_id: ID de la imagen en la base de datos
            caption: Caption generado
            keywords: Lista de keywords
            objetos: Lista de objetos detectados con posiciones
            modelo_usado: Nombre del modelo IA usado
            confianza: Confianza promedio del procesamiento
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener estado actual
                cursor.execute("SELECT estado FROM imagenes WHERE id = ?", (imagen_id,))
                resultado = cursor.fetchone()
                if not resultado:
                    self.logger.error(f"No se encontró imagen con ID: {imagen_id}")
                    return False
                
                estado_anterior = resultado[0]
                
                # Preparar datos
                keywords_json = json.dumps(keywords or [], ensure_ascii=False)
                objetos_json = json.dumps(objetos or [], ensure_ascii=False)
                
                # Actualizar imagen
                cursor.execute('''
                    UPDATE imagenes SET
                        caption = COALESCE(?, caption),
                        keywords = COALESCE(?, keywords),
                        objetos_detectados = COALESCE(?, objetos_detectados),
                        estado = 'completed',
                        modelo_ia_usado = ?,
                        confianza_promedio = COALESCE(?, confianza_promedio),
                        fecha_procesamiento = CURRENT_TIMESTAMP,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (caption, keywords_json, objetos_json, modelo_usado, confianza, imagen_id))
                
                # Registrar en historial
                self._registrar_historial(cursor, imagen_id, 'procesamiento_ia', estado_anterior, 'completed')
                
                conn.commit()
                self.logger.info(f"Procesamiento IA actualizado para imagen ID: {imagen_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error al actualizar procesamiento IA: {e}")
            return False
    
    def buscar_imagenes(self, filtros: Dict = None, limite: int = 100) -> List[Dict]:
        """
        Buscar imágenes con filtros avanzados
        
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
                    
                    if 'keyword' in filtros:
                        query += " AND keywords LIKE ?"
                        params.append(f"%{filtros['keyword']}%")
                    
                    if 'tamano_min' in filtros:
                        query += " AND tamano_bytes >= ?"
                        params.append(filtros['tamano_min'])
                    
                    if 'tamano_max' in filtros:
                        query += " AND tamano_bytes <= ?"
                        params.append(filtros['tamano_max'])
                
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
                    
                    # --- FIX: Asegurar compatibilidad con la clave 'file_path' esperada por la GUI ---
                    if 'ruta_completa' in imagen:
                        imagen['file_path'] = imagen['ruta_completa']

                    imagenes.append(imagen)
                
                return imagenes
                
        except Exception as e:
            self.logger.error(f"Error en búsqueda de imágenes: {e}")
            return []
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtener estadísticas completas de la base de datos
        
        Returns:
            Diccionario con estadísticas detalladas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                estadisticas = {}
                
                # Estadísticas generales
                cursor.execute("SELECT COUNT(*) FROM imagenes")
                estadisticas['total_imagenes'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM imagenes WHERE estado = 'completed'")
                estadisticas['imagenes_procesadas'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM imagenes WHERE estado = 'pending'")
                estadisticas['imagenes_pendientes'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM imagenes WHERE estado = 'error'")
                estadisticas['imagenes_error'] = cursor.fetchone()[0]
                
                # Estadísticas por formato
                cursor.execute("""
                    SELECT formato, COUNT(*) as cantidad 
                    FROM imagenes 
                    GROUP BY formato 
                    ORDER BY cantidad DESC
                """)
                estadisticas['por_formato'] = dict(cursor.fetchall())
                
                # Estadísticas por modelo IA
                cursor.execute("""
                    SELECT modelo_ia_usado, COUNT(*) as cantidad 
                    FROM imagenes 
                    WHERE modelo_ia_usado IS NOT NULL
                    GROUP BY modelo_ia_usado 
                    ORDER BY cantidad DESC
                """)
                estadisticas['por_modelo_ia'] = dict(cursor.fetchall())
                
                # Estadísticas de tamaño
                cursor.execute("""
                    SELECT 
                        AVG(tamano_bytes) as promedio,
                        MIN(tamano_bytes) as minimo,
                        MAX(tamano_bytes) as maximo,
                        SUM(tamano_bytes) as total
                    FROM imagenes
                """)
                resultado = cursor.fetchone()
                estadisticas['tamano'] = {
                    'promedio_bytes': resultado[0] or 0,
                    'minimo_bytes': resultado[1] or 0,
                    'maximo_bytes': resultado[2] or 0,
                    'total_bytes': resultado[3] or 0
                }
                
                # Estadísticas de procesamiento reciente (últimos 7 días)
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM imagenes 
                    WHERE fecha_procesamiento >= date('now', '-7 days')
                """)
                estadisticas['procesadas_ultima_semana'] = cursor.fetchone()[0]
                
                return estadisticas
                
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    def exportar_datos(self, formato: str = 'json', filtros: Dict = None) -> str:
        """
        Exportar datos de imágenes en formato especificado
        
        Args:
            formato: 'json' o 'csv'
            filtros: Filtros de búsqueda opcionales
            
        Returns:
            Ruta del archivo exportado
        """
        try:
            imagenes = self.buscar_imagenes(filtros, limite=10000)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if formato.lower() == 'json':
                archivo_salida = f"export_imagenes_{timestamp}.json"
                with open(archivo_salida, 'w', encoding='utf-8') as f:
                    json.dump(imagenes, f, ensure_ascii=False, indent=2, default=str)
            
            elif formato.lower() == 'csv':
                import csv
                archivo_salida = f"export_imagenes_{timestamp}.csv"
                
                if imagenes:
                    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=imagenes[0].keys())
                        writer.writeheader()
                        for imagen in imagenes:
                            # Convertir listas/dicts a strings para CSV
                            row = {}
                            for k, v in imagen.items():
                                if isinstance(v, (list, dict)):
                                    row[k] = json.dumps(v, ensure_ascii=False)
                                else:
                                    row[k] = v
                            writer.writerow(row)
            
            else:
                raise ValueError(f"Formato no soportado: {formato}")
            
            self.logger.info(f"Datos exportados a: {archivo_salida}")
            return archivo_salida
            
        except Exception as e:
            self.logger.error(f"Error al exportar datos: {e}")
            return ""
    
    def limpiar_registros_antiguos(self, dias: int = 30) -> int:
        """
        Limpiar registros antiguos del historial
        
        Args:
            dias: Número de días de antigüedad para limpiar
            
        Returns:
            Número de registros eliminados
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM historial_procesamiento 
                    WHERE timestamp < date('now', '-{} days')
                """.format(dias))
                
                eliminados = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"Eliminados {eliminados} registros antiguos del historial")
                return eliminados
                
        except Exception as e:
            self.logger.error(f"Error al limpiar registros antiguos: {e}")
            return 0
    
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
        # SQLite se maneja con context managers, no necesita cierre explícito
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar_conexion()


# Funciones de utilidad para integración fácil
def crear_base_datos(db_path: str = "stockprep_images.db") -> EnhancedDatabaseManager:
    """
    Crear una nueva instancia del gestor de base de datos
    
    Args:
        db_path: Ruta al archivo de base de datos
        
    Returns:
        Instancia del gestor de base de datos
    """
    return EnhancedDatabaseManager(db_path)

def procesar_directorio_imagenes(directorio: str, output_dir: str = None, 
                                db_path: str = "stockprep_images.db") -> Dict:
    """
    Procesar todas las imágenes de un directorio y agregarlas a la base de datos
    
    Args:
        directorio: Directorio con imágenes
        output_dir: Directorio con archivos de procesamiento TXT
        db_path: Ruta a la base de datos
        
    Returns:
        Diccionario con estadísticas del procesamiento
    """
    directorio = Path(directorio)
    if not directorio.exists():
        raise ValueError(f"El directorio no existe: {directorio}")
    
    # Extensiones de imagen soportadas
    extensiones_imagen = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
    
    # Encontrar todas las imágenes
    imagenes = []
    for ext in extensiones_imagen:
        imagenes.extend(directorio.glob(f"*{ext}"))
        imagenes.extend(directorio.glob(f"*{ext.upper()}"))
    
    # Procesar imágenes
    db_manager = EnhancedDatabaseManager(db_path)
    
    estadisticas = {
        'total_encontradas': len(imagenes),
        'insertadas_exitosamente': 0,
        'ya_existian': 0,
        'errores': 0
    }
    
    for imagen_path in imagenes:
        try:
            if db_manager.insertar_imagen_automatica(str(imagen_path), output_dir):
                estadisticas['insertadas_exitosamente'] += 1
            else:
                estadisticas['ya_existian'] += 1
        except Exception as e:
            logging.error(f"Error procesando {imagen_path}: {e}")
            estadisticas['errores'] += 1
    
    return estadisticas


if __name__ == "__main__":
    # Ejemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # Crear gestor de base de datos
    db_manager = EnhancedDatabaseManager("test_stockprep.db")
    
    # Ejemplo de inserción manual
    # db_manager.insertar_imagen_manual(
    #     "ruta/a/imagen.jpg",
    #     titulo="Imagen de prueba",
    #     descripcion="Una imagen de ejemplo",
    #     keywords=["prueba", "ejemplo", "test"],
    #     estado="completed"
    # )
    
    # Ejemplo de búsqueda
    imagenes = db_manager.buscar_imagenes({'estado': 'completed'}, limite=10)
    print(f"Encontradas {len(imagenes)} imágenes completadas")
    
    # Ejemplo de estadísticas
    stats = db_manager.obtener_estadisticas()
    print("Estadísticas de la base de datos:")
    for clave, valor in stats.items():
        print(f"  {clave}: {valor}") 
