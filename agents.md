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
...
    }
  ]
}

