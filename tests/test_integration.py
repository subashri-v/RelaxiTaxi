import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ride_utils import calculate_distance, calculate_fare

def test_end_to_end_distance_and_fare():
    start = (12.9716, 77.5946)
    end = (13.0827, 80.2707)
    distance = calculate_distance(start, end)
    fare = calculate_fare(distance, ac=True)
    assert fare > 0
    assert distance > 0
