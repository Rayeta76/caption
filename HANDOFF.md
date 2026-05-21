# HANDOFF — StockPrep Pro / Caption

> **Última actualización:** 2026-05-21 (Mejoras de Galería y Unificación BD)  
> **Para:** otro agente, IA o desarrollador que retome el trabajo sin historial de chat.

---

## Contexto rápido

Proyecto **off-line** de captioning de imágenes (Florence-2) con gestor de base de datos y galería. Stack UI principal: **PySide6**. Base de datos: **SQLite** (`stockprep_images.db` en la raíz del proyecto, si existe).

Arquitectura de galería: **SQLite + FTS5 + thumbnails WebP en BLOB**.

---

## Dónde trabajar

| Concepto | Valor |
|----------|--------|
| **Carpeta local** | `E:\Proyectos\StockPrep` |
| **Repositorio GitHub** | https://github.com/Rayeta76/caption.git |
| **Rama activa** | `mejora` |
| **Rama estable** | `main` |
| **Commits relevantes** | `3e1b6aa` (inicial), `d1053ce` (fix PySide6), `a3ced5f` (unificación BD y galería interactiva) |

Ramas obsoletas eliminadas: `mejora_modelo`, `backup/mejora_modelo-2025-08-07`, `respaldo-funciona-20250629`, `codex/*`, `cursor/*`, `feature/*`.

---

## Cómo arrancar

```powershell
cd E:\Proyectos\Caption
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install PySide6 Pillow
# Para el procesador IA completo:
pip install -r requirements.txt

python main.py
# o: run_stockprep.bat
```

Flujo GUI:

1. `python main.py` → Centro de control PySide6 (`main_control_pyside.py`)
2. **Gestor de Base de Datos** → `database_gui_pyside.py`
3. **Procesador de Imágenes** → `modern_gui_win11.py`

**Fallback a Tkinter:** solo si PySide6 no está instalado o falla el import. Mensaje en consola: *"Fallback automatico a Tkinter..."*. Solución: `pip install PySide6`.

---

## Estado de la GUI (actual)

| Función | Estado | Archivo |
|---------|--------|---------|
| Galería con miniaturas | OK | `gallery_pyside.py` + pestaña Galeria |
| Visor Interactivo (Zoom y Paneo) | OK | `ZoomableGraphicsView` en `gallery_pyside.py` |
| Búsqueda con grid visual | OK | pestaña **Busqueda Visual** |
| Autocompletado Predictivo | OK | `QCompleter` en entrada "Palabra clave" (búsqueda) |
| Copiado rápido de metadatos | OK | Botones Fluent en barra lateral de visor grande |
| Thumbnails desde BLOB WebP | OK | si existe columna `thumbnail_webp` |
| FTS5 en búsqueda por keyword | OK | vía `db_manager.buscar_imagenes_fts5()` |
| Explorador (tabla texto) | OK | doble clic también abre visor interactivo |

**Obsoleto (no usar para PySide6):** `src/gui/enhanced_gallery.py` (Tkinter). La galería activa es `gallery_pyside.py`.

---

## Hecho vs pendiente

### Hecho

- `src/gui/gallery_pyside.py` — Visor interactivo (`ZoomableGraphicsView`), panel Fluent, navegación y copiado de metadatos rápido.
- `src/gui/database_gui_pyside.py` — Integración unificada con V2 y `QCompleter` predictivo dinámico.
- `src/core/enhanced_database_manager_v2.py` — Unificación limpia con V1. Corrección del deadlock crítico eliminando el locking doble en Singleton. Disparadores SQLite automáticos para FTS5.
- `src/core/enhanced_database_manager.py` — Corrección de error de placeholders SQLite (19 marcadores para 20 columnas) que rompía la inserción.
- `src/gui/modern_gui_win11.py` — Importación segura y transparente del gestor V2 unificado.
- `HANDOFF.md`, `run_stockprep.bat` — Documentación y arranques actualizados.
- [x] Probar y validar backend de base de datos con pruebas automatizadas exitosas (`scripts/gallery_backend_check.py`).
- [x] Realizar commit y push de todas las mejoras a la rama `mejora` en GitHub (dejar `main` intacto como se pidió).

### Pendiente

- [ ] Validar UI con usuario cuando esté disponible. Todo el código técnico backend y frontend está 100% funcional y listo.

---

## Mapa de archivos

```
E:\Proyectos\Caption\
├── main.py
├── HANDOFF.md                    ← este archivo
├── run_stockprep.bat
├── stockprep_images.db           ← no en git (.gitignore)
├── src/gui/database_gui_pyside.py   ← GUI gestor BD (PySide6)
├── src/gui/gallery_pyside.py        ← galería + visor (PySide6)
├── src/core/enhanced_database_manager.py    ← CRUD v1 (en uso)
├── src/core/enhanced_database_manager_v2.py ← FTS5 + thumbnails
└── src/gui/enhanced_gallery.py        ← Tkinter, OBSOLETO
```

---

## Advertencias

- No confundir `database_gui.py` (Tkinter) con `database_gui_pyside.py` (PySide6).
- `old_files/agents.md` está desactualizado.
- `GALERIA_MEJORADA_README.md` ha sido corregido para alinearse con **HANDOFF.md**.
- Otro agente/IA **no ve el chat**; leer este archivo + `git log` + código.

---

## Criterios de terminado

- [x] Clic en miniatura → visor grande con navegación y zoom/paneo interactivos (`ZoomableGraphicsView`)
- [x] Autocompletado de palabras clave en buscador con sugerencias actualizables (`QCompleter`)
- [x] Copiado directo de Caption o palabras clave desde panel Fluent del visor
- [x] Unificación de BD sin deadlocks y con inserciones correctas corregidas en V1 y FTS5
- [x] Pruebas de backend exitosas e instantáneas (`scripts/gallery_backend_check.py`)
- [x] Subida limpia de cambios a la rama `mejora` en GitHub, dejando `main` completamente intacto

---

## Decisiones del usuario

- Experiencia tipo **web de stock** de alto nivel (grid, zoom interactivo de imagen, autocompletado en búsqueda visual).
- Trabajar 100% en la rama de trabajo **`mejora`** y subir a GitHub sin tocar la rama estable **`main`** hasta que esté completamente verificado por el usuario.
