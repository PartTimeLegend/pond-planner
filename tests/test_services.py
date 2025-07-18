from unittest.mock import Mock

import pytest

from services.PondStockManager import PondStockManager
from services.PondTransactionManager import PondTransactionManager
from services.PondValidationService import PondValidationService


class TestPondStockManager:
    """Test cases for PondStockManager service."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_fish_repo = Mock()
        self.mock_validation = Mock()
        self.mock_transaction = Mock()

        # Configure mocks
        self.mock_fish_repo.fish_exists.return_value = True
        self.mock_validation.validate_fish_quantity.return_value = []
        self.mock_validation.validate_fish_stock_data.return_value = []
        self.mock_transaction.execute_transaction.side_effect = lambda op: op()

        self.manager = PondStockManager(
            self.mock_fish_repo, self.mock_validation, self.mock_transaction
        )

    def test_add_fish_valid(self):
        """Test adding valid fish to stock."""
        self.manager.add_fish("goldfish", 5)

        stock = self.manager.get_stock()
        assert stock["goldfish"] == 5

    def test_add_fish_accumulates(self):
        """Test that adding fish accumulates quantities."""
        self.manager.add_fish("goldfish", 5)
        self.manager.add_fish("goldfish", 3)

        stock = self.manager.get_stock()
        assert stock["goldfish"] == 8

    def test_add_fish_validation_error(self):
        """Test that validation errors are raised."""
        self.mock_validation.validate_fish_quantity.return_value = ["Invalid quantity"]

        with pytest.raises(ValueError, match="Invalid quantity"):
            self.manager.add_fish("goldfish", -1)

    def test_add_fish_unknown_fish(self):
        """Test that unknown fish type raises error."""
        self.mock_fish_repo.fish_exists.return_value = False

        with pytest.raises(ValueError, match="Unknown fish type"):
            self.manager.add_fish("unknown", 5)

    def test_remove_fish_valid(self):
        """Test removing fish from stock."""
        self.manager.add_fish("goldfish", 10)
        self.manager.remove_fish("goldfish", 3)

        stock = self.manager.get_stock()
        assert stock["goldfish"] == 7

    def test_remove_fish_all(self):
        """Test removing all fish removes entry."""
        self.manager.add_fish("goldfish", 5)
        self.manager.remove_fish("goldfish", 10)  # More than available

        stock = self.manager.get_stock()
        assert "goldfish" not in stock

    def test_remove_fish_nonexistent(self):
        """Test removing nonexistent fish does nothing."""
        self.manager.remove_fish("goldfish", 5)  # No goldfish in stock

        stock = self.manager.get_stock()
        assert len(stock) == 0

    def test_bulk_add_fish_valid(self):
        """Test bulk adding fish."""
        fish_batch = {"goldfish": 10, "koi": 3}
        self.manager.bulk_add_fish(fish_batch)

        stock = self.manager.get_stock()
        assert stock["goldfish"] == 10
        assert stock["koi"] == 3

    def test_bulk_add_fish_validation_error(self):
        """Test that bulk add validation errors are raised."""
        self.mock_validation.validate_fish_stock_data.return_value = ["Invalid data"]

        with pytest.raises(ValueError, match="Invalid fish stock data"):
            self.manager.bulk_add_fish({"goldfish": -1})

    def test_get_stock_defensive_copy(self):
        """Test that get_stock returns defensive copy."""
        self.manager.add_fish("goldfish", 5)

        stock1 = self.manager.get_stock()
        stock2 = self.manager.get_stock()

        # Modify returned dict
        stock1["goldfish"] = 100

        # Original should be unchanged
        assert stock2["goldfish"] == 5

    def test_clear_stock(self):
        """Test clearing all stock."""
        self.manager.add_fish("goldfish", 5)
        self.manager.add_fish("koi", 3)

        self.manager.clear_stock()

        stock = self.manager.get_stock()
        assert len(stock) == 0

    def test_get_stock_count(self):
        """Test getting total stock count."""
        self.manager.add_fish("goldfish", 5)
        self.manager.add_fish("koi", 3)

        count = self.manager.get_stock_count()
        assert count == 8

    def test_has_fish(self):
        """Test checking if fish type is in stock."""
        self.manager.add_fish("goldfish", 5)

        assert self.manager.has_fish("goldfish") is True
        assert self.manager.has_fish("GOLDFISH") is True  # Case insensitive
        assert self.manager.has_fish("koi") is False


class TestPondValidationService:
    """Test cases for PondValidationService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_shape_repo = Mock()
        self.mock_shape_repo.get_validation_rules.return_value = {
            "min_dimensions": {"length": 0.1, "width": 0.1, "depth": 0.05},
            "max_dimensions": {"length": 1000.0, "width": 1000.0, "depth": 100.0},
        }
        self.mock_shape_repo.shape_exists.return_value = True
        self.mock_shape_repo.get_shape_keys.return_value = ["rectangular", "circular"]

        self.validator = PondValidationService(self.mock_shape_repo)

    def test_validate_dimensions_valid(self):
        """Test validation of valid dimensions."""
        errors = self.validator.validate_dimensions(5.0, 3.0, 1.5)
        assert errors == []

    def test_validate_dimensions_too_small(self):
        """Test validation of dimensions that are too small."""
        errors = self.validator.validate_dimensions(0.05, 3.0, 1.5)
        assert len(errors) == 1
        assert "Length must be at least 0.1 meters" in errors[0]

    def test_validate_dimensions_too_large(self):
        """Test validation of dimensions that are too large."""
        errors = self.validator.validate_dimensions(2000.0, 3.0, 1.5)
        assert len(errors) == 1
        assert "Length cannot exceed 1000.0 meters" in errors[0]

    def test_validate_fish_quantity_valid(self):
        """Test validation of valid fish quantity."""
        errors = self.validator.validate_fish_quantity(5)
        assert errors == []

    def test_validate_fish_quantity_invalid(self):
        """Test validation of invalid fish quantities."""
        errors = self.validator.validate_fish_quantity(0)
        assert "Quantity must be positive" in errors[0]

        errors = self.validator.validate_fish_quantity(15000)
        assert "Quantity exceeds maximum allowed" in errors[0]

    def test_validate_pond_shape_valid(self):
        """Test validation of valid pond shape."""
        errors = self.validator.validate_pond_shape("rectangular")
        assert errors == []

    def test_validate_pond_shape_invalid(self):
        """Test validation of invalid pond shape."""
        self.mock_shape_repo.shape_exists.return_value = False

        errors = self.validator.validate_pond_shape("invalid_shape")
        assert len(errors) == 1
        assert "Invalid shape 'invalid_shape'" in errors[0]

    def test_validate_fish_stock_data_valid(self):
        """Test validation of valid fish stock data."""
        stock_data = {"goldfish": 5, "koi": 3}
        errors = self.validator.validate_fish_stock_data(stock_data)
        assert errors == []

    def test_validate_fish_stock_data_invalid_type(self):
        """Test validation of invalid fish stock data type."""
        errors = self.validator.validate_fish_stock_data("not_a_dict")
        assert "Fish stock must be a dictionary" in errors[0]

    def test_validate_fish_stock_data_invalid_values(self):
        """Test validation of fish stock data with invalid values."""
        stock_data = {"goldfish": "not_int", 123: 5}
        errors = self.validator.validate_fish_stock_data(stock_data)

        assert len(errors) >= 2
        assert any("must be integer" in error for error in errors)
        assert any("must be string" in error for error in errors)


class TestPondTransactionManager:
    """Test cases for PondTransactionManager."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.manager = PondTransactionManager()

    def test_execute_transaction_success(self):
        """Test successful transaction execution."""

        def operation():
            return "success"

        result = self.manager.execute_transaction(operation)
        assert result == "success"

    def test_execute_transaction_failure_rollback(self):
        """Test transaction rollback on failure."""

        def failing_operation():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            self.manager.execute_transaction(failing_operation)

    def test_manual_transaction_success(self):
        """Test manual transaction management success."""
        self.manager.begin_transaction()
        self.manager.save_state("test_key", "original_value")
        self.manager.commit_transaction()

        assert not self.manager.is_in_transaction()

    def test_manual_transaction_rollback(self):
        """Test manual transaction rollback."""
        self.manager.begin_transaction()
        self.manager.save_state("test_key", "original_value")
        self.manager.rollback_transaction()

        assert not self.manager.is_in_transaction()

    def test_nested_transaction(self):
        """Test nested transaction handling."""

        def outer_operation():
            def inner_operation():
                return "inner_result"

            result = self.manager.execute_transaction(inner_operation)
            return f"outer_{result}"

        result = self.manager.execute_transaction(outer_operation)
        assert result == "outer_inner_result"

    def test_state_preservation(self):
        """Test that state is preserved for rollback."""
        self.manager.begin_transaction()
        self.manager.save_state("test_key", "original")

        saved_state = self.manager.get_rollback_state("test_key")
        assert saved_state == "original"

    def test_transaction_errors(self):
        """Test transaction error conditions."""
        # Cannot commit without active transaction
        with pytest.raises(RuntimeError, match="No active transaction to commit"):
            self.manager.commit_transaction()

        # Cannot rollback without active transaction
        with pytest.raises(RuntimeError, match="No active transaction to rollback"):
            self.manager.rollback_transaction()

        # Cannot begin when already active
        self.manager.begin_transaction()
        with pytest.raises(RuntimeError, match="Transaction already active"):
            self.manager.begin_transaction()
