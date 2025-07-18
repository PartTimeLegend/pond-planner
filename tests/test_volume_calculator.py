import math
from unittest.mock import Mock

import pytest

from calculators.VolumeCalculator import VolumeCalculator
from PondDimensions import PondDimensions


class TestVolumeCalculator:
    """Test cases for VolumeCalculator class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock shape repository
        self.mock_shape_repo = Mock()
        self.mock_shape_repo.shape_exists.return_value = True
        self.mock_shape_repo.get_validation_rules.return_value = {
            "min_dimensions": {"length": 0.1, "width": 0.1, "depth": 0.05},
            "max_dimensions": {"length": 1000.0, "width": 1000.0, "depth": 100.0},
        }

        self.calculator = VolumeCalculator(self.mock_shape_repo)

    def test_rectangular_volume(self):
        """Test volume calculation for rectangular pond."""
        self.mock_shape_repo.get_shape_by_key.return_value = {
            "formula_type": "simple",
            "multiplier": 1.0,
        }

        dimensions = PondDimensions(5.0, 3.0, 1.5, "rectangular")
        volume = self.calculator.calculate_volume_liters(dimensions)

        # 5 × 3 × 1.5 = 22.5 m³ = 22,500 liters
        assert volume == 22500.0

    def test_circular_volume(self):
        """Test volume calculation for circular pond."""
        self.mock_shape_repo.get_shape_by_key.return_value = {
            "formula_type": "circular",
            "multiplier": 1.0,
        }

        dimensions = PondDimensions(0.0, 4.0, 1.0, "circular")  # width = diameter
        volume = self.calculator.calculate_volume_liters(dimensions)

        # π × (4/2)² × 1.0 = π × 4 × 1.0 = 4π m³ ≈ 12,566 liters
        expected = math.pi * 4 * 1.0 * 1000
        assert abs(volume - expected) < 0.1

    def test_oval_volume(self):
        """Test volume calculation for oval pond."""
        self.mock_shape_repo.get_shape_by_key.return_value = {
            "formula_type": "elliptical",
            "multiplier": 1.0,
        }

        dimensions = PondDimensions(6.0, 4.0, 1.0, "oval")
        volume = self.calculator.calculate_volume_liters(dimensions)

        # π × (6/2) × (4/2) × 1.0 = π × 3 × 2 × 1.0 = 6π m³
        expected = math.pi * 6 * 1.0 * 1000
        assert abs(volume - expected) < 0.1

    def test_triangular_volume(self):
        """Test volume calculation for triangular pond."""
        self.mock_shape_repo.get_shape_by_key.return_value = {
            "formula_type": "triangular",
            "multiplier": 1.0,
        }

        dimensions = PondDimensions(6.0, 4.0, 1.0, "triangular")
        volume = self.calculator.calculate_volume_liters(dimensions)

        # 0.5 × 6 × 4 × 1.0 = 12 m³ = 12,000 liters
        assert volume == 12000.0

    def test_kidney_volume_with_multiplier(self):
        """Test volume calculation for kidney-shaped pond with multiplier."""
        self.mock_shape_repo.get_shape_by_key.return_value = {
            "formula_type": "approximation",
            "multiplier": 0.75,
        }

        dimensions = PondDimensions(5.0, 3.0, 1.0, "kidney")
        volume = self.calculator.calculate_volume_liters(dimensions)

        # 5 × 3 × 1.0 × 0.75 = 11.25 m³ = 11,250 liters
        assert volume == 11250.0

    def test_hexagonal_volume(self):
        """Test volume calculation for hexagonal pond."""
        self.mock_shape_repo.get_shape_by_key.return_value = {
            "formula_type": "polygon",
            "multiplier": 1.0,
            "area_formula": "(3 * sqrt(3) / 2) * width^2",
        }

        dimensions = PondDimensions(0.0, 2.0, 1.0, "hexagonal")
        volume = self.calculator.calculate_volume_liters(dimensions)

        # (3 × √3 / 2) × 2² × 1.0 = 6√3 m³
        expected = (3 * math.sqrt(3) / 2) * 4 * 1.0 * 1000
        assert abs(volume - expected) < 0.1

    def test_validation_none_dimensions(self):
        """Test that None dimensions raise ValueError."""
        with pytest.raises(ValueError, match="Pond dimensions cannot be None"):
            self.calculator.calculate_volume_liters(None)

    def test_validation_wrong_type(self):
        """Test that wrong type raises TypeError."""
        with pytest.raises(TypeError, match="Expected PondDimensions object"):
            self.calculator.calculate_volume_liters("not_dimensions")

    def test_validation_no_shape(self):
        """Test that missing shape raises ValueError."""
        dimensions = PondDimensions(5.0, 3.0, 1.5, "")

        with pytest.raises(ValueError, match="Pond shape must be specified"):
            self.calculator.calculate_volume_liters(dimensions)

    def test_validation_unknown_shape(self):
        """Test that unknown shape raises ValueError."""
        self.mock_shape_repo.shape_exists.return_value = False
        self.mock_shape_repo.get_shape_keys.return_value = ["rectangular", "circular"]

        dimensions = PondDimensions(5.0, 3.0, 1.5, "unknown")

        with pytest.raises(ValueError, match="Unknown shape 'unknown'"):
            self.calculator.calculate_volume_liters(dimensions)

    def test_validation_dimensions_too_small(self):
        """Test that dimensions below minimum raise ValueError."""
        dimensions = PondDimensions(0.05, 3.0, 1.5, "rectangular")

        with pytest.raises(ValueError, match="Length must be at least 0.1 meters"):
            self.calculator.calculate_volume_liters(dimensions)

    def test_validation_dimensions_too_large(self):
        """Test that dimensions above maximum raise ValueError."""
        dimensions = PondDimensions(1500.0, 3.0, 1.5, "rectangular")

        with pytest.raises(ValueError, match="Length cannot exceed 1000.0 meters"):
            self.calculator.calculate_volume_liters(dimensions)

    def test_negative_volume_raises_error(self):
        """Test that negative calculated volume raises ValueError."""
        self.mock_shape_repo.get_shape_by_key.return_value = {
            "formula_type": "simple",
            "multiplier": -1.0,  # This would create negative volume
        }

        dimensions = PondDimensions(5.0, 3.0, 1.5, "rectangular")

        with pytest.raises(ValueError, match="Calculated volume must be positive"):
            self.calculator.calculate_volume_liters(dimensions)
