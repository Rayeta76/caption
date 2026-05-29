# --- src/io/output_handler.py ---
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

class OutputHandler:
    """
    Gestiona el guardado de los resultados del procesamiento en diferentes formatos.
    """
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_results(self, results: list, format_type: str, prefix="StockPrep"):
        """
        Guarda los resultados en el formato especificado.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}"
        
        if format_type.upper() == "JSON":
            return self._save_as_json(results, filename)
        elif format_type.upper() == "CSV":
            return self._save_as_csv(results, filename)
        # Puedes añadir XML u otros formatos aquí si lo deseas
        else:
            raise ValueError(f"Formato no soportado: {format_type}")

    def _save_as_json(self, results: list, filename: str):
        filepath = self.output_dir / f"{filename}.json"
        data_to_save = {
            "metadata": {
                "total_images": len(results),
                "export_date": datetime.now().isoformat(),
            },
            "results": results
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        return str(filepath)

    def _save_as_csv(self, results: list, filename: str):
        filepath = self.output_dir / f"{filename}.csv"
        
        # Aplanar los datos para el CSV
        flattened_data = []
        for res in results:
            if not res.get('error'):
                flattened_data.append({
                    'filename': res.get('filename', ''),
                    'new_filename': res.get('new_filename', ''),
                    'description': res.get('description', ''),
                    'keywords': ", ".join(res.get('keywords', [])),
                })

        if not flattened_data:
            return None # No hay datos que guardar

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
            writer.writeheader()
            writer.writerows(flattened_data)
        return str(filepath)