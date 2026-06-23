import sys
import qdarktheme
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from data_processor import NetworkDataProcessor

def main():
    app = QApplication(sys.argv)
    
    # Apply a modern dark theme style sheet automatically
    qdarktheme.setup_theme("dark")
    
    # Initialize components
    processor = NetworkDataProcessor()
    window = MainWindow(processor)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()