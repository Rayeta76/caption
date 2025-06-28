# 🚀 StockPrep Pro v2.0 - Estructura Modular

## 📋 Descripción General

StockPrep Pro v2.0 ahora cuenta con una **arquitectura modular** que separa las funcionalidades principales en módulos independientes, proporcionando una experiencia de usuario más organizada y profesional.

## 🏗️ Nueva Estructura

### 🎯 **GUI de Inicio (Centro de Control)**
- **Archivo**: `src/gui/inicio_gui.py`
- **Función**: Punto de entrada principal con menú de navegación
- **Características**:
  - Tarjetas visuales para cada módulo
  - Estadísticas del sistema en tiempo real
  - Navegación intuitiva entre módulos
  - Información de estado del modelo y base de datos

### 🖼️ **Módulo de Reconocimiento de Imágenes**
- **Archivos**: 
  - `src/gui/modern_gui_stockprep.py` (Tkinter)
  - `src/gui/modern_gui_win11.py` (PySide6)
- **Función**: Procesamiento de imágenes con IA
- **Características**:
  - Procesamiento individual y en lote
  - Generación de captions con Florence-2
  - Detección de objetos
  - Extracción de keywords con YAKE
  - Exportación en múltiples formatos

### 🗄️ **Módulo de Gestión de Base de Datos**
- **Archivo**: `src/gui/database_gui.py`
- **Función**: Administración completa de la base de datos
- **Características**:
  - Explorador de registros con paginación
  - Búsqueda avanzada por múltiples criterios
  - Estadísticas detalladas del sistema
  - Herramientas de mantenimiento
  - Exportación e importación de datos

## 🚀 Cómo Usar la Nueva Estructura

### 1. **Inicio de la Aplicación**
```bash
python main.py
```

Al ejecutar, se abre la **GUI de Inicio** con dos opciones principales:

### 2. **Reconocimiento de Imágenes** 🖼️
- Haz clic en "🚀 Abrir Reconocimiento de Imágenes"
- Funcionalidad completa para procesar imágenes
- Al cerrar, regresa automáticamente al menú principal

### 3. **Gestión de Base de Datos** 🗄️
- Haz clic en "🗄️ Abrir Gestión de Base de Datos"
- Interfaz dedicada para administrar datos
- Al cerrar, regresa automáticamente al menú principal

## 📊 Funcionalidades de la GUI de Inicio

### **Panel de Estadísticas**
- **Imágenes Procesadas**: Contador total
- **Tamaño Base de Datos**: Espacio ocupado
- **Última Actividad**: Timestamp de última operación
- **Estado del Modelo**: Si Florence-2 está cargado

### **Tarjetas de Módulos**
Cada módulo tiene su propia tarjeta con:
- **Descripción detallada** de funcionalidades
- **Botón principal** para acceder al módulo
- **Botón secundario** para funciones rápidas

## 🔧 Funcionalidades del Módulo de Base de Datos

### **Tab 1: Explorador de Registros** 🗂️
- **Tabla paginada** con todos los registros
- **Filtros rápidos** por archivo, fecha y contenido
- **Navegación por páginas** (50 registros por página)
- **Vista de detalles** completos por registro
- **Menú contextual** con opciones de acción

### **Tab 2: Búsqueda Avanzada** 🔍
- **Criterios múltiples** de búsqueda
- **Filtros por fecha** y tipo de archivo
- **Búsqueda en contenido** y keywords
- **Resultados detallados** con exportación

### **Tab 3: Estadísticas** 📊
- **Métricas del sistema** actualizadas
- **Gráficos de actividad** (en desarrollo)
- **Información de rendimiento**
- **Análisis de uso**

### **Tab 4: Mantenimiento** 🔧
- **Compactación** de base de datos
- **Verificación de integridad**
- **Limpieza de registros** huérfanos
- **Copias de seguridad**
- **Log de actividades** de mantenimiento

## 🎨 Diseño y Experiencia de Usuario

### **Consistencia Visual**
- **Iconos uniformes** en toda la aplicación
- **Colores coherentes** (azul principal #0078D4, verde éxito #3CB371)
- **Tipografía moderna** (Segoe UI)
- **Estilos Windows 11** en ambas interfaces

### **Navegación Intuitiva**
- **Flujo natural** entre módulos
- **Regreso automático** al menú principal
- **Estados visuales** claros (cargado/no cargado)
- **Feedback inmediato** en todas las acciones

### **Responsive y Adaptable**
- **Ventanas redimensionables** con tamaños mínimos
- **Layouts flexibles** que se adaptan al contenido
- **Paginación inteligente** para grandes volúmenes de datos

## 📁 Estructura de Archivos

```
StockPrep Pro v2.0/
├── main.py                          # Punto de entrada principal
├── stockprep_icon.ico              # Icono de la aplicación
├── stockprep_icon.png              # Icono alternativo
├── src/
│   ├── gui/
│   │   ├── inicio_gui.py           # GUI de inicio (Centro de Control)
│   │   ├── modern_gui_stockprep.py # Módulo reconocimiento (Tkinter)
│   │   ├── modern_gui_win11.py     # Módulo reconocimiento (PySide6)
│   │   └── database_gui.py         # Módulo gestión de BD
│   ├── core/
│   │   ├── model_manager.py        # Gestión del modelo Florence-2
│   │   ├── image_processor.py      # Procesamiento de imágenes
│   │   └── sqlite_database.py      # Base de datos SQLite
│   ├── output/
│   │   └── output_handler_v2.py    # Manejo de salidas
│   └── utils/
│       └── keyword_extractor.py    # Extracción de keywords
```

## 🔄 Flujo de Trabajo

1. **Inicio** → GUI de Inicio se abre automáticamente
2. **Selección** → Usuario elige módulo desde las tarjetas
3. **Trabajo** → Usuario realiza tareas en el módulo seleccionado
4. **Regreso** → Al cerrar módulo, regresa al Centro de Control
5. **Estadísticas** → Se actualizan automáticamente al regresar

## 🚀 Ventajas de la Nueva Estructura

### **Para el Usuario**
- ✅ **Navegación clara** entre funcionalidades
- ✅ **Especialización** de cada módulo
- ✅ **Menos sobrecarga** visual
- ✅ **Acceso rápido** a funciones específicas

### **Para el Desarrollo**
- ✅ **Separación de responsabilidades**
- ✅ **Código más mantenible**
- ✅ **Fácil extensión** con nuevos módulos
- ✅ **Testing independiente** por módulo

### **Para el Rendimiento**
- ✅ **Carga bajo demanda** de módulos pesados
- ✅ **Menor uso de memoria** inicial
- ✅ **Inicialización más rápida**
- ✅ **Mejor gestión de recursos**

## 🔧 Configuración y Requisitos

### **Dependencias Principales**
- Python 3.8+
- Tkinter (incluido con Python)
- PySide6 (opcional, para interfaz moderna)
- PIL/Pillow
- PyTorch + Transformers (Florence-2)
- YAKE (extracción de keywords)

### **Instalación**
```bash
pip install -r requirements.txt
```

### **Ejecución**
```bash
python main.py
```

## 🆕 Próximas Funcionalidades

### **Módulo de Base de Datos**
- [ ] Búsqueda avanzada completa
- [ ] Exportación masiva en múltiples formatos
- [ ] Herramientas de mantenimiento funcionales
- [ ] Gráficos y estadísticas avanzadas
- [ ] Sistema de copias de seguridad

### **GUI de Inicio**
- [ ] Dashboard con métricas en tiempo real
- [ ] Configuración global de la aplicación
- [ ] Gestión de perfiles de usuario
- [ ] Notificaciones y alertas

### **Integración**
- [ ] API REST para acceso externo
- [ ] Plugin system para extensiones
- [ ] Sincronización con servicios en la nube
- [ ] Exportación a sistemas externos

---

## 📞 Soporte

Para reportar problemas o sugerir mejoras, utiliza el sistema de issues del proyecto.

**StockPrep Pro v2.0** - Sistema Inteligente de Procesamiento de Imágenes con Arquitectura Modular 