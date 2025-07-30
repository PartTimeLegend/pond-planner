import os
import tempfile

import pytest
import yaml

from Fish import Fish
from repositories.yaml_fish_repository import YamlFishRepository
from repositories.yaml_shape_repository import YamlShapeRepository


class TestYamlFishRepository:
    """Test cases for YamlFishRepository class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary YAML file with test data
        self.test_data = {
            "fish_species": {
                "goldfish": {
                    "name": "Goldfish",
                    "adult_length_cm": 20,
                    "bioload_factor": 1.0,
                    "min_liters_per_fish": 75,
                },
                "koi": {
                    "name": "Koi",
                    "adult_length_cm": 60,
                    "bioload_factor": 2.5,
                    "min_liters_per_fish": 950,
                },
            }
        }

        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        yaml.dump(self.test_data, self.temp_file)
        self.temp_file.close()

        self.repository = YamlFishRepository(self.temp_file.name)

    def teardown_method(self):
        """Clean up after each test method."""
        os.unlink(self.temp_file.name)

    def test_initialization(self):
        """Test repository initialization."""
        assert self.repository is not None
        assert len(self.repository.get_all_fish()) == 2

    def test_get_all_fish(self):
        """Test getting all fish from repository."""
        all_fish = self.repository.get_all_fish()

        assert isinstance(all_fish, dict)
        assert len(all_fish) == 2
        assert "goldfish" in all_fish
        assert "koi" in all_fish
        assert isinstance(all_fish["goldfish"], Fish)

    def test_get_fish_by_key_valid(self):
        """Test getting fish by valid key."""
        fish = self.repository.get_fish_by_key("goldfish")

        assert isinstance(fish, Fish)
        assert fish.name == "Goldfish"
        assert fish.adult_length_cm == 20
        assert fish.bioload_factor == 1.0
        assert fish.min_liters_per_fish == 75

    def test_get_fish_by_key_case_insensitive(self):
        """Test that fish lookup is case insensitive."""
        fish = self.repository.get_fish_by_key("GOLDFISH")
        assert fish.name == "Goldfish"

    def test_get_fish_by_key_invalid(self):
        """Test getting fish by invalid key raises KeyError."""
        with pytest.raises(KeyError, match="Fish key 'unknown' not found"):
            self.repository.get_fish_by_key("unknown")

    def test_fish_exists_valid(self):
        """Test checking if valid fish exists."""
        assert self.repository.fish_exists("goldfish") is True
        assert self.repository.fish_exists("GOLDFISH") is True  # Case insensitive

    def test_fish_exists_invalid(self):
        """Test checking if invalid fish exists."""
        assert self.repository.fish_exists("unknown") is False

    def test_get_fish_keys(self):
        """Test getting sorted fish keys."""
        keys = self.repository.get_fish_keys()

        assert isinstance(keys, list)
        assert len(keys) == 2
        assert keys == ["goldfish", "koi"]  # Should be sorted

    def test_invalid_yaml_file(self):
        """Test that invalid YAML file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            YamlFishRepository("/nonexistent/file.yaml")

    def test_missing_required_field(self):
        """Test that missing required field raises ValueError."""
        invalid_data = {
            "fish_species": {
                "invalid_fish": {
                    "name": "Invalid Fish",
                    # Missing required fields
                }
            }
        }

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(invalid_data, temp_file)
        temp_file.close()

        try:
            with pytest.raises(ValueError, match="Invalid fish data"):
                YamlFishRepository(temp_file.name)
        finally:
            os.unlink(temp_file.name)


class TestYamlShapeRepository:
    """Test cases for YamlShapeRepository class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary YAML file with test shape data
        self.test_data = {
            "pond_shapes": {
                "rectangular": {
                    "name": "Rectangular",
                    "formula_type": "simple",
                    "multiplier": 1.0,
                },
                "circular": {
                    "name": "Circular",
                    "formula_type": "circular",
                    "multiplier": 1.0,
                },
            },
            "shape_categories": {"geometric": ["rectangular", "circular"]},
            "validation_rules": {
                "min_dimensions": {"length": 0.1, "width": 0.1, "depth": 0.05}
            },
        }

        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        yaml.dump(self.test_data, self.temp_file)
        self.temp_file.close()

        self.repository = YamlShapeRepository(self.temp_file.name)

    def teardown_method(self):
        """Clean up after each test method."""
        os.unlink(self.temp_file.name)

    def test_get_all_shapes(self):
        """Test getting all shapes from repository."""
        shapes = self.repository.get_all_shapes()

        assert isinstance(shapes, dict)
        assert len(shapes) == 2
        assert "rectangular" in shapes
        assert "circular" in shapes

    def test_get_shape_by_key_valid(self):
        """Test getting shape by valid key."""
        shape = self.repository.get_shape_by_key("rectangular")

        assert isinstance(shape, dict)
        assert shape["name"] == "Rectangular"
        assert shape["formula_type"] == "simple"

    def test_get_shape_by_key_invalid(self):
        """Test getting shape by invalid key raises KeyError."""
        with pytest.raises(KeyError, match="Shape key 'unknown' not found"):
            self.repository.get_shape_by_key("unknown")

    def test_shape_exists(self):
        """Test checking if shape exists."""
        assert self.repository.shape_exists("rectangular") is True
        assert self.repository.shape_exists("unknown") is False

    def test_get_shape_keys(self):
        """Test getting sorted shape keys."""
        keys = self.repository.get_shape_keys()

        assert isinstance(keys, list)
        assert len(keys) == 2
        assert "rectangular" in keys
        assert "circular" in keys

    def test_get_shapes_by_category(self):
        """Test getting shapes by category."""
        geometric = self.repository.get_shapes_by_category("geometric")

        assert isinstance(geometric, list)
        assert "rectangular" in geometric
        assert "circular" in geometric

    def test_get_shapes_by_invalid_category(self):
        """Test getting shapes by invalid category returns empty list."""
        result = self.repository.get_shapes_by_category("unknown")
        assert result == []

    def test_get_validation_rules(self):
        """Test getting validation rules."""
        rules = self.repository.get_validation_rules()

        assert isinstance(rules, dict)
        assert "min_dimensions" in rules
        assert rules["min_dimensions"]["length"] == 0.1
