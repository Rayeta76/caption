# HANDOFF — StockPrep Pro / Caption

> **Última actualización:** 2026-05-20  
> **Para:** otro agente, IA o desarrollador que retome el trabajo sin historial de chat.

---

## Contexto rápido

Proyecto **off-line** de captioning de imágenes (Florence-2) con gestor de base de datos y galería. Stack UI principal: **PySide6**. Base de datos: **SQLite** (`stockprep_images.db` en la raíz del proyecto, si existe).

El usuario reportó problemas en la galería:

- Al hacer clic en una imagen **no se amplía** (solo texto / `QMessageBox`).
- En búsqueda aparece **solo texto, sin miniaturas**.
- Experiencia lejana de una web de stock (sin visor, sin grid visual en resultados).

Se decidió la arquitectura: **SQLite + FTS5 + thumbnails WebP en BLOB** (buena relación simplicidad/rendimiento para PySide6 off-line).

---

## Dónde trabajar

| Concepto | Valor |
|----------|--------|
| **Carpeta local** | `E:\Proyectos\Caption` |
| **Repositorio GitHub** | https://github.com/Rayeta76/caption.git |
| **Rama activa de trabajo** | `backup/mejora_modelo` |
| **Rama estable (referencia)** | `main` |
| **Último commit de restauración** | `b78ffb9` — *Punto de restauración: Antes de mejoras de galería* |

Ramas obsoletas **ya eliminadas** (local y remoto): `mejora_modelo`, `backup/mejora_modelo-2025-08-07`, `respaldo-funciona-20250629`, ramas `codex/*`, `cursor/*`, `feature/*`.

---

## Cómo arrancar la aplicación

```powershell
cd E:\Proyectos\Caption

# Primera vez (recomendado)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Arranque
python main.py
# o doble clic en:
#   run_stockprep.bat
```

Flujo en GUI:

1. `python main.py` → Centro de control PySide6  
2. **Gestor de Base de Datos** → galería y búsqueda (archivo: `src/gui/database_gui_pyside.py`)  
3. **Procesador de Imágenes** → `src/gui/modern_gui_win11.py`

**Nota:** En el entorno probado en sesión anterior faltaban `PySide6` y `transformers` en el Python global; sin `venv` la app puede fallar al abrir.

---

## Hecho vs pendiente

### ✅ Hecho (archivos creados, no integrados en la app principal)

| Archivo | Descripción |
|---------|-------------|
| `src/core/enhanced_database_manager_v2.py` | BD v2: FTS5, thumbnails WebP en BLOB, migración |
| `src/gui/enhanced_gallery.py` | Galería nueva: grid, clic → visor, búsqueda visual (PySide6) |
| `integrate_enhanced_gallery.py` | Script Tkinter para migrar BD y generar thumbnails |
| `GALERIA_MEJORADA_README.md` | Documentación de la mejora (léela con criterio; ver abajo) |
| `run_stockprep.bat` | Lanzador Windows con `pause` |
| `create_restore_point.py` | Script para tag/commit de restauración |

### ✅ Integrado en PySide6 (2026-05-20)

- `src/gui/gallery_pyside.py` — visor ampliado, thumbnails BLOB/disco, grid reutilizable.
- `database_gui_pyside.py` — galería y **Búsqueda visual** con miniaturas; clic abre visor (no QMessageBox).
- `main_control_pyside.py` — ya no rompe si falta PySide6 (`NameError`).
- `main.py` — mensajes sin emojis (evita error cp1252 en Windows).

### ❌ Pendiente

1. Instalar deps: `pip install PySide6 Pillow` (y resto de `requirements.txt` para el procesador IA).
2. Primera vez: abrir Gestor BD genera columnas `thumbnail_webp` vía `EnhancedDatabaseManagerV2` (puede tardar si hay muchas imágenes).
3. Opcional: `python integrate_enhanced_gallery.py` para migración guiada.
4. `enhanced_gallery.py` (Tkinter) queda **obsoleto**; usar solo flujo PySide6.

---

## Archivos clave (mapa)

```
E:\Proyectos\Caption\
├── main.py                          # Entrada: --gui pyside|tkinter, --cli
├── run_stockprep.bat                # Lanzador doble clic
├── HANDOFF.md                       # Este archivo (fuente de verdad para handoff)
├── GALERIA_MEJORADA_README.md       # Detalle técnico de la galería v2
├── stockprep_images.db              # BD (puede no estar en git; ver .gitignore)
├── src/gui/database_gui_pyside.py   # ⚠️ Galería ACTUAL en producción (antigua)
├── src/gui/enhanced_gallery.py      # Galería NUEVA (no cableada aún)
├── src/core/enhanced_database_manager.py    # BD v1 (en uso hoy)
└── src/core/enhanced_database_manager_v2.py # BD v2 (FTS5 + WebP BLOB)
```

---

## Problema original (código actual)

En `database_gui_pyside.py`, al clic en miniatura:

```python
thumbnail_widget.clicked.connect(self.show_record_details)
# show_record_details → QMessageBox con texto, NO imagen grande
```

La búsqueda en la misma GUI no reutiliza el componente de galería mejorada.

---

## Advertencias para no repetir errores

- **`GALERIA_MEJORADA_README.md`** describe la solución como terminada; **no lo está** hasta integrar en `database_gui_pyside.py`.
- No confundir `database_gui.py` (Tkinter) con `database_gui_pyside.py` (PySide6, la que abre `main.py`).
- `old_files/agents.md` está **desactualizado**; usar este `HANDOFF.md`.
- Historial de chat en Cursor **no** es visible para otro agente; solo este archivo + git + código.

---

## Git — comandos útiles

```powershell
cd E:\Proyectos\Caption
git branch --show-current          # debe ser backup/mejora_modelo
git status
git log -3 --oneline
```

Volver al punto de restauración anterior a la galería:

```bash
git checkout b78ffb9
```

---

## Criterios de “terminado”

- [x] Clic en miniatura abre visor con imagen grande y navegación prev/next  
- [x] Búsqueda muestra resultados con thumbnails (FTS5 si `db_v2` disponible)  
- [ ] Migración v2 completa en BD grande (automática al abrir Gestor BD)  
- [ ] Prueba manual: `python main.py` → Gestor BD → Galería + Búsqueda  
- [ ] Cambios commiteados y push a `origin/backup/mejora_modelo` (o PR a `main`)

---

## Contacto / decisiones del usuario

- Prefiere experiencia tipo **web de stock** (grid, zoom al clic, búsqueda visual).  
- Arquitectura acordada: **SQLite + FTS5 + WebP BLOB**.  
- Trabajar en **`backup/mejora_modelo`** hasta validar; **`main`** como línea estable.
