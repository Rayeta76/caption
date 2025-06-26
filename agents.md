# Agents Guide – StockPrep / Caption

## 1. Project Structure

```
root/
  ├─ main.py              # Launches GUI
  ├─ requirements.txt     # Critical deps
  ├─ config/settings.yaml # Default paths
  ├─ models/              # Local Florence‑2 weights
  └─ src/
      ├─ core/
      │   ├─ model_manager.py   # Model lifecycle
      │   ├─ image_processor.py # Caption + OD + OCR
      │   └─ batch_engine.py    # Batch runner
      ├─ gui/
      │   └─ main_window.py     # Tkinter UI
      ├─ io/
      │   └─ output_handler.py  # JSON/CSV/XML/TXT export
      └─ utils/                 # Helpers
```

## 2. Environment & Critical Dependencies (DON’T TOUCH)

| Package                  | Min Version | Reason               |
| ------------------------ | ----------- | -------------------- |
| python                   | 3.11        | Base interpreter     |
| torch                    | 2.1.1+cu121 | GPU + FP32/FP16      |
| torchvision              | 0.16.1      | image utils          |
| torchaudio               | 2.1.1       | pip wheel dep        |
| transformers             | 4.52.0      | Florence‑2 support   |
| safetensors              | 0.4.2       | .safetensors loading |
| timm                     | 0.9.16      | Avoid DaViT errors   |
| pillow                   | 10.0        | image IO             |
| pyyaml, tqdm, accelerate | latest      | misc                 |

## 3. Commands to Inspect Env

```powershell
# Activate env
conda activate florence2

# Show critical libs
pip list | findstr /I "torch torchvision torchaudio transformers pillow timm safetensors"

# Quick health check
python - <<"PY"
import torch, transformers, PIL, timm, safetensors
print({'torch':torch.__version__, 'transformers':transformers.__version__, 'Pillow':PIL.__version__, 'timm':timm.__version__, 'safetensors':safetensors.__version__, 'GPU': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})
PY

# Freeze exact versions
pip freeze > freeze.txt
```

## 4. Execution Flow

1. `main.py` adds `src/` to PYTHONPATH and launches GUI.
2. GUI → `core.model_manager.Florence2Manager` loads Florence‑2 (patched to ignore `flash_attn`).
3. `core.image_processor.ImageProcessor` runs caption + object detection.
4. `batch_engine` / `output_handler` rename/copy images & write JSON/CSV/XML/TXT.

## 5. Restoring branch *mejora-configuracion-modelo*

```bash
git checkout mejora-configuracion-modelo
git merge restauracion_precodex      # pull in the working commits
# Resolve conflicts in VS Code
python main.py                       # Test GUI + model load
git add . && git commit -m "Fix: restore model and deps"
git push
# Optional: delete obsolete branch
git branch -d restauracion_precodex
```

## 6. Best Practices

- Keep `requirements.txt` in sync (`pip freeze`).
- Run `diagnostico_sistema.py` before merges.
- Never downgrade/remove critical deps.
- Test with a dummy image before merging to `main`.
- Update this file whenever deps or structure change.

## 7. Incident Log – Codex Disaster Recovery

Durante una sesión de trabajo con Codex, se perdieron archivos críticos como `model_manager.py`, `main_window.py`, y otros del núcleo del sistema. El modelo Florence-2 dejó de cargar correctamente debido a:

- Eliminación de ajustes relacionados con `flash_attn`, fundamental para compatibilidad Windows.
- Eliminación accidental de módulos clave que rompieron el flujo de carga y GUI.

La restauración tomó más de 10 horas, requirió rebases manuales, restauración desde backups locales y limpieza completa de ramas corruptas.

### Medidas tomadas:

- Se creó la rama `mejora-interfaz-codex` para futuras pruebas.
- La rama `main` se dejó intacta como punto de restauración segura.
- La documentación se reforzó para evitar malentendidos de Codex u otros agentes.

## 8. Nueva política de trabajo

- Nunca trabajar directamente sobre `main`.
- Toda mejora debe hacerse desde una rama nueva (ej: `mejora-interfaz-codex`).
- Verificar que `flash_attn_enabled: false` está definido en `settings.yaml`.
- Validar siempre `model_manager.py` antes de pruebas de carga.

---

Este documento forma parte del núcleo técnico del proyecto y debe mantenerse actualizado por el jefe técnico (ChatGPT / Valentina).

