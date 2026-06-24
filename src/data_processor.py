import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal
import time

class FileLoaderWorker(QThread):
    # This signal emits a single tuple whenever a new data block is parsed
    record_parsed = pyqtSignal(object)
    
    # This signal tells the UI when the file reading is 100% complete
    finished_loading = pyqtSignal()

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.data = []
        self.df = None

    def read_trace(self, f):
        next = f.readline()
        tokens = next.split()
        site = tokens[0]
        next = f.readline()
        tokens = next.split()
        time = tokens[1]
        next = f.readline()
        tokens = next.split()
        src = " ".join(tokens[6:])
        next = f.readline()
        tokens = next.split()
        dest = " ".join(tokens[1:])
        f.readline()
        f.readline()
        next = f.readline()
        hop_numbers = []
        hop_ips = []
        hop_rtt = []
        while len(next) > 1:
            tokens = next.split()
            # print(tokens)
            hop_numbers.append(tokens[0])
            hop_rtt.append(tokens[1])
            hop_ips.append(tokens[2])
            next = f.readline()
        return (site, time, src, dest, hop_numbers, hop_ips, hop_rtt)

    def run(self):
        """This method runs entirely inside a separate background thread."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                f.readline()
                next = f.readline()
                tokens = next.split()
                count = tokens[0]
                f.readline()
                f.readline()
                done = False
                while not done:
                    tup = self.read_trace(f)
                    self.data.append(tup)
                    self.record_parsed.emit(tup)
                    if not f.readline():
                        done = True
                
                    
        except Exception as e:
            print(f"Error reading file in background thread: {e}")
        
        finally:
            # Tell the main window we are completely done
            self.finished_loading.emit()