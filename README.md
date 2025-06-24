# StockPrep

Este proyecto utiliza el modelo **Florence‑2** para generar descripciones de imágenes.

## Configuración del modelo

Ahora `Florence2Manager` acepta un parámetro opcional `model_id`. Si no se indica, se leerá la variable de entorno `FLORENCE2_MODEL_ID`. En caso de que ninguna esté definida se usará la ruta local predeterminada.

```python
from core.model_manager import Florence2Manager

# Usar la variable de entorno
manager = Florence2Manager()

# O indicar la ruta o identificador manualmente
manager = Florence2Manager(model_id="microsoft/Florence-2-large")
```
