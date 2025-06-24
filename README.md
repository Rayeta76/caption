# StockPrep

StockPrep es una herramienta para procesar imágenes mediante el modelo **Florence-2**. Permite generar descripciones detalladas, detectar objetos y renombrar archivos de forma opcional. La aplicación cuenta con una interfaz gráfica escrita en tkinter.

## Instalación

1. Crea y activa un entorno virtual de Python (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```
2. Instala las dependencias desde `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Ejecuta `main.py` para iniciar la interfaz gráfica:
```bash
python main.py
```

Desde la ventana podrás cargar el modelo Florence‑2, seleccionar la carpeta con tus imágenes y procesarlas.

## Scripts opcionales

El proyecto incluye varios utilitarios para diagnóstico y descarga:

- **`diagnostico-florence2.py`**: verifica versiones de PyTorch, `timm` y Transformers, además de probar la carga básica del modelo.
- **`verificar_instalacion.py`**: muestra información resumida del entorno instalado, útil para confirmar que las dependencias se han instalado correctamente.
- **`download-florence2-script.py`**: descarga el modelo Florence‑2 de Hugging Face para usarlo de manera local.
- **`test-florence2-options.py`**: ofrece opciones de prueba para cargar diferentes variantes del modelo.

Estos scripts son opcionales y se pueden ejecutar directamente con `python nombre_del_script.py` para obtener información adicional o realizar pruebas.
