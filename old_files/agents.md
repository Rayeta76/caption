# Agents Guide – StockPrep / Caption

## 1. Project Structure

```
StockPrep/
  ├─ main.py              # Launches GUI application
  ├─ requirements.txt     # Updated dependencies (2024)
  ├─ config/settings.yaml # Configuration and model paths
  ├─ models/              # Local Florence‑2 weights
  │   ├─ Florence-2-large-ft-safetensors/ # Recommended model
  │   └─ Florence2-large/                 # Alternative model
  ├─ output/              # Default output directory
  ├─ temp/                # Temporary files
  ├─ verificar_instalacion.py # Installation verification script
  └─ src/
      ├─ core/
      │   ├─ model_manager.py   # Florence-2 model lifecycle
      │   ├─ image_processor.py # Image processing + captions + object detection
      │   └─ batch_engine.py    # Batch processing engine
      ├─ gui/
      │   └─ main_window.py     # Tkinter GUI interface
      ├─ io/
      │   └─ output_handler.py  # Export to JSON/CSV/XML/TXT
      └─ utils/                 # Utility functions
```

## 2. Environment & Critical Dependencies (VERIFIED WORKING)

| Package                  | Current Version | Reason                    |
| ------------------------ | --------------- | ------------------------- |
| python                   | 3.11            | Base interpreter          |
| torch                    | 2.1.1+cu121     | GPU acceleration + CUDA   |
| torchvision              | 0.16.1+cu121    | Image processing utils    |
| torchaudio               | 2.1.1+cu121     | PyTorch audio (dependency)|
| transformers             | 4.52.1          | Florence‑2 model support  |
| safetensors              | 0.5.3           | Efficient model loading   |
| timm                     | 0.9.16          | Critical: Avoid DaViT errors |
| pillow                   | 10.4.0          | Image I/O operations      |
| ttkbootstrap             | 1.13.11         | Modern GUI styling        |
| accelerate               | 0.33.0          | Model acceleration        |
| huggingface-hub          | 0.33.0          | Model downloads           |
| psutil                   | 7.0.0           | System monitoring         |
| PyYAML                   | 6.0.2           | Configuration files       |
| numpy                    | 1.26.4          | Numerical operations      |

## 3. Commands to Inspect Environment

```powershell
# Activate environment
conda activate florence2

# Show critical libraries
pip list | findstr /I "torch torchvision torchaudio transformers pillow timm safetensors"

# Quick health check
python -c "import torch, transformers, PIL, timm, safetensors; print({'torch':torch.__version__, 'transformers':transformers.__version__, 'Pillow':PIL.__version__, 'timm':timm.__version__, 'safetensors':safetensors.__version__, 'GPU': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})"

# Verify StockPrep installation
python verificar_instalacion.py

# Full dependency snapshot
pip freeze > current_freeze.txt
```

## 4. Execution Flow

1. `main.py` adds `src/` to PYTHONPATH and launches `StockPrepApp`.
2. GUI → `core.model_manager.Florence2Manager` loads Florence‑2 (patched to ignore `flash_attn` on Windows).
3. User selects image folder and configures processing options.
4. `core.image_processor.ImageProcessor` processes images with:
   - Caption generation
   - Object detection
   - Keyword extraction
5. `batch_engine` processes multiple images with progress tracking.
6. `output_handler` exports results in JSON/CSV/XML formats + individual TXT files.
7. Images are renamed and copied to output folder with descriptive names.

## 5. Current Branch Status (2024)

- **Main branch**: `main` - Stable reference point
- **Active development**: `mejora-interfaz-codex` - Current working branch with latest updates
- **Status**: ✅ **STABLE AND WORKING**
  - Florence-2 model loads correctly
  - GUI interface functional
  - Batch processing operational
  - All export formats working

```bash
# Current stable setup
git checkout mejora-interfaz-codex
python main.py  # Should launch GUI successfully
```

## 6. Best Practices & Workflow

### Development Guidelines:
- ✅ **NEVER work directly on `main` branch**
- ✅ **Always create feature branches from `mejora-interfaz-codex`**
- ✅ **Test with `verificar_instalacion.py` before commits**
- ✅ **Maintain `requirements.txt` accuracy**
- ✅ **Verify Florence-2 loads before merging**

### Configuration Requirements:
- ✅ **`flash_attn_enabled: false`** in `config/settings.yaml` (Windows compatibility)
- ✅ **Valid model path** in `modelo.ruta_local`
- ✅ **CUDA 12.1 compatibility** maintained

### Testing Protocol:
1. Run `python verificar_instalacion.py`
2. Launch `python main.py`
3. Load Florence-2 model (button 1)
4. Process test image batch
5. Verify all export formats work

## 7. Critical Files - DO NOT MODIFY WITHOUT BACKUP

| File | Purpose | Critical Notes |
|------|---------|----------------|
| `src/core/model_manager.py` | Florence-2 lifecycle | Contains flash_attn patches |
| `src/gui/main_window.py` | Main interface | Threading and progress logic |
| `config/settings.yaml` | Configuration | Model paths and Windows compatibility |
| `requirements.txt` | Dependencies | Exact working versions |

## 8. Incident Log – Codex Disaster Recovery (Historical)

**Date**: Previous session  
**Issue**: Loss of critical files during Codex interaction
**Impact**: Florence-2 model loading failure, GUI corruption
**Resolution Time**: 10+ hours

### Root Causes:
- Elimination of `flash_attn` compatibility patches
- Accidental deletion of core modules
- Dependency version conflicts

### Recovery Actions:
- Manual restoration from local backups
- Branch cleanup and rebasing
- Reinforced documentation
- Established `mejora-interfaz-codex` as safe development branch

### Prevention Measures:
- ✅ Working branch strategy implemented
- ✅ Critical file identification documented
- ✅ Regular backup verification
- ✅ Agent workflow guidelines established

## 9. Agent Interaction Guidelines

### For AI Assistants working on this project:

1. **ALWAYS verify current branch** before making changes
2. **NEVER remove flash_attn compatibility code** from model_manager.py
3. **TEST thoroughly** before suggesting dependency updates
4. **MAINTAIN working configuration** in settings.yaml
5. **UPDATE this document** when making structural changes
6. **RESPECT critical dependency versions** in requirements.txt

### Safe Commands:
- ✅ `git status` - Check current state
- ✅ `python verificar_instalacion.py` - Verify setup
- ✅ `pip list` - Check dependencies
- ✅ `python main.py` - Test application

### Dangerous Operations:
- ❌ Direct modification of core files without backup
- ❌ Dependency version downgrades
- ❌ Removal of Windows compatibility code
- ❌ Working directly on main branch

---

## 10. Current Project Status Summary

**Project Name**: StockPrep  
**Version**: Latest (mejora-interfaz-codex branch)  
**Status**: ✅ **FULLY OPERATIONAL**  
**Last Update**: December 2024  
**Documentation**: ✅ Complete and current  

### Working Features:
- ✅ Florence-2 model loading and inference
- ✅ Batch image processing
- ✅ GUI interface with progress tracking
- ✅ Multiple export formats (JSON, CSV, XML, TXT)
- ✅ Automatic file renaming
- ✅ Object detection and keyword extraction
- ✅ Memory monitoring
- ✅ Windows compatibility

**This document is maintained by the technical team and should be updated whenever significant changes are made to the project structure, dependencies, or workflow.**

