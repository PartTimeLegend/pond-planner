from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ValidationService(ABC):
    """
    Abstract interface for validation operations following Single Responsibility Principle.
    Separates validation logic from business logic.
    """

    @abstractmethod
    def validate_dimensions(self, length: float, width: float, depth: float) -> List[str]:
        """Validate pond dimensions and return list of error messages."""

    @abstractmethod
    def validate_fish_quantity(self, quantity: int) -> List[str]:
        """Validate fish quantity and return list of error messages."""

    @abstractmethod
    def validate_pond_shape(self, shape: str) -> List[str]:
        """Validate pond shape and return list of error messages."""

    @abstractmethod
    def validate_fish_stock_data(self, fish_stock: Dict[str, int]) -> List[str]:
        """Validate entire fish stock data."""
