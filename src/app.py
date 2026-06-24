import sys
import qdarktheme
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Apply a modern dark theme style sheet automatically
    qdarktheme.setup_theme("dark")
    
    # Initialize components
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()