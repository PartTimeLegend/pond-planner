from unittest.mock import Mock

import pytest

from calculators.StockingCalculator import StockingCalculator
from Fish import Fish


class TestStockingCalculator:
    """Test cases for StockingCalculator class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock fish repository
        self.mock_fish_repo = Mock()

        # Create mock fish data
        self.goldfish = Fish("Goldfish", 20, 1.0, 75)
        self.koi = Fish("Koi", 60, 2.5, 950)
        self.shubunkin = Fish("Shubunkin", 25, 1.1, 190)

        self.mock_fish_repo.get_fish_by_key.side_effect = self._get_fish_by_key
        self.mock_fish_repo.get_all_fish.return_value = {
            "goldfish": self.goldfish,
            "koi": self.koi,
            "shubunkin": self.shubunkin,
        }

        self.calculator = StockingCalculator(self.mock_fish_repo)

    def _get_fish_by_key(self, key):
        """Helper to simulate fish repository lookup."""
        fish_map = {
            "goldfish": self.goldfish,
            "koi": self.koi,
            "shubunkin": self.shubunkin,
        }
        if key in fish_map:
            return fish_map[key]
        raise KeyError(f"Fish key '{key}' not found")

    def test_calculate_required_volume_empty_stock(self):
        """Test required volume calculation with empty stock."""
        result = self.calculator.calculate_required_volume({})
        assert result == 0.0

    def test_calculate_required_volume_single_fish(self):
        """Test required volume calculation with single fish type."""
        stock = {"goldfish": 5}
        result = self.calculator.calculate_required_volume(stock)

        # 5 × 75L = 375L
        assert result == 375.0

    def test_calculate_required_volume_multiple_fish(self):
        """Test required volume calculation with multiple fish types."""
        stock = {"goldfish": 5, "koi": 2}
        result = self.calculator.calculate_required_volume(stock)

        # 5 × 75L + 2 × 950L = 375 + 1900 = 2275L
        assert result == 2275.0

    def test_calculate_required_volume_zero_quantity(self):
        """Test that zero or negative quantities are ignored."""
        stock = {"goldfish": 5, "koi": 0, "shubunkin": -1}
        result = self.calculator.calculate_required_volume(stock)

        # Only goldfish should count: 5 × 75L = 375L
        assert result == 375.0

    def test_calculate_required_volume_unknown_fish(self):
        """Test that unknown fish type raises KeyError."""
        stock = {"unknown_fish": 5}

        with pytest.raises(KeyError):
            self.calculator.calculate_required_volume(stock)

    def test_calculate_required_volume_invalid_fish_data(self):
        """Test handling of fish with invalid min_liters_per_fish."""
        # Create fish with None value
        invalid_fish = Fish("Invalid", 20, 1.0, None)

        # Update the mock to return invalid fish for specific key
        def mock_get_fish_by_key(key):
            if key == "invalid_fish":
                return invalid_fish
            return self._get_fish_by_key(key)

        self.mock_fish_repo.get_fish_by_key.side_effect = mock_get_fish_by_key

        stock = {"invalid_fish": 5}

        with pytest.raises(
            ValueError, match="invalid min_liters_per_fish value \\(None\\)"
        ):
            self.calculator.calculate_required_volume(stock)

    def test_calculate_bioload_empty_stock(self):
        """Test bioload calculation with empty stock."""
        result = self.calculator.calculate_bioload({})
        assert result == 0.0

    def test_calculate_bioload_single_fish(self):
        """Test bioload calculation with single fish type."""
        stock = {"goldfish": 5}
        result = self.calculator.calculate_bioload(stock)

        # 5 × 1.0 = 5.0
        assert result == 5.0

    def test_calculate_bioload_multiple_fish(self):
        """Test bioload calculation with multiple fish types."""
        stock = {"goldfish": 5, "koi": 2}
        result = self.calculator.calculate_bioload(stock)

        # 5 × 1.0 + 2 × 2.5 = 5.0 + 5.0 = 10.0
        assert result == 10.0

    def test_calculate_bioload_invalid_fish_data(self):
        """Test handling of fish with invalid bioload_factor."""
        # Create fish with None value
        invalid_fish = Fish("Invalid", 20, None, 75)

        # Update the mock to return invalid fish for specific key
        def mock_get_fish_by_key(key):
            if key == "invalid_fish":
                return invalid_fish
            return self._get_fish_by_key(key)

        self.mock_fish_repo.get_fish_by_key.side_effect = mock_get_fish_by_key

        stock = {"invalid_fish": 5}

        with pytest.raises(ValueError, match="invalid bioload_factor value \\(None\\)"):
            self.calculator.calculate_bioload(stock)

    def test_get_stocking_recommendations_valid_volume(self):
        """Test stocking recommendations with valid volume."""
        result = self.calculator.get_stocking_recommendations(5000.0)

        expected = {
            "Goldfish": 66,  # 5000 / 75 = 66.67 → 66
            "Koi": 5,  # 5000 / 950 = 5.26 → 5
            "Shubunkin": 26,  # 5000 / 190 = 26.31 → 26
        }

        assert result == expected

    def test_get_stocking_recommendations_zero_volume(self):
        """Test that zero volume raises ValueError."""
        with pytest.raises(ValueError, match="Pond volume must be positive"):
            self.calculator.get_stocking_recommendations(0.0)

    def test_get_stocking_recommendations_negative_volume(self):
        """Test that negative volume raises ValueError."""
        with pytest.raises(ValueError, match="Pond volume must be positive"):
            self.calculator.get_stocking_recommendations(-100.0)

    def test_get_stocking_recommendations_invalid_fish_data(self):
        """Test recommendations skip fish with invalid data."""
        # Add fish with invalid min_liters_per_fish
        invalid_fish = Fish("Invalid", 20, 1.0, None)
        self.mock_fish_repo.get_all_fish.return_value = {
            "goldfish": self.goldfish,
            "invalid_fish": invalid_fish,
        }

        result = self.calculator.get_stocking_recommendations(1000.0)

        # Should only include goldfish, skip invalid fish
        assert "Goldfish" in result
        assert "Invalid" not in result

    def test_validate_stocking_adequate(self):
        """Test stocking validation when pond is adequate."""
        stock = {"goldfish": 5}  # Requires 375L
        pond_volume = 500.0  # Adequate

        result = self.calculator.validate_stocking(stock, pond_volume)
        assert result is True

    def test_validate_stocking_overstocked(self):
        """Test stocking validation when pond is overstocked."""
        stock = {"goldfish": 10}  # Requires 750L
        pond_volume = 500.0  # Inadequate

        result = self.calculator.validate_stocking(stock, pond_volume)
        assert result is False

    def test_validate_stocking_exact_capacity(self):
        """Test stocking validation at exact capacity."""
        stock = {"goldfish": 5}  # Requires 375L
        pond_volume = 375.0  # Exact match

        result = self.calculator.validate_stocking(stock, pond_volume)
        assert result is True

    def test_validate_stocking_empty_stock(self):
        """Test stocking validation with empty stock."""
        result = self.calculator.validate_stocking({}, 1000.0)
        assert result is True
