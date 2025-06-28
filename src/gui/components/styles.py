"""
Estilos para la interfaz gráfica de StockPrep Pro
"""

def get_win11_style() -> str:
    """Retorna el estilo CSS para Windows 11"""
    return """
    /* Estilo principal de la aplicación */
    QMainWindow {
        background-color: #F5F5F5;
        color: #2B2B2B;
    }
    
    /* Barra de menú */
    QMenuBar {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E0E0E0;
        padding: 4px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QMenuBar::item:selected {
        background-color: #E3F2FD;
        color: #1976D2;
    }
    
    /* Pestañas */
    QTabWidget::pane {
        border: 1px solid #E0E0E0;
        background-color: #FFFFFF;
        border-radius: 8px;
    }
    
    QTabBar::tab {
        background-color: #F5F5F5;
        color: #666666;
        padding: 12px 20px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 500;
    }
    
    QTabBar::tab:selected {
        background-color: #FFFFFF;
        color: #1976D2;
        border-bottom: 2px solid #1976D2;
    }
    
    QTabBar::tab:hover {
        background-color: #E3F2FD;
        color: #1976D2;
    }
    
    /* Botones */
    QPushButton {
        background-color: #1976D2;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 14px;
    }
    
    QPushButton:hover {
        background-color: #1565C0;
    }
    
    QPushButton:pressed {
        background-color: #0D47A1;
    }
    
    QPushButton:disabled {
        background-color: #BDBDBD;
        color: #757575;
    }
    
    /* Botón de éxito */
    QPushButton.Success {
        background-color: #4CAF50;
    }
    
    QPushButton.Success:hover {
        background-color: #45A049;
    }
    
    QPushButton.Success:pressed {
        background-color: #3D8B40;
    }
    
    /* Botón de carga */
    QPushButton.Loading {
        background-color: #FF9800;
    }
    
    QPushButton.Loading:hover {
        background-color: #F57C00;
    }
    
    /* Campos de texto */
    QTextEdit, QLineEdit {
        background-color: #FFFFFF;
        border: 2px solid #E0E0E0;
        border-radius: 6px;
        padding: 8px;
        font-size: 14px;
    }
    
    QTextEdit:focus, QLineEdit:focus {
        border-color: #1976D2;
    }
    
    /* Barras de progreso */
    QProgressBar {
        border: 2px solid #E0E0E0;
        border-radius: 6px;
        text-align: center;
        background-color: #F5F5F5;
    }
    
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 4px;
    }
    
    /* Listas */
    QListWidget {
        background-color: #FFFFFF;
        border: 2px solid #E0E0E0;
        border-radius: 6px;
        padding: 4px;
    }
    
    QListWidget::item {
        padding: 8px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QListWidget::item:selected {
        background-color: #E3F2FD;
        color: #1976D2;
    }
    
    QListWidget::item:hover {
        background-color: #F5F5F5;
    }
    
    /* Tablas */
    QTableWidget {
        background-color: #FFFFFF;
        border: 2px solid #E0E0E0;
        border-radius: 6px;
        gridline-color: #E0E0E0;
    }
    
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #F0F0F0;
    }
    
    QTableWidget::item:selected {
        background-color: #E3F2FD;
        color: #1976D2;
    }
    
    /* Checkboxes y Radio buttons */
    QCheckBox, QRadioButton {
        spacing: 8px;
        font-size: 14px;
    }
    
    QCheckBox::indicator, QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #E0E0E0;
        border-radius: 3px;
        background-color: #FFFFFF;
    }
    
    QCheckBox::indicator:checked {
        background-color: #1976D2;
        border-color: #1976D2;
    }
    
    QRadioButton::indicator:checked {
        background-color: #1976D2;
        border-color: #1976D2;
        border-radius: 9px;
    }
    
    /* Grupos */
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
    
    /* Etiquetas */
    QLabel {
        color: #333333;
        font-size: 14px;
    }
    
    /* Barra de estado */
    QStatusBar {
        background-color: #FFFFFF;
        border-top: 1px solid #E0E0E0;
        padding: 4px;
    }
    
    QStatusBar::item {
        border: none;
    }
    """

def get_dark_style() -> str:
    """Retorna el estilo CSS para modo oscuro"""
    return """
    /* Estilo oscuro para la aplicación */
    QMainWindow {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    
    /* Barra de menú */
    QMenuBar {
        background-color: #2D2D2D;
        border-bottom: 1px solid #404040;
        padding: 4px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QMenuBar::item:selected {
        background-color: #404040;
        color: #FFFFFF;
    }
    
    /* Pestañas */
    QTabWidget::pane {
        border: 1px solid #404040;
        background-color: #2D2D2D;
        border-radius: 8px;
    }
    
    QTabBar::tab {
        background-color: #404040;
        color: #CCCCCC;
        padding: 12px 20px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 500;
    }
    
    QTabBar::tab:selected {
        background-color: #2D2D2D;
        color: #FFFFFF;
        border-bottom: 2px solid #0078D4;
    }
    
    /* Botones */
    QPushButton {
        background-color: #0078D4;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 14px;
    }
    
    QPushButton:hover {
        background-color: #106EBE;
    }
    
    QPushButton:pressed {
        background-color: #005A9E;
    }
    
    /* Campos de texto */
    QTextEdit, QLineEdit {
        background-color: #2D2D2D;
        border: 2px solid #404040;
        border-radius: 6px;
        padding: 8px;
        font-size: 14px;
        color: #FFFFFF;
    }
    
    QTextEdit:focus, QLineEdit:focus {
        border-color: #0078D4;
    }
    
    /* Grupos */
    QGroupBox {
        font-weight: bold;
        border: 2px solid #404040;
        border-radius: 8px;
        margin-top: 1ex;
        padding: 10px;
        background-color: #2D2D2D;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        color: #0078D4;
    }
    """ 