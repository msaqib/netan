from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtCore import pyqtSignal, Qt

class LoadView(QWidget):
    # Custom signal that sends the file path string when a file is chosen
    file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("Network Dataset Analyzer")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        
        self.subtitle = QLabel("Please select a network dataset file to begin analysis.")
        self.subtitle.setStyleSheet("font-size: 14px; color: #888; margin-bottom: 20px;")

        self.btn_load = QPushButton("Select & Load Dataset")
        self.btn_load.setFixedSize(200, 40)
        self.btn_load.clicked.connect(self.open_dialog)

        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_load, alignment=Qt.AlignmentFlag.AlignCenter)

    def open_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Network Data File", "", "All Files (*.*)"
        )
        if file_path:
            self.file_selected.emit(file_path)