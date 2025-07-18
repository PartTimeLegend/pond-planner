import os
import sys

import pytest

# Add the parent directory to the Python path so tests can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_pond_dimensions():
    """Fixture providing sample pond dimensions."""
    from PondDimensions import PondDimensions

    return PondDimensions(5.0, 3.0, 1.5, "rectangular")


@pytest.fixture
def sample_fish_stock():
    """Fixture providing sample fish stock."""
    return {"goldfish": 10, "koi": 3, "shubunkin": 5}


@pytest.fixture
def large_pond_dimensions():
    """Fixture providing large pond dimensions."""
    from PondDimensions import PondDimensions

    return PondDimensions(10.0, 8.0, 2.0, "oval")
