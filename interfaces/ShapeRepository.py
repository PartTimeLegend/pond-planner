from abc import ABC, abstractmethod
from typing import Dict, List, Any


class ShapeRepository(ABC):
    """
    Abstract interface for pond shape data access following the Repository pattern.
    Allows for different data sources while maintaining the same interface.
    """

    @abstractmethod
    def get_all_shapes(self) -> Dict[str, Dict[str, Any]]:
        """Get all available pond shapes with their properties."""

    @abstractmethod
    def get_shape_by_key(self, shape_key: str) -> Dict[str, Any]:
        """Get a specific shape by its key."""


    @abstractmethod
    def shape_exists(self, shape_key: str) -> bool:
        """Check if a shape exists in the repository."""

    @abstractmethod
    def get_shape_keys(self) -> List[str]:
        """Get all available shape keys."""

    @abstractmethod
    def get_shapes_by_category(self, category: str) -> List[str]:
        """Get shapes belonging to a specific category."""

    @abstractmethod
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for pond dimensions."""
