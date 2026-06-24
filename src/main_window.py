from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from views.load_view import LoadView
from views.dashboard_view import DashboardView
from data_processor import FileLoaderWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

        # 1. Switch views to the dashboard instantly so the user sees updates live
        self.stacked_widget.setCurrentIndex(1)
        self.dashboard_view.clear_dashboard()
        
        # 2. Instantiate our background thread worker
        self.worker = FileLoaderWorker(file_path)
        
        from PyQt6.QtCore import Qt
        self.worker.record_parsed.connect(
            self.dashboard_view.append_single_record, 
            Qt.ConnectionType.QueuedConnection
        )
        self.worker.finished_loading.connect(self.on_loading_complete)

        # 4. Start the thread!
        self.worker.start()
    
    def on_loading_complete(self):
        # Optional housecleaning once the entire file finishes streaming
        self.dashboard_view.lbl_target.setText("Select a record to view details")
        # Clean up the thread object safely
        self.worker.deleteLater()