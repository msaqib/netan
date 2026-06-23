from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from views.load_view import LoadView
from views.dashboard_view import DashboardView
from data_processor import NetworkDataProcessor

class MainWindow(QMainWindow):
    def __init__(self, processor: NetworkDataProcessor):
        super().__init__()
        self.processor = processor
        self.setWindowTitle("Network Analyzer")
        self.resize(900, 650)

        # The stack container that holds our screen variants
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create views
        self.load_view = LoadView()
        self.dashboard_view = DashboardView()

        # Add views to the stack
        self.stacked_widget.addWidget(self.load_view)      # Index 0
        self.stacked_widget.addWidget(self.dashboard_view) # Index 1

        # Connect the load view's signal to our main window routing function
        self.load_view.file_selected.connect(self.handle_file_loading)

    def handle_file_loading(self, file_path: str):
        # We invoke your data processor (which we will build later)
        success = self.processor.load_file(file_path)
        
        if success:
            # Transition smoothly to the dashboard layout view
            self.stacked_widget.setCurrentIndex(1)
            # Update dashboard view table with data
            self.dashboard_view.update_display(self.processor.get_all_data())
        else:
            QMessageBox.critical(self, "Error", "Failed to parse custom network file format.")