import os

def generar_arbol_markdown(ruta_raiz: str, archivo_salida: str, nivel: int = 0, archivo=None):
    elementos = sorted(os.listdir(ruta_raiz))
    for i, nombre in enumerate(elementos):
        ruta_completa = os.path.join(ruta_raiz, nombre)
        prefijo = "│   " * nivel + "├── " if i < len(elementos) - 1 else "│   " * nivel + "└── "
        if os.path.isdir(ruta_completa):
            print(f"{prefijo}{nombre}/", file=archivo)
            generar_arbol_markdown(ruta_completa, archivo_salida, nivel + 1, archivo)
        else:
            print(f"{prefijo}{nombre}", file=archivo)

def exportar_readme_estructura(ruta_proyecto: str, nombre_salida: str = "README.md"):
    with open(nombre_salida, "w", encoding="utf-8") as f:
        print(f"# Proyecto: {os.path.basename(ruta_proyecto)}", file=f)
        print("\n## Estructura de Carpetas y Archivos\n", file=f)
        print("```text", file=f)
        generar_arbol_markdown(ruta_proyecto, nombre_salida, archivo=f)
        print("```", file=f)

if __name__ == "__main__":
    ruta = r"E:\Proyectos\Caption"  # Ruta del proyecto (la que ya conocemos)
    exportar_readme_estructura(ruta)
    print("✅ README.md generado correctamente con la estructura del proyecto.")
