import math
from typing import Dict, Any
from PondDimensions import PondDimensions
from interfaces.ShapeRepository import ShapeRepository


class VolumeCalculator:
    """
    Handles pond volume calculations for different shapes using configurable shape definitions.
    Follows Single Responsibility Principle and Open/Closed Principle.
    """

    def __init__(self, shape_repository: ShapeRepository):
        """
        Initialize with a shape repository.

        Args:
            shape_repository: Implementation of ShapeRepository interface
        """
        self._shape_repository = shape_repository

    def calculate_volume_liters(self, dimensions: PondDimensions) -> float:
        """
        Calculate the volume of the pond in liters based on its shape and dimensions.

        This method performs comprehensive validation of the pond dimensions using
        repository validation rules, then calculates the volume using shape-specific
        formulas loaded from the shape repository configuration.

        Args:
            dimensions (PondDimensions): Object containing pond specifications including:
                - length_meters: Length dimension in meters
                - width_meters: Width dimension in meters
                - avg_depth_meters: Average depth in meters
                - shape: Shape identifier (must exist in shape repository)

        Returns:
            float: The volume of the pond in liters. Calculation precision depends on
                  the shape complexity and formula used. Result is guaranteed to be positive.

        Raises:
            ValueError: If dimensions are None, invalid (negative/zero), or if the
                       calculated volume is not positive.
            TypeError: If dimensions parameter is not a PondDimensions object.
            KeyError: If the pond shape is not found in the shape repository.

        Note:
            - Validation includes both basic checks and repository-defined rules
            - Shape-specific formulas are loaded from YAML configuration
            - Volume calculation follows ACID consistency principles
            - Different shapes may use dimensions differently (e.g., width as diameter for circles)
            - Result includes proper unit conversion from cubic meters to liters

        Example:
            >>> from PondDimensions import PondDimensions
            >>> dims = PondDimensions(5.0, 3.0, 1.5, "rectangular")
            >>> volume = calculator.calculate_volume_liters(dims)
            >>> print(f"Volume: {volume:,.0f} liters")
        """
        # Validation for consistency (part of ACID Consistency)
        self._validate_dimensions(dimensions)

        shape_config = self._shape_repository.get_shape_by_key(dimensions.shape)

        # Calculate volume in cubic meters based on shape configuration
        volume_m3 = self._calculate_volume_by_shape_config(
            shape_config,
            dimensions.length_meters,
            dimensions.width_meters,
            dimensions.avg_depth_meters,
        )

        # Ensure result is valid (Consistency check)
        if volume_m3 <= 0:
            raise ValueError("Calculated volume must be positive")

        # Convert to liters (1 cubic meter = 1000 liters)
        return volume_m3 * 1000

    def _validate_dimensions(self, dimensions: PondDimensions) -> None:
        """
        Validate pond dimensions using repository validation rules and basic checks.

        This method performs comprehensive validation including type checking,
        basic dimension validation, shape existence verification, and repository-defined
        minimum/maximum dimension limits.

        Args:
            dimensions (PondDimensions): The pond dimensions to validate.

        Raises:
            ValueError: If dimensions are None, have invalid values, or exceed limits.
            TypeError: If dimensions is not a PondDimensions object.
            KeyError: If the shape is not found in the shape repository.

        Note:
            - Checks basic requirements (positive values, proper object type)
            - Validates against repository-defined min/max limits
            - Verifies shape exists in the shape repository
            - Part of ACID consistency validation
        """
        if not dimensions:
            raise ValueError("Pond dimensions cannot be None")

        if not isinstance(dimensions, PondDimensions):
            raise TypeError("Expected PondDimensions object")

        if not hasattr(dimensions, "shape") or not dimensions.shape:
            raise ValueError("Pond shape must be specified")

        if not self._shape_repository.shape_exists(dimensions.shape):
            available_shapes = ", ".join(self._shape_repository.get_shape_keys())
            raise ValueError(
                f"Unknown shape '{dimensions.shape}'. Available shapes: {available_shapes}"
            )

        # Get validation rules and check dimensions
        validation_rules = self._shape_repository.get_validation_rules()
        min_dims = validation_rules.get("min_dimensions", {})
        max_dims = validation_rules.get("max_dimensions", {})

        if dimensions.length_meters < min_dims.get("length", 0):
            raise ValueError(
                f"Length must be at least {min_dims.get('length', 0)} meters"
            )
        if dimensions.width_meters < min_dims.get("width", 0):
            raise ValueError(
                f"Width must be at least {min_dims.get('width', 0)} meters"
            )
        if dimensions.avg_depth_meters < min_dims.get("depth", 0):
            raise ValueError(
                f"Depth must be at least {min_dims.get('depth', 0)} meters"
            )

        if dimensions.length_meters > max_dims.get("length", float("inf")):
            raise ValueError(
                f"Length cannot exceed {max_dims.get('length')} meters"
            )
        if dimensions.width_meters > max_dims.get("width", float("inf")):
            raise ValueError(
                f"Width cannot exceed {max_dims.get('width')} meters"
            )
        if dimensions.avg_depth_meters > max_dims.get("depth", float("inf")):
            raise ValueError(
                f"Depth cannot exceed {max_dims.get('depth')} meters"
            )

    def _calculate_volume_by_shape_config(
        self,
        shape_config: Dict[str, Any],
        length: float,
        width: float,
        depth: float,
    ) -> float:
        """
        Calculate volume based on shape configuration loaded from YAML repository.

        This method applies shape-specific formulas and multipliers to calculate
        the surface area, then multiplies by depth to get volume. The formula
        type determines which calculation method is used.

        Args:
            shape_config (Dict[str, Any]): Shape configuration from repository containing:
                - formula_type: Type of calculation (simple, circular, elliptical, etc.)
                - multiplier: Adjustment factor for approximate shapes
                - area_formula: Formula description for documentation
            length (float): Length dimension in meters.
            width (float): Width dimension in meters.
            depth (float): Depth dimension in meters.

        Returns:
            float: Volume in cubic meters (before conversion to liters).

        Note:
            - Formula types include: simple, circular, elliptical, triangular, polygon, approximation
            - Multipliers are used for complex shapes that approximate simpler ones
            - Polygon calculations support hexagonal and octagonal shapes
            - Approximation formulas may use elliptical or rectangular base calculations
            - Falls back to simple rectangular calculation for unknown formula types
        """
        formula_type = shape_config.get("formula_type", "simple")
        multiplier = shape_config.get("multiplier", 1.0)

        if formula_type == "simple":
            area = length * width
        elif formula_type == "circular":
            area = math.pi * (width / 2) ** 2
        elif formula_type == "elliptical":
            area = math.pi * (length / 2) * (width / 2)
        elif formula_type == "triangular":
            area = 0.5 * length * width
        elif formula_type == "polygon":
            if "hexagonal" in shape_config.get("area_formula", ""):
                area = (3 * math.sqrt(3) / 2) * width * width
            elif "octagonal" in shape_config.get("area_formula", ""):
                area = 2 * (1 + math.sqrt(2)) * width * width
            else:
                area = length * width  # fallback
        elif formula_type == "approximation":
            if "pi" in shape_config.get("area_formula", ""):
                area = math.pi * (length / 2) * (width / 2)
            else:
                area = length * width
        else:
            # Default fallback
            area = length * width

        return area * multiplier * depth
