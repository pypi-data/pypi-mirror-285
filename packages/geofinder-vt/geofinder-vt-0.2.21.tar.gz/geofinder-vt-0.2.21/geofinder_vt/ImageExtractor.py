import os
import shutil
from datetime import datetime
import pandas as pd
from geopy.distance import geodesic

class ImageExtractor:
    def __init__(self, input_csv, dir_prefix):
        self.input_csv = input_csv
        self.dir_prefix = dir_prefix
        self.df = pd.read_csv(input_csv)
        self.base_path = "."

    def list_relevant_folders(self):
        all_items = os.listdir(self.base_path)
        folders = [item for item in all_items if os.path.isdir(os.path.join(self.base_path, item)) and item.startswith(self.dir_prefix)]
        return folders

    def consolidate_files(self, folders):
        all_files = []
        for folder in folders:
            full_folder_path = os.path.join(self.base_path, folder)
            files = os.listdir(full_folder_path)
            files = [f"{folder}/{file}" for file in files if 'metadata' not in file]
            all_files.extend(files)
        return all_files

    def prepare_dataframe(self, all_files):
        df = pd.DataFrame(all_files, columns=["filename"])
        df[["folder", "fname"]] = df["filename"].str.split('/', expand=True)
        df[["dummy", "timestamp", "latitude", "longitude"]] = df['fname'].str.split('_', expand=True)
        df['longitude'] = df['longitude'].str.replace('.jpg', '')
        df = df[df['latitude'].notna()]
        return df

    def find_closest_coords(self, row, ref_df):
        closest_distance = float('inf')
        closest_file = None
        for _, row_df in ref_df.iterrows():
            distance = geodesic((float(row_df['latitude']), float(row_df['longitude'])), (float(row['lat']), float(row['lon']))).kilometers
            if distance < 0.02 and distance < closest_distance:
                closest_file = row_df['filename']
                closest_distance = distance
        return [closest_file]

    def process_files(self, ref_df):
        self.df['closest_coords'] = self.df.apply(lambda row: self.find_closest_coords(row, ref_df), axis=1)
        unique_files = set(sum(self.df['closest_coords'].tolist(), []))
        return unique_files

    def move_files(self, unique_files):
        destination_path = f"results_{datetime.now().timestamp()}"
        os.mkdir(destination_path)
        for file in unique_files:
            if file:
                shutil.copy(file, destination_path)
        return destination_path

    def run(self):
        folders = self.list_relevant_folders()
        all_files = self.consolidate_files(folders)
        ref_df = self.prepare_dataframe(all_files)
        unique_files = self.process_files(ref_df)
        destination = self.move_files(unique_files)
        self.df.to_csv('prelim_output.csv')
        return destination

# Example usage
if __name__ == "__main__":
    input_csv = "example.csv"  # Path to your CSV file containing geolocation data
    directory_prefix = "GH"  # Directory prefix to filter relevant folders
    extractor = ImageExtractor(input_csv, directory_prefix)
    destination_path = extractor.run()
    print(f"Processed files moved to: {destination_path}")
