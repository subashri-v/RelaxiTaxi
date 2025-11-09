import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ride_utils import calculate_distance, calculate_fare, get_coordinates

def test_calculate_fare_non_ac():
    assert calculate_fare(10, ac=False) == 40 + 15 * 10

def test_calculate_fare_ac():
    assert calculate_fare(5, ac=True) == 60 + 20 * 5

def test_negative_distance_raises():
    with pytest.raises(ValueError):
        calculate_fare(-5)

def test_calculate_distance():
    d = calculate_distance((12.9716, 77.5946), (13.0827, 80.2707))
    assert abs(d - 291.0) < 1.0  # within 1 km tolerance

def test_calculate_distance_invalid_input():
    """Test distance calculation when invalid coordinates are given."""
    d = calculate_distance(("invalid", "coords"), (13.0, 77.0))
    assert d is None or isinstance(d, (int, float))

def test_calculate_fare_invalid_type():
    """Test that calculate_fare raises TypeError for invalid distance input."""
    with pytest.raises(TypeError):
        calculate_fare("Luxury", 10)

def test_calculate_distance_empty_coords():
    """Test distance calculation when one or both coordinates are missing."""
    assert calculate_distance(None, (13.0, 77.0)) is None
    assert calculate_distance((12.9, 77.5), None) is None

def test_calculate_distance_exception_handling(monkeypatch):
    """Force an exception inside calculate_distance to cover the except block."""
    from ride_utils import calculate_distance

    # Monkeypatch geodesic to raise an exception
    def mock_geodesic(a, b):
        raise Exception("Simulated failure")

    import ride_utils
    monkeypatch.setattr(ride_utils, "geodesic", mock_geodesic)

    # Now call it — should handle the exception and return None
    result = calculate_distance((12.9, 77.5), (13.0, 80.2))
    assert result is None

class MockLocation:
    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

def test_get_coordinates_success(monkeypatch):
    """Test get_coordinates returns correct tuple when location is found."""
    mock_location = MockLocation(12.9716, 77.5946)

    class MockGeolocator:
        def geocode(self, name):
            return mock_location

    monkeypatch.setattr("ride_utils.Nominatim", lambda **kwargs: MockGeolocator())

    coords = get_coordinates("Bangalore")
    assert coords == (12.9716, 77.5946)

def test_get_coordinates_failure(monkeypatch):
    """Test get_coordinates returns None when location is not found."""
    class MockGeolocator:
        def geocode(self, name):
            return None

    monkeypatch.setattr("ride_utils.Nominatim", lambda **kwargs: MockGeolocator())

    coords = get_coordinates("UnknownPlace")
    assert coords is None

