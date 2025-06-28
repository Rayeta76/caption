"""
Gestor de base de datos SQLite para almacenar información de imágenes procesadas
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


class SQLiteImageDatabase:
    """Base de datos SQLite embebida para gestionar información de imágenes"""
    
    def __init__(self, db_path: str = "stockprep_images.db"):
        """
        Inicializa la base de datos SQLite
        
        Args:
            db_path: Ruta al archivo de base de datos
        """
        # Para :memory: usar string directamente, para archivos usar Path
        if db_path == ":memory:":
            self.db_path = db_path
        else:
            self.db_path = str(Path(db_path))
        self._create_tables()
    
    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla principal de imágenes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        caption TEXT,
                        keywords TEXT,
                        objects TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processed_at TIMESTAMP,
                        width INTEGER,
                        height INTEGER,
                        file_size INTEGER,
                        renamed_file TEXT,
                        error TEXT
                    )
                """)
                
                # Índices para búsquedas rápidas
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_file ON images(file)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at ON images(created_at)
                """)
                
                # Tabla de estadísticas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        total_images INTEGER DEFAULT 0,
                        successful INTEGER DEFAULT 0,
                        errors INTEGER DEFAULT 0,
                        avg_processing_time REAL,
                        total_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print(f"✅ Tablas creadas en {self.db_path}")
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            raise
    
    def guardar_imagen(self, **data: Any) -> int:
        """
        Guarda la información de una imagen procesada
        
        Args:
            **data: Datos de la imagen (file, caption, keywords, objects, etc.)
            
        Returns:
            ID del registro insertado
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convertir listas/diccionarios a JSON
                if 'keywords' in data and isinstance(data['keywords'], list):
                    data['keywords'] = json.dumps(data['keywords'], ensure_ascii=False)
                
                if 'objects' in data and isinstance(data['objects'], dict):
                    data['objects'] = json.dumps(data['objects'], ensure_ascii=False)
                
                # Agregar timestamp de procesamiento
                data['processed_at'] = datetime.now().isoformat()
                
                # Campos permitidos
                allowed_fields = [
                    'file', 'file_path', 'caption', 'keywords', 'objects',
                    'processed_at', 'width', 'height', 'file_size', 
                    'renamed_file', 'error'
                ]
                
                # Filtrar solo campos permitidos
                filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                
                # Construir consulta dinámicamente
                fields = ', '.join(filtered_data.keys())
                placeholders = ', '.join(['?' for _ in filtered_data])
                values = list(filtered_data.values())
                
                cursor.execute(
                    f"INSERT INTO images ({fields}) VALUES ({placeholders})",
                    values
                )
                
                return cursor.lastrowid or 0
        except Exception as e:
            print(f"❌ Error guardando imagen: {e}")
            return 0
    
    def obtener_imagen(self, image_id: int) -> Optional[Dict]:
        """
        Obtiene la información de una imagen por ID
        
        Args:
            image_id: ID de la imagen
            
        Returns:
            Diccionario con los datos o None si no existe
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM images WHERE id = ?", (image_id,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                # Convertir JSON strings de vuelta a objetos
                if data.get('keywords'):
                    try:
                        data['keywords'] = json.loads(data['keywords'])
                    except:
                        pass
                if data.get('objects'):
                    try:
                        data['objects'] = json.loads(data['objects'])
                    except:
                        pass
                return data
            
            return None
    
    def buscar_imagenes(self, **criterios) -> List[Dict]:
        """
        Busca imágenes según criterios
        
        Args:
            **criterios: Criterios de búsqueda (file, caption contiene texto, etc.)
            
        Returns:
            Lista de imágenes que coinciden
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM images WHERE 1=1"
                params = []
                
                if 'file' in criterios:
                    query += " AND file LIKE ?"
                    params.append(f"%{criterios['file']}%")
                
                if 'caption_contains' in criterios:
                    query += " AND caption LIKE ?"
                    params.append(f"%{criterios['caption_contains']}%")
                
                if 'keywords_contains' in criterios:
                    query += " AND keywords LIKE ?"
                    params.append(f"%{criterios['keywords_contains']}%")
                
                if 'from_date' in criterios:
                    query += " AND created_at >= ?"
                    params.append(criterios['from_date'])
                
                if 'to_date' in criterios:
                    query += " AND created_at <= ?"
                    params.append(criterios['to_date'])
                
                query += " ORDER BY created_at DESC"
                
                if 'limit' in criterios:
                    query += f" LIMIT {int(criterios['limit'])}"
                
                cursor.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    data = dict(row)
                    # Convertir JSON strings
                    if data.get('keywords'):
                        try:
                            data['keywords'] = json.loads(data['keywords'])
                        except:
                            pass
                    if data.get('objects'):
                        try:
                            data['objects'] = json.loads(data['objects'])
                        except:
                            pass
                    results.append(data)
                
                return results
        except Exception as e:
            print(f"❌ Error buscando imágenes: {e}")
            return []
    
    def obtener_estadisticas_globales(self) -> Dict:
        """
        Obtiene estadísticas globales de todas las sesiones
        
        Returns:
            Diccionario con estadísticas agregadas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de imágenes procesadas
                cursor.execute("SELECT COUNT(*) FROM images WHERE error IS NULL")
                total_procesadas = cursor.fetchone()[0]
                
                # Total de errores
                cursor.execute("SELECT COUNT(*) FROM images WHERE error IS NOT NULL")
                total_errores = cursor.fetchone()[0]
                
                return {
                    'total_imagenes_procesadas': total_procesadas,
                    'total_errores': total_errores,
                    'total_sesiones': 0,
                    'total_imagenes_sesiones': 0,
                    'tiempo_promedio_imagen': 0.0,
                    'tiempo_total_procesamiento': 0.0
                }
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {
                'total_imagenes_procesadas': 0,
                'total_errores': 0,
                'total_sesiones': 0,
                'total_imagenes_sesiones': 0,
                'tiempo_promedio_imagen': 0.0,
                'tiempo_total_procesamiento': 0.0
            }
    
    def cerrar(self):
        """Cierra la conexión (no necesario con context managers, pero útil para limpieza)"""
        pass  # SQLite se cierra automáticamente con context managers 