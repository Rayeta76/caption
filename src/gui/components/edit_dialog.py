"""
Diálogo de Edición para Registros de la Base de Datos.
"""
import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QFormLayout, QLineEdit,
        QDialogButtonBox, QLabel, QTextEdit
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

class EditRecordDialog(QDialog):
    def __init__(self, record_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Registro")
        
        self.layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        self.titulo_input = QLineEdit(record_data.get('titulo', ''))
        self.descripcion_input = QTextEdit(record_data.get('descripcion', ''))
        self.etiquetas_input = QLineEdit(', '.join(record_data.get('etiquetas', [])))

        form_layout.addRow(QLabel("Título:"), self.titulo_input)
        form_layout.addRow(QLabel("Descripción:"), self.descripcion_input)
        form_layout.addRow(QLabel("Etiquetas (separadas por comas):"), self.etiquetas_input)
        
        self.layout.addLayout(form_layout)
        
        # Botones
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.layout.addWidget(self.button_box)

    def get_data(self):
        """Devuelve los datos editados en un diccionario."""
        etiquetas = [tag.strip() for tag in self.etiquetas_input.text().split(',') if tag.strip()]
        return {
            'titulo': self.titulo_input.text(),
            'descripcion': self.descripcion_input.toPlainText(),
            'etiquetas': etiquetas
        } 