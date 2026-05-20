# HANDOFF — StockPrep Pro / Caption

> **Última actualización:** 2026-05-20 (post-fix GUI PySide6)  
> **Para:** otro agente, IA o desarrollador que retome el trabajo sin historial de chat.

---

## Contexto rápido

Proyecto **off-line** de captioning de imágenes (Florence-2) con gestor de base de datos y galería. Stack UI principal: **PySide6**. Base de datos: **SQLite** (`stockprep_images.db` en la raíz del proyecto, si existe).

Arquitectura de galería: **SQLite + FTS5 + thumbnails WebP en BLOB**.

---

## Dónde trabajar

| Concepto | Valor |
|----------|--------|
| **Carpeta local** | `E:\Proyectos\Caption` |
| **Repositorio GitHub** | https://github.com/Rayeta76/caption.git |
| **Rama activa** | `backup/mejora_modelo` |
| **Rama estable** | `main` |
| **Commits relevantes** | `3e1b6aa` (handoff inicial), `d1053ce` (fix GUI PySide6) |

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
| Clic → imagen grande + prev/next | OK | `ImageViewerDialog` en `gallery_pyside.py` |
| Búsqueda con grid visual | OK | pestaña **Busqueda Visual** |
| Thumbnails desde BLOB WebP | OK | si existe columna `thumbnail_webp` |
| Thumbnails desde disco | OK | fallback si hay `ruta_salida` / `ruta_completa` |
| FTS5 en búsqueda por keyword | OK | vía `db_v2.buscar_imagenes_fts5()` |
| Explorador (tabla texto) | OK | doble clic también abre visor |

**Obsoleto (no usar para PySide6):** `src/gui/enhanced_gallery.py` (Tkinter). La galería activa es `gallery_pyside.py`.

---

## Hecho vs pendiente

### Hecho

- `src/gui/gallery_pyside.py` — visor, thumbnails, grid
- `src/gui/database_gui_pyside.py` — integración galería + búsqueda visual
- `src/core/enhanced_database_manager_v2.py` — FTS5, BLOB, migración columnas
- `main_control_pyside.py` — arranque seguro sin PySide6
- `main.py` — sin emojis en prints (Windows cp1252)
- `HANDOFF.md`, `run_stockprep.bat`, `integrate_enhanced_gallery.py` (opcional)

### Pendiente

- [ ] Probar en máquina del usuario con `stockprep_images.db` real
- [ ] `pip install PySide6` si sigue el fallback a Tkinter
- [ ] Push de `d1053ce` a GitHub si aún no se hizo (`git push origin backup/mejora_modelo`)
- [ ] Merge a `main` cuando esté validado
- [ ] Actualizar `GALERIA_MEJORADA_README.md` (sigue diciendo cosas desactualizadas)

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
- `GALERIA_MEJORADA_README.md` puede contradecir este handoff; priorizar **HANDOFF.md**.
- Otro agente/IA **no ve el chat**; leer este archivo + `git log` + código.

---

## Criterios de terminado

- [x] Clic en miniatura → visor grande con navegación
- [x] Búsqueda con thumbnails
- [ ] Validación manual por el usuario
- [ ] Push / merge a `main`

---

## Decisiones del usuario

- Experiencia tipo **web de stock** (grid, zoom, búsqueda visual).
- Trabajar en **`backup/mejora_modelo`** hasta validar.
