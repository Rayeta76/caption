"""
Widget de estadísticas para la interfaz gráfica
"""
from typing import Dict
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QGroupBox, QLabel

class ModernStatsWidget(QWidget):
    """Widget moderno para mostrar estadísticas"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # Estilo moderno
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 10px;
                background-color: #FAFAFA;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2B579A;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
        """)
        
        # Estadísticas de procesamiento
        processing_group = QGroupBox("📊 Estadísticas de Procesamiento")
        processing_layout = QVBoxLayout()
        
        self.total_images_label = QLabel("Imágenes procesadas: 0")
        self.success_rate_label = QLabel("Tasa de éxito: 100%")
        self.avg_time_label = QLabel("Tiempo promedio: 0s")
        
        processing_layout.addWidget(self.total_images_label)
        processing_layout.addWidget(self.success_rate_label)
        processing_layout.addWidget(self.avg_time_label)
        processing_group.setLayout(processing_layout)
        
        # Estadísticas de base de datos
        db_group = QGroupBox("🗄️ Base de Datos")
        db_layout = QVBoxLayout()
        
        self.db_records_label = QLabel("Registros: 0")
        self.db_size_label = QLabel("Tamaño: 0 KB")
        self.last_update_label = QLabel("Última actualización: Nunca")
        
        db_layout.addWidget(self.db_records_label)
        db_layout.addWidget(self.db_size_label)
        db_layout.addWidget(self.last_update_label)
        db_group.setLayout(db_layout)
        
        layout.addWidget(processing_group, 0, 0)
        layout.addWidget(db_group, 0, 1)
        
        self.setLayout(layout)
    
    def update_stats(self, stats: Dict):
        """Actualiza las estadísticas mostradas"""
        if 'total_images' in stats:
            self.total_images_label.setText(f"Imágenes procesadas: {stats['total_images']}")
        if 'success_rate' in stats:
            self.success_rate_label.setText(f"Tasa de éxito: {stats['success_rate']:.1f}%")
        if 'avg_time' in stats:
            self.avg_time_label.setText(f"Tiempo promedio: {stats['avg_time']:.1f}s")
        if 'db_records' in stats:
            self.db_records_label.setText(f"Registros: {stats['db_records']}")
        if 'db_size' in stats:
            self.db_size_label.setText(f"Tamaño: {stats['db_size']} KB")
        if 'last_update' in stats:
            self.last_update_label.setText(f"Última actualización: {stats['last_update']}") 