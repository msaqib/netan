import pandas as pd
class NetworkDataProcessor():
    def __init__(self):
        self.df = None
    def load_file(self, file_path: str) -> bool:
        try:
            # Adjust separation (sep) based on your file format (e.g., '\t', ',', or spaces)
            self.df = pd.read_csv(filepath, sep=None, engine='python')
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    def get_all_data(self) -> pd.DataFrame:
        """Returns the complete dataset."""
        return self.df if self.df is not None else pd.DataFrame()

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