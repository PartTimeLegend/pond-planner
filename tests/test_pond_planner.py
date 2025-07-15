import pytest
from unittest.mock import Mock, patch
from PondPlanner import PondPlanner
from PondDimensions import PondDimensions


class TestPondPlanner:
    """Test cases for PondPlanner main facade class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.planner = PondPlanner()

    def test_initialization(self):
        """Test that PondPlanner initializes correctly."""
        assert self.planner is not None
        assert self.planner.dimensions is None
        assert isinstance(self.planner.fish_stock, dict)
        assert len(self.planner.fish_stock) == 0

    def test_set_dimensions_valid(self):
        """Test setting valid pond dimensions."""
        self.planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")

        assert self.planner.dimensions is not None
        assert self.planner.dimensions.length_meters == 5.0
        assert self.planner.dimensions.width_meters == 3.0
        assert self.planner.dimensions.avg_depth_meters == 1.5
        assert self.planner.dimensions.shape == "rectangular"

    def test_set_dimensions_invalid_negative(self):
        """Test that negative dimensions raise ValueError."""
        with pytest.raises(ValueError, match="Invalid dimensions"):
            self.planner.set_dimensions(-1.0, 3.0, 1.5, "rectangular")

    def test_set_dimensions_invalid_shape(self):
        """Test that invalid shape raises ValueError."""
        with pytest.raises(ValueError, match="Invalid dimensions"):
            self.planner.set_dimensions(5.0, 3.0, 1.5, "invalid_shape")

    def test_calculate_volume_no_dimensions(self):
        """Test that calculating volume without dimensions raises ValueError."""
        with pytest.raises(ValueError, match="Pond dimensions not set"):
            self.planner.calculate_volume_liters()

    def test_calculate_volume_with_dimensions(self):
        """Test volume calculation with valid dimensions."""
        self.planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")
        volume = self.planner.calculate_volume_liters()

        # 5m × 3m × 1.5m = 22.5 m³ = 22,500 liters
        assert volume == 22500.0

    def test_add_fish_valid(self):
        """Test adding valid fish to stock."""
        self.planner.add_fish("goldfish", 5)

        stock = self.planner.fish_stock
        assert "goldfish" in stock
        assert stock["goldfish"] == 5

    def test_add_fish_invalid_type(self):
        """Test that adding invalid fish type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown fish type"):
            self.planner.add_fish("invalid_fish", 5)

    def test_add_fish_invalid_quantity(self):
        """Test that adding invalid quantity raises ValueError."""
        with pytest.raises(ValueError, match="Invalid quantity"):
            self.planner.add_fish("goldfish", -1)

    def test_remove_fish(self):
        """Test removing fish from stock."""
        self.planner.add_fish("goldfish", 10)
        self.planner.remove_fish("goldfish", 3)

        stock = self.planner.fish_stock
        assert stock["goldfish"] == 7

    def test_remove_fish_all(self):
        """Test removing all fish of a type removes entry."""
        self.planner.add_fish("goldfish", 5)
        self.planner.remove_fish("goldfish", 10)  # Remove more than available

        stock = self.planner.fish_stock
        assert "goldfish" not in stock

    def test_add_fish_batch(self):
        """Test adding multiple fish types in a batch."""
        batch = {
            "goldfish": 10,
            "koi": 3,
            "goldfish": 5  # This should add to existing
        }

        self.planner.add_fish_batch(batch)
        stock = self.planner.fish_stock

        assert stock["goldfish"] == 5  # Last value in dict
        assert stock["koi"] == 3

    def test_calculate_required_volume(self):
        """Test calculating required volume for fish stock."""
        self.planner.add_fish("goldfish", 5)  # 5 × 75L = 375L
        self.planner.add_fish("koi", 2)       # 2 × 950L = 1900L

        required = self.planner.calculate_required_volume()
        assert required == 2275.0  # 375 + 1900

    def test_calculate_bioload(self):
        """Test calculating total bioload."""
        self.planner.add_fish("goldfish", 5)  # 5 × 1.0 = 5.0
        self.planner.add_fish("koi", 2)       # 2 × 2.5 = 5.0

        bioload = self.planner.calculate_bioload()
        assert bioload == 10.0

    def test_get_stocking_recommendations(self):
        """Test getting stocking recommendations."""
        self.planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")  # 22,500L

        recommendations = self.planner.get_stocking_recommendations()

        assert isinstance(recommendations, dict)
        assert "Goldfish" in recommendations
        assert recommendations["Goldfish"] == 300  # 22500 / 75

    def test_calculate_pump_size(self):
        """Test pump size calculation."""
        self.planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")
        self.planner.add_fish("goldfish", 5)

        pump_lph, category = self.planner.calculate_pump_size()

        assert isinstance(pump_lph, int)
        assert pump_lph > 0
        assert category in ["Light bioload", "Medium bioload", "Heavy bioload"]

    def test_calculate_filter_size(self):
        """Test filter size calculation."""
        self.planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")
        self.planner.add_fish("goldfish", 5)

        filters = self.planner.calculate_filter_size()

        assert isinstance(filters, dict)
        assert "biological_filter" in filters
        assert "uv_sterilizer" in filters
        assert "mechanical_filter" in filters

    def test_get_available_shapes(self):
        """Test getting available pond shapes."""
        shapes = self.planner.get_available_shapes()

        assert isinstance(shapes, list)
        assert len(shapes) > 0
        assert "rectangular" in shapes
        assert "circular" in shapes

    def test_get_shapes_by_category(self):
        """Test getting shapes by category."""
        geometric_shapes = self.planner.get_shapes_by_category("geometric")

        assert isinstance(geometric_shapes, list)
        assert "rectangular" in geometric_shapes
        assert "circular" in geometric_shapes

    def test_generate_report_no_dimensions(self):
        """Test report generation without dimensions."""
        report = self.planner.generate_report()
        assert "Error: Pond dimensions not set" in report

    def test_generate_report_with_data(self):
        """Test comprehensive report generation."""
        self.planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")
        self.planner.add_fish("goldfish", 10)

        report = self.planner.generate_report()

        assert "POND PLANNING REPORT" in report
        assert "22,500 liters" in report
        assert "Goldfish: 10 fish" in report
        assert "Equipment Recommendations" in report

    def test_fish_database_property(self):
        """Test accessing fish database property."""
        db = self.planner.fish_database

        assert isinstance(db, dict)
        assert len(db) > 0
        assert "goldfish" in db

    def test_transaction_rollback(self):
        """Test that failed operations rollback correctly."""
        self.planner.add_fish("goldfish", 5)
        original_stock = self.planner.fish_stock.copy()

        # Try to add invalid fish in batch - should rollback
        try:
            self.planner.add_fish_batch({"goldfish": 5, "invalid_fish": 3})
        except ValueError:
            pass

        # Stock should remain unchanged
        assert self.planner.fish_stock == original_stock
