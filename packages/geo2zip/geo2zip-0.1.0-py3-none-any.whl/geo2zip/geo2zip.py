import csv
import os

from scipy.spatial import KDTree

class Geo2Zip:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), 'data/geo2zip.csv')
        self.data = self._read_csv(file_path)
        self.tree, self.geoids = self._build_kdtree(self.data)
    
    def _read_csv(self, file_path):
        try:
            with open(file_path, mode='r') as csvfile:
                reader = csv.DictReader(csvfile) 
                data = [row for row in reader]
            return data
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            raise
    
    def _build_kdtree(self, data):
        coordinates = []
        geoids = []
        for row in data:
            try:
                lat = float(row['INTPTLAT'])
                lon = float(row['INTPTLONG'])
                coordinates.append((lat, lon))
                geoids.append(row['GEOID'])
            except ValueError:
                # Skip rows with invalid coordinates
                continue
        tree = KDTree(coordinates)
        return tree, geoids
    
    def find_closest_zip(self, lat, lon):
        distance, index = self.tree.query((lat, lon))
        closest_zip = self.geoids[index]
        return closest_zip

