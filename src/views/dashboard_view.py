from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QSplitter, QListWidget, QListWidgetItem, QLabel, QFrame, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.all_records = []
        self.known_sites = set()
        self.known_cities = set()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Search bar setup
        filter_layout = QHBoxLayout()

        # 1. Text Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter data (IP, operator, logs)...")
        self.search_input.textChanged.connect(self.filter_records)
        filter_layout.addWidget(self.search_input, stretch=2)

        # 🚀 2. Site Dropdown Selector
        self.site_dropdown = QComboBox()
        self.site_dropdown.addItem("All Sites")  # Default placeholder option
        self.site_dropdown.currentTextChanged.connect(self.filter_records) # Trigger filter on change
        filter_layout.addWidget(self.site_dropdown, stretch=1)

        # 🚀 2.1 City Dropdown Selector
        self.city_dropdown = QComboBox()
        self.city_dropdown.addItem("All cities")  # Default placeholder option
        self.city_dropdown.currentTextChanged.connect(self.filter_records) # Trigger filter on change
        filter_layout.addWidget(self.city_dropdown, stretch=1)

        main_layout.addLayout(filter_layout)

        # --- Main Body Splitter (Left: List, Right: Details) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Left List Pane
        self.master_list = QListWidget()
        self.master_list.itemSelectionChanged.connect(self.display_selected_details)
        self.splitter.addWidget(self.master_list)

        # Right Detail Container (Metadata + Table)
        self.detail_container = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setContentsMargins(15, 0, 0, 0)

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

        self.hop_table = QTableWidget()
        self.hop_table.setColumnCount(3)
        self.hop_table.setHorizontalHeaderLabels(["Hop", "RTT (ms)", "IP Address"])
        self.hop_table.horizontalHeader().setStretchLastSection(True)
        self.detail_layout.addWidget(self.hop_table)

        self.splitter.addWidget(self.detail_container)
        self.splitter.setSizes([300, 600])

    def clear_dashboard(self):
        """Resets the dashboard view and locks the filter controls."""
        self.all_records.clear()
        self.master_list.clear()
        self.known_sites.clear()
        self.known_cities.clear()
        
        self.site_dropdown.clear()
        self.site_dropdown.addItem("All Sites")

        self.city_dropdown.clear()
        self.city_dropdown.addItem("All Cities")
        
        # 🔒 Lock controls so user cannot click them while data streams in
        self.search_input.setEnabled(False)
        self.site_dropdown.setEnabled(False)
        self.city_dropdown.setEnabled(False)
        
        self.hop_table.setRowCount(0)
        self.lbl_target.setText("Loading data stream... Please wait.")

    def update_display(self, data_tuples):
        """Called by MainWindow controller once data is fully parsed and ready."""
        self.clear_dashboard()
        self.all_records = data_tuples
        self.populate_list(self.all_records)

    def populate_list(self, records):
        """Helper to cleanly rebuild the master list view based on filtered subsets."""
        self.master_list.clear()
        for record in records:
            # Re-map the filtered items back to their original position index in self.all_records
            try:
                original_idx = self.all_records.index(record)
                location = record[2].split()[-1] if record[2] else "Unknown"
                display_text = f"🌐 {record[0]}\n📅 {record[1][:10]} | 📍 {location}"
                
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, original_idx) 
                self.master_list.addItem(list_item)
            except ValueError:
                continue

    def filter_records(self):
        """Triggers multi-criteria filtering combining search text and dropdown state."""
        text_query = self.search_input.text().lower()
        selected_site = self.site_dropdown.currentText()
        selected_city = self.city_dropdown.currentText()

        filtered = []
        for r in self.all_records:
            # 1. Evaluate Text Search constraint
            match_text = not text_query or (
                text_query in r[0].lower() or 
                text_query in r[2].lower() or 
                text_query in r[3].lower()
            )
            
            match_site = (selected_site == "All Sites") or (r[0] == selected_site)
            rec_city = r[2].split()[-1] if r[2] else "Unknown"
            match_city = (selected_city == "All Cities") or (rec_city == selected_city)

            # 2. Evaluate Dropdown selection constraint
            match_dropdown = (selected_site == "All Sites") or (r[0] == selected_site)

            # Combined boolean filter matrix evaluation
            if match_text and match_site and match_city:
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
        """Appends incoming records sequentially to the UI without active filter checks."""
        try:
            self.all_records.append(record)
            
            # Extract unique sites for the dropdown options behind the scenes
            site_name = record[0]
            if site_name and site_name not in self.known_sites:
                self.known_sites.add(site_name)
                self.site_dropdown.addItem(site_name)

            city_name = record[2].split()[-1] if record[2] else "Unknown"
            if city_name and city_name not in self.known_cities:
                self.known_cities.add(city_name)
                self.city_dropdown.addItem(city_name)

            # Draw every item to the list sequentially during the stream
            idx = len(self.all_records) - 1
            location = record[2].split()[-1] if record[2] else "Unknown"
            display_text = f"🌐 {record[0]}\n📅 {record[1][:10]} | 📍 {location}"
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, idx) 
            self.master_list.addItem(list_item)
                
        except Exception as e:
            print(f"❌ Error rendering incoming record: {e}")

    def unlock_ui(self):
        """Called when file reading is 100% complete to restore control interaction."""
        self.search_input.setEnabled(True)
        self.site_dropdown.setEnabled(True)
        self.city_dropdown.setEnabled(True)
        self.lbl_target.setText("Select a record to view details")