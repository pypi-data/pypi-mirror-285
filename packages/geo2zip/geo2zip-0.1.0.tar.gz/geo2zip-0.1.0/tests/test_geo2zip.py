import os
import pytest
from geo2zip import Geo2Zip

# Defined the coordinates for some well-known American cities and their expected ZIP codes
# This can be extended if needed
cities = [
    ("New York, NY", 40.7128, -74.0060, "10007"),
    ("Los Angeles, CA", 34.0522, -118.2437, "90013"),
    ("Chicago, IL", 41.8781, -87.6298, "60604"),
    ("Houston, TX", 29.7604, -95.3698, "77002"),
    ("Phoenix, AZ", 33.4484, -112.0740, "85003"),
    ("Philadelphia, PA", 39.9526, -75.1652, "19102"),
    ("San Antonio, TX", 29.4241, -98.4936, "78205"),
    ("San Diego, CA", 32.7157, -117.1611, "92132"),
    ("Dallas, TX", 32.7767, -96.7970, "75270"),
    ("San Francisco, CA", 37.7749, -122.4194, "94102"),
]

@pytest.fixture(scope="module")
def geo2zip():
    file_path = os.path.join(os.path.dirname(__file__), '../geo2zip/data/geo2zip.csv')
    return Geo2Zip(file_path)

@pytest.mark.parametrize("city, lat, lon, expected_zip", cities)
def test_find_closest_zip(geo2zip, city, lat, lon, expected_zip):
    closest_zip = geo2zip.find_closest_zip(lat, lon)
    assert closest_zip == expected_zip, f"Expected {expected_zip} but got {closest_zip} for {city}"

