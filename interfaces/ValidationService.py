from abc import ABC, abstractmethod


class ValidationService(ABC):
    """
    Abstract interface for validation operations following Single Responsibility Principle.
    """

    @abstractmethod
    def validate_dimensions(
        self, length: float, width: float, depth: float
    ) -> list[str]:
        """Validate pond dimensions and return list of error messages."""

    @abstractmethod
    def validate_fish_quantity(self, quantity: int) -> list[str]:
        """Validate fish quantity and return list of error messages."""

    @abstractmethod
    def validate_pond_shape(self, shape: str) -> list[str]:
        """Validate pond shape and return list of error messages."""

    @abstractmethod
    def validate_fish_stock_data(self, fish_stock: dict[str, int]) -> list[str]:
        """Validate entire fish stock data."""
