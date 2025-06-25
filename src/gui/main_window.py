"""
Interfaz gráfica principal de StockPrep
Este archivo crea la ventana principal de la aplicación
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Window, ttk
import threading
import queue
from pathlib import Path
import os

class StockPrepApp:
    """Aplicación principal con interfaz gráfica"""
    
    def __init__(self):
        """Inicializa la aplicación"""
        # Crear ventana principal con un tema moderno
        self.root = Window(themename="superhero")
        self.root.title("StockPrep - Procesador de Imágenes con IA")
        self.root.geometry("1000x700")

        # Fuente predeterminada para botones y etiquetas
        self.root.style.configure(".", font=("Segoe UI", 12))
        
        # Configurar icono si existe
        try:
            self.root.iconbitmap('icon.ico')
        except tk.TclError:
            pass  # Ignorar error si el icono no existe

        # Variables de control
        self.carpeta_entrada = tk.StringVar()
        self.carpeta_salida = tk.StringVar(value=str(Path.cwd() / "output"))
        self.modelo_cargado = False
        self.procesando = False
        
        # Cola para comunicación entre hilos
        self.cola_mensajes = queue.Queue()
        
        # Componentes del modelo
        self.model_manager = None
        self.processor = None
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Iniciar verificación de mensajes
        self.verificar_mensajes()

    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # === Sección 1: Título ===
        titulo = ttk.Label(
            main_frame,
            text="StockPrep - Generador de Descripciones con IA",
            font=('Arial', 16, 'bold')
        )
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # === Sección 2: Selección de carpetas ===
        # Carpeta de entrada
        ttk.Label(main_frame, text="Carpeta de imágenes:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            main_frame,
            textvariable=self.carpeta_entrada,
            width=50
        ).grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(
            main_frame,
            text="Examinar...",
            command=self.seleccionar_carpeta_entrada
        ).grid(row=1, column=2)

        # Carpeta de salida
        ttk.Label(main_frame, text="Carpeta de salida:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            main_frame,
            textvariable=self.carpeta_salida,
            width=50
        ).grid(row=2, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(
            main_frame,
            text="Examinar...",
            command=self.seleccionar_carpeta_salida
        ).grid(row=2, column=2)

        # === Sección 3: Opciones ===
        opciones_frame = ttk.LabelFrame(main_frame, text="Opciones de procesamiento", padding="10")
        opciones_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)

        # Formato de salida
        ttk.Label(opciones_frame, text="Formato de salida:").grid(row=0, column=0, sticky=tk.W)
        self.formato_salida = tk.StringVar(value="JSON")
        formato_combo = ttk.Combobox(
            opciones_frame,
            textvariable=self.formato_salida,
            values=["JSON", "CSV", "XML"],
            state="readonly",
            width=15
        )
        formato_combo.grid(row=0, column=1, padx=10, sticky=tk.W)

        # Opciones adicionales
        self.incluir_objetos = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opciones_frame,
            text="Detectar objetos en las imágenes",
            variable=self.incluir_objetos
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        self.renombrar_archivos = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opciones_frame,
            text="Renombrar archivos con la descripción",
            variable=self.renombrar_archivos
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W)

        # === Sección 4: Botones de control ===
        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=4, column=0, columnspan=3, pady=20)

        self.btn_cargar_modelo = ttk.Button(
            botones_frame,
            text="1. Cargar Modelo Florence-2",
            command=self.cargar_modelo,
            width=25,
            bootstyle="info"
        )
        self.btn_cargar_modelo.pack(side=tk.LEFT, padx=5)

        self.btn_procesar = ttk.Button(
            botones_frame,
            text="2. Procesar Imágenes",
            command=self.procesar_imagenes,
            state=tk.DISABLED,
            width=25,
            bootstyle="success"
        )
        self.btn_procesar.pack(side=tk.LEFT, padx=5)

        self.btn_detener = ttk.Button(
            botones_frame,
            text="Detener",
            command=self.detener_procesamiento,
            state=tk.DISABLED,
            width=15,
            bootstyle="danger"
        )
        self.btn_detener.pack(side=tk.LEFT, padx=5)

        # === Sección 5: Progreso ===
        progreso_frame = ttk.LabelFrame(main_frame, text="Progreso", padding="10")
        progreso_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progreso_frame.columnconfigure(0, weight=1)

        # Barra de progreso
        self.progreso = ttk.Progressbar(
            progreso_frame,
            mode='determinate',
            length=400
        )
        self.progreso.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Etiquetas de estado
        self.lbl_estado = ttk.Label(progreso_frame, text="Esperando...")
        self.lbl_estado.grid(row=1, column=0, sticky=tk.W)

        self.lbl_memoria = ttk.Label(progreso_frame, text="")
        self.lbl_memoria.grid(row=1, column=1, sticky=tk.E)

        # === Sección 6: Log ===
        log_frame = ttk.LabelFrame(main_frame, text="Registro de actividad", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Área de texto con scroll
        self.log_text = tk.Text(log_frame, height=12, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Hacer que el log frame se expanda
        main_frame.rowconfigure(6, weight=1)

        # Mensaje inicial
        self.escribir_log("✨ Bienvenido a StockPrep")
        self.escribir_log("📌 Instrucciones:")
        self.escribir_log("1. Primero carga el modelo Florence-2 (botón 1)")
        self.escribir_log("2. Selecciona la carpeta con tus imágenes")
        self.escribir_log("3. Presiona 'Procesar Imágenes' (botón 2)")

    def verificar_mensajes(self):
        """Verifica mensajes de los hilos de procesamiento"""
        try:
            while True:
                tipo, datos = self.cola_mensajes.get_nowait()
                
                if tipo == 'log':
                    self.escribir_log(datos)
                elif tipo == 'estado':
                    self.lbl_estado.config(text=datos)
                elif tipo == 'progreso':
                    actual, total = datos
                    self.progreso['value'] = (actual / total) * 100
                    self.lbl_estado.config(text=f"Procesando imagen {actual} de {total}")
                elif tipo == 'memoria':
                    self.lbl_memoria.config(text=datos)
                elif tipo == 'modelo_cargado':
                    self.modelo_cargado = True
                    self.btn_cargar_modelo.config(state=tk.DISABLED, text="✅ Modelo Cargado")
                    self.btn_procesar.config(state=tk.NORMAL)
                elif tipo == 'error':
                    messagebox.showerror("Error", datos)
                elif tipo == 'completado':
                    self.procesamiento_completado()

        except queue.Empty:
            pass
        
        # Verificar de nuevo en 100ms
        self.root.after(100, self.verificar_mensajes)

    def escribir_log(self, mensaje):
        """Escribe un mensaje en el área de log"""
        self.log_text.insert(tk.END, f"{mensaje}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def seleccionar_carpeta_entrada(self):
        """Abre diálogo para seleccionar carpeta de entrada"""
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta con las imágenes")
        if carpeta:
            self.carpeta_entrada.set(carpeta)
            self.escribir_log(f"📁 Carpeta seleccionada: {carpeta}")

            # Contar imágenes
            extensiones = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
            try:
                imagenes = [f for f in Path(carpeta).iterdir() if f.suffix.lower() in extensiones]
                self.escribir_log(f"📷 Encontradas {len(imagenes)} imágenes")
            except Exception as e:
                self.escribir_log(f"❌ Error al leer carpeta: {str(e)}")

    def seleccionar_carpeta_salida(self):
        """Abre diálogo para seleccionar carpeta de salida"""
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta para guardar resultados")
        if carpeta:
            self.carpeta_salida.set(carpeta)

    def cargar_modelo(self):
        """Carga el modelo Florence-2 en un hilo separado"""
        def cargar_en_hilo():
            try:
                self.cola_mensajes.put(('log', '🔄 Iniciando carga del modelo...'))
                self.cola_mensajes.put(('estado', 'Cargando modelo Florence-2...'))

                # Importar y crear el gestor del modelo
                from core.model_manager import Florence2Manager
                self.model_manager = Florence2Manager()

                # Función callback para actualizar progreso
                def actualizar_progreso(mensaje):
                    self.cola_mensajes.put(('log', mensaje))

                # Cargar modelo
                if self.model_manager.cargar_modelo(actualizar_progreso):
                    # Crear procesador
                    from core.image_processor import ImageProcessor
                    self.processor = ImageProcessor(self.model_manager)

                    # Actualizar memoria
                    memoria = self.model_manager.obtener_uso_memoria()
                    self.cola_mensajes.put(('memoria', memoria))
                    self.cola_mensajes.put(('modelo_cargado', True))
                    self.cola_mensajes.put(('estado', 'Modelo cargado y listo'))
                else:
                    self.cola_mensajes.put(('error', 'No se pudo cargar el modelo'))

            except Exception as e:
                self.cola_mensajes.put(('error', f'Error al cargar modelo: {str(e)}'))

        # Deshabilitar botón y ejecutar en hilo
        self.btn_cargar_modelo.config(state=tk.DISABLED, text="Cargando...")
        thread = threading.Thread(target=cargar_en_hilo, daemon=True)
        thread.start()

    def procesar_imagenes(self):
        """Procesa las imágenes en un hilo separado"""
        # Validar entrada
        if not self.carpeta_entrada.get():
            messagebox.showerror("Error", "Por favor selecciona una carpeta de imágenes")
            return
        if not self.modelo_cargado:
            messagebox.showerror("Error", "Por favor carga primero el modelo")
            return

        # Preparar para procesamiento
        self.procesando = True
        self.btn_procesar.config(state=tk.DISABLED)
        self.btn_detener.config(state=tk.NORMAL)
        self.progreso['value'] = 0

        def procesar_en_hilo():
            try:
                carpeta_entrada = Path(self.carpeta_entrada.get())
                carpeta_salida = Path(self.carpeta_salida.get())
                carpeta_salida.mkdir(exist_ok=True, parents=True)

                # Buscar imágenes
                extensiones = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
                imagenes = [
                    f for f in carpeta_entrada.iterdir() 
                    if f.suffix.lower() in extensiones
                ]
                
                if not imagenes:
                    self.cola_mensajes.put(('error', 'No se encontraron imágenes en la carpeta'))
                    return

                self.cola_mensajes.put(('log', f'\n🚀 Iniciando procesamiento de {len(imagenes)} imágenes'))
                resultados = []

                # Procesar cada imagen
                for i, imagen_path in enumerate(imagenes):
                    if not self.procesando:
                        break
                    
                    self.cola_mensajes.put(('progreso', (i + 1, len(imagenes))))
                    self.cola_mensajes.put(('log', f'📸 Procesando: {imagen_path.name}'))

                    # Procesar imagen
                    resultado = self.processor.procesar_imagen(str(imagen_path))
                    
                    if 'error' not in resultado:
                        # Extraer keywords
                        keywords = self.processor.extraer_keywords(resultado)
                        resultado['keywords'] = keywords
                        
                        # Renombrar si está activado
                        if self.renombrar_archivos.get():
                            descripcion = resultado.get('descripcion', '')
                            if descripcion:
                                nombre_nuevo = self._crear_nombre_seguro(descripcion, i)
                                destino = carpeta_salida / f"{nombre_nuevo}{imagen_path.suffix}"
                                import shutil
                                shutil.copy2(imagen_path, destino)
                                resultado['archivo_renombrado'] = destino.name
                                self.cola_mensajes.put(('log', f'✅ Renombrado: {destino.name}'))
                    else:
                        self.cola_mensajes.put(('log', f'❌ Error: {resultado["error"]}'))
                    
                    resultados.append(resultado)

                    # Actualizar memoria cada 5 imágenes
                    if i % 5 == 0:
                        memoria = self.model_manager.obtener_uso_memoria()
                        self.cola_mensajes.put(('memoria', memoria))

                # Guardar resultados
                if resultados and self.procesando:
                    self._guardar_resultados(resultados, carpeta_salida)
                
                self.cola_mensajes.put(('completado', True))

            except Exception as e:
                self.cola_mensajes.put(('error', f'Error durante el procesamiento: {str(e)}'))
                self.cola_mensajes.put(('completado', True))

        # Ejecutar en hilo
        thread = threading.Thread(target=procesar_en_hilo, daemon=True)
        thread.start()

    def _crear_nombre_seguro(self, texto, indice):
        """Crea un nombre de archivo seguro a partir del texto"""
        import re
        texto = texto.lower()
        texto = re.sub(r'[^\w\s-]', '', texto)
        texto = re.sub(r'[-\s]+', '-', texto)
        texto = texto[:50]  # Limitar longitud
        return f"{texto}_{indice:03d}"

    def _guardar_resultados(self, resultados, carpeta_salida):
        """Guarda los resultados en el formato seleccionado"""
        formato = self.formato_salida.get()
        try:
            if formato == "JSON":
                self._guardar_json(resultados, carpeta_salida)
            elif formato == "CSV":
                self._guardar_csv(resultados, carpeta_salida)
            elif formato == "XML":
                self._guardar_xml(resultados, carpeta_salida)
            self.cola_mensajes.put(('log', f'💾 Resultados guardados en formato {formato}'))
        except Exception as e:
            self.cola_mensajes.put(('error', f'Error al guardar resultados: {str(e)}'))

    def _guardar_json(self, resultados, carpeta_salida):
        """Guarda resultados en formato JSON"""
        import json
        from datetime import datetime
        archivo = carpeta_salida / f"stockprep_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        datos = {
            'metadata': {
                'total_imagenes': len(resultados),
                'fecha_procesamiento': datetime.now().isoformat(),
                'modelo': 'Florence-2-large-ft-safetensors',
                'formato': 'JSON'
            },
            'resultados': resultados
        }
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    def _guardar_csv(self, resultados, carpeta_salida):
        """Guarda resultados en formato CSV"""
        import csv
        from datetime import datetime
        archivo = carpeta_salida / f"stockprep_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            campos = ['archivo', 'descripcion', 'keywords', 'objetos', 'archivo_renombrado']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            for resultado in resultados:
                if 'error' not in resultado:
                    fila = {
                        'archivo': resultado.get('archivo', ''),
                        'descripcion': resultado.get('descripcion', ''),
                        'keywords': ', '.join(resultado.get('keywords', [])),
                        'objetos': str(resultado.get('objetos', '')),
                        'archivo_renombrado': resultado.get('archivo_renombrado', '')
                    }
                    writer.writerow(fila)

    def _guardar_xml(self, resultados, carpeta_salida):
        """Guarda resultados en formato XML"""
        import xml.etree.ElementTree as ET
        from datetime import datetime
        archivo = carpeta_salida / f"stockprep_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        
        root = ET.Element("stockprep_resultados")
        
        # Metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "total_imagenes").text = str(len(resultados))
        ET.SubElement(metadata, "fecha_procesamiento").text = datetime.now().isoformat()
        ET.SubElement(metadata, "modelo").text = "Florence-2-large-ft-safetensors"

        # Resultados
        resultados_elem = ET.SubElement(root, "resultados")
        for resultado in resultados:
            if 'error' not in resultado:
                imagen_elem = ET.SubElement(resultados_elem, "imagen")
                ET.SubElement(imagen_elem, "archivo").text = resultado.get('archivo', '')
                ET.SubElement(imagen_elem, "descripcion").text = resultado.get('descripcion', '')
                
                # Keywords
                keywords_elem = ET.SubElement(imagen_elem, "keywords")
                for keyword in resultado.get('keywords', []):
                    ET.SubElement(keywords_elem, "keyword").text = keyword

                if 'archivo_renombrado' in resultado:
                    ET.SubElement(imagen_elem, "archivo_renombrado").text = resultado['archivo_renombrado']

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(archivo, encoding='utf-8', xml_declaration=True)

    def detener_procesamiento(self):
        """Detiene el procesamiento en curso"""
        self.procesando = False
        self.btn_detener.config(state=tk.DISABLED)
        self.escribir_log("⏹️ Procesamiento detenido por el usuario")

    def procesamiento_completado(self):
        """Llamado cuando se completa el procesamiento"""
        self.procesando = False
        self.btn_procesar.config(state=tk.NORMAL)
        self.btn_detener.config(state=tk.DISABLED)
        self.lbl_estado.config(text="Procesamiento completado")
        self.escribir_log("\n✅ ¡Procesamiento completado!")
        messagebox.showinfo(
            "Completado",
            "El procesamiento ha finalizado.\nRevisa la carpeta de salida para ver los resultados."
        )

    def run(self):
        """Inicia la aplicación"""
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Iniciar bucle principal
        self.root.mainloop()