#!/usr/bin/env python3
"""
Script para corregir el archivo SQLite
"""

# Leer el archivo actual
with open('src/core/sqlite_database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar el método problemático
old_method = '''    def _create_tables(self):
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
        except Exception as e:
            print(f"Error creando tablas: {e}")
            raise'''

new_method = '''    def _create_tables(self):
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
        except Exception as e:
            print(f"Error creando tablas: {e}")
            raise'''

# Reemplazar en el contenido
content = content.replace(old_method, new_method)

# Escribir el archivo corregido
with open('src/core/sqlite_database.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo SQLite corregido") 