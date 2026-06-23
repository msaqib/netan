import pandas as pd
class NetworkDataProcessor():
    def __init__(self):
        self.df = None
        self.data = []

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
        # print('Returning...')
        return (site, time, src, dest, hop_numbers, hop_ips, hop_rtt)


    def load_file(self, file_path: str) -> bool:
        try:
            # Adjust separation (sep) based on your file format (e.g., '\t', ',', or spaces)
            # self.df = pd.read_csv(filepath, sep=None, engine='python')
            data = []
            with open(file_path, "r") as f:
                f.readline()
                next = f.readline()
                tokens = next.split()
                count = tokens[0]
                f.readline()
                f.readline()
                done = False
                while not done:
                    # next = f.readline()
                    tup = self.read_trace(f)
                    # print(tup)
                    self.data.append(tup)
                    if not f.readline():
                        done = True

                
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    def get_all_data(self) -> pd.DataFrame:
        """Returns the complete dataset."""
        # return self.df if self.df is not None else pd.DataFrame()
        return self.data

    def filter_data(self, search_term: str, column_name: str = None) -> pd.DataFrame:
        """Filters rows containing the search term."""
        if self.df is None or not search_term:
            return self.get_all_data()

        # Case-insensitive search across a specific column or the entire dataframe
        if column_name and column_name in self.df.columns:
            mask = self.df[column_name].astype(str).str.contains(search_term, case=False, na=False)
            return self.df[mask]
        else:
            # Search globally across all columns
            mask = self.df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            return self.df[mask]