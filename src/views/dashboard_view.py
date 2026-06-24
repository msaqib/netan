from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QSplitter, QListWidget, QListWidgetItem, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.all_records = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Search bar setup
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter data (IP, payload, headers, logs)...")
        self.search_input.textChanged.connect(self.filter_records)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # 2. Main Body Splitter (Left: List, Right: Details)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # --- LEFT PANEL: Master List ---
        self.master_list = QListWidget()
        self.master_list.itemSelectionChanged.connect(self.display_selected_details)
        self.splitter.addWidget(self.master_list)

        # --- RIGHT PANEL: Detail View ---
        self.detail_container = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setContentsMargins(15, 0, 0, 0) # Pad slightly from the splitter line

        # Summary Metadata Cards
        self.lbl_target = QLabel("Select a record to view details")
        self.lbl_target.setStyleSheet("font-size: 18px; font-weight: bold; color: #1fb6ff;")
        
        self.lbl_meta = QLabel("")
        self.lbl_meta.setStyleSheet("font-size: 12px; color: #aaaaaa; margin-bottom: 5px;")
        
        self.lbl_dest = QLabel("")
        self.lbl_dest.setStyleSheet("font-size: 13px; font-weight: 500; margin-bottom: 15px;")
        self.lbl_dest.setWordWrap(True)

        self.detail_layout.addWidget(self.lbl_target)
        self.detail_layout.addWidget(self.lbl_meta)
        self.detail_layout.addWidget(self.lbl_dest)

        # Hops Detail Table
        self.hop_table = QTableWidget()
        self.hop_table.setColumnCount(3)
        self.hop_table.setHorizontalHeaderLabels(["Hop", "RTT (ms)", "IP Address"])
        self.hop_table.horizontalHeader().setStretchLastSection(True)
        self.detail_layout.addWidget(self.hop_table)

        # Add right panel to splitter and set initial proportional widths (e.g., 35% left, 65% right)
        self.splitter.addWidget(self.detail_container)
        self.splitter.setSizes([300, 600])

    def clear_dashboard(self):
        """Resets the dashboard view before a fresh file streaming starts."""
        self.all_records.clear()
        self.master_list.clear()
        self.hop_table.setRowCount(0)
        self.lbl_target.setText("Loading data stream...")

    def update_display(self, data_tuples):
        """Called by MainWindow controller once data is fully parsed and ready."""
        self.clear_dashboard()
        self.all_records = data_tuples
        self.populate_list(self.all_records)

    def populate_list(self, records):
        """Helper to safely build out list entries using the layout items."""
        self.master_list.clear()
        for idx, record in enumerate(records):
            # Format list card label string using Domain, Source, and Timestamp
            display_text = f"🌐 {record[0]}\n📅 {record[1][:10]} | 📍 {record[2].split()[-1]}"
            
            list_item = QListWidgetItem(display_text)
            # Stash the original index configuration reference inside the list item data
            list_item.setData(Qt.ItemDataRole.UserRole, idx) 
            self.master_list.addItem(list_item)

    def filter_records(self):
        """Triggers local search match loops over existing tuple collections."""
        query = self.search_input.text().lower()
        if not query:
            self.populate_list(self.all_records)
            return

        filtered = []
        for r in self.all_records:
            # Search across Target URL, Source details, or Destination info fields
            if query in r[0].lower() or query in r[2].lower() or query in r[3].lower():
                filtered.append(r)
        
        self.populate_list(filtered)

    def display_selected_details(self):
        """Fires when an item on the left panel is selected."""
        selected_items = self.master_list.selectedItems()
        if not selected_items:
            return

        # Retrieve the index back from the item's stored user data
        visible_item = selected_items[0]
        actual_index = visible_item.data(Qt.ItemDataRole.UserRole)
        
        # Pull correct matched index record based on filter scenarios
        query = self.search_input.text().lower()
        record = self.all_records[actual_index] if not query else self.master_list.itemWidget(visible_item) 
        
        # Fallback if complex matching relies heavily on active display lists
        current_list_idx = self.master_list.row(visible_item)
        # Re-derive record directly from what's currently showing in master list
        if query:
            # Reconstruct quick runtime map fallback
            filtered_list = [r for r in self.all_records if query in r[0].lower() or query in r[2].lower() or query in r[3].lower()]
            record = filtered_list[current_list_idx]

        # 1. Update Header text strings
        self.lbl_target.setText(record[0])
        self.lbl_meta.setText(f"🕒 Time: {record[1]}   |   📡 Source: {record[2]}")
        self.lbl_dest.setText(f"🎯 Target Endpoint:\n{record[3]}")

        # 2. Reset and populate Hop Table
        hop_nums = record[4]
        hop_ips = record[5]
        hop_rtts = record[6]

        self.hop_table.setRowCount(len(hop_nums))

        for row_idx in range(len(hop_nums)):
            hop_item = QTableWidgetItem(hop_nums[row_idx])
            rtt_item = QTableWidgetItem(f"{hop_rtts[row_idx]} ms")
            ip_item = QTableWidgetItem(hop_ips[row_idx])

            # Center text formatting alignments
            hop_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rtt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Highlight significant routing transit times (e.g., latency > 90ms via orange/red hints)
            try:
                rtt_val = float(hop_rtts[row_idx])
                if rtt_val > 150.0:
                    rtt_item.setForeground(QColor("#ff5555"))  # Severe latency spike (Global transit / Undersea leap)
                    rtt_item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
                elif rtt_val > 80.0:
                    rtt_item.setForeground(QColor("#ffb86c"))  # High warning latency (Regional/International cross)
            except ValueError:
                pass  # Handles missing measurements or timeout markers like '*' safely

            # Highlight final destination target record row
            if row_idx == len(hop_nums) - 1:
                ip_item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
                ip_item.setText(f"🏁 {hop_ips[row_idx]} [DEST]")

            self.hop_table.setItem(row_idx, 0, hop_item)
            self.hop_table.setItem(row_idx, 1, rtt_item)
            self.hop_table.setItem(row_idx, 2, ip_item)

        self.hop_table.resizeColumnsToContents()
    def append_single_record(self, record: tuple):
        """Appends a single newly-parsed record to the master list live."""
        try:
            # 1. Store it in our local memory state tracking array
            self.all_records.append(record)
            
            # 2. Add it directly to the UI list widget
            idx = len(self.all_records) - 1
            location = record[2].split()[-1] if record[2] else "Unknown"
            display_text = f"🌐 {record[0]}\n📅 {record[1][:10]} | 📍 {location}"
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, idx) 
            self.master_list.addItem(list_item)
        except Exception as e:
            # This ensures silent thread errors are forced into your console
            print(f"❌ Error rendering incoming record: {e}")