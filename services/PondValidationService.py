from typing import List, Dict
from interfaces.ValidationService import ValidationService
from interfaces.ShapeRepository import ShapeRepository


class PondValidationService(ValidationService):
    """
    Concrete implementation of validation service for pond planning.
    Uses shape repository for extensible validation rules.
    """

    def __init__(self, shape_repository: ShapeRepository = None):
        """
        Initialize with optional shape repository.

        Args:
            shape_repository: Optional shape repository for validation rules
        """
        if shape_repository is None:
            from repositories.YamlShapeRepository import YamlShapeRepository
            shape_repository = YamlShapeRepository()

        self._shape_repository = shape_repository
        self._validation_rules = shape_repository.get_validation_rules()

    def validate_dimensions(self, length: float, width: float, depth: float) -> List[str]:
        """
        Validate pond dimensions using repository rules.
        Args:
            length: Length of the pond in meters
            width: Width of the pond in meters
            depth: Depth of the pond in meters
        Returns:
            List[str]: List of error messages if validation fails, empty if valid
        """
        errors = []

        min_dims = self._validation_rules.get('min_dimensions', {})
        max_dims = self._validation_rules.get('max_dimensions', {})

        # Check minimum dimensions
        if length < min_dims.get('length', 0):
            errors.append(f"Length must be at least {min_dims.get('length', 0)} meters")
        if width < min_dims.get('width', 0):
            errors.append(f"Width must be at least {min_dims.get('width', 0)} meters")
        if depth < min_dims.get('depth', 0):
            errors.append(f"Depth must be at least {min_dims.get('depth', 0)} meters")

        # Check maximum dimensions
        if length > max_dims.get('length', float('inf')):
            errors.append(f"Length cannot exceed {max_dims.get('length')} meters")
        if width > max_dims.get('width', float('inf')):
            errors.append(f"Width cannot exceed {max_dims.get('width')} meters")
        if depth > max_dims.get('depth', float('inf')):
            errors.append(f"Depth cannot exceed {max_dims.get('depth')} meters")

        return errors

    def validate_fish_quantity(self, quantity: int) -> List[str]:
        """
        Validate fish quantity for stocking.
        Args:
            quantity: Number of fish to validate
        Returns:
            List[str]: List of error messages if validation fails, empty if valid
        """
        errors = []

        if quantity <= 0:
            errors.append("Quantity must be positive")
        if quantity > 10000:  # Reasonable upper limit
            errors.append("Quantity exceeds maximum allowed (10000)")

        return errors

    def validate_pond_shape(self, shape: str) -> List[str]:
        """
        Validate pond shape using repository data.
        Args:
            shape: Shape of the pond to validate
        Returns:
            List[str]: List of error messages if validation fails, empty if valid
        """
        errors = []

        if not shape or not isinstance(shape, str):
            errors.append("Shape must be a valid string")
        elif not self._shape_repository.shape_exists(shape):
            available_shapes = ', '.join(self._shape_repository.get_shape_keys())
            errors.append(f"Invalid shape '{shape}'. Available shapes: {available_shapes}")

        return errors

    def validate_fish_stock_data(self, fish_stock: Dict[str, int]) -> List[str]:
        """
        Validate entire fish stock data.
        Args:
            fish_stock: Dictionary of fish types and their quantities
        Returns:
            List[str]: List of error messages if validation fails, empty if valid
        """
        errors = []

        if not isinstance(fish_stock, dict):
            errors.append("Fish stock must be a dictionary")
            return errors

        for fish_type, quantity in fish_stock.items():
            if not isinstance(fish_type, str):
                errors.append(f"Fish type must be string, got {type(fish_type)}")
            if not isinstance(quantity, int):
                errors.append(f"Quantity for {fish_type} must be integer, got {type(quantity)}")
            else:
                quantity_errors = self.validate_fish_quantity(quantity)
                errors.extend([f"{fish_type}: {error}" for error in quantity_errors])

        return errors
