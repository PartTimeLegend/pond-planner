from abc import ABC, abstractmethod
from typing import Any


class ShapeRepository(ABC):
    """
    Abstract interface for pond shape data access following the Repository pattern.
    """

    @abstractmethod
    def get_all_shapes(self) -> dict[str, dict[str, Any]]:
        """Get all available pond shapes with their properties."""

    @abstractmethod
    def get_shape_by_key(self, shape_key: str) -> dict[str, Any]:
        """Get a specific shape by its key."""

    @abstractmethod
    def shape_exists(self, shape_key: str) -> bool:
        """Check if a shape exists in the repository."""

    @abstractmethod
    def get_shape_keys(self) -> list[str]:
        """Get all available shape keys."""

    @abstractmethod
    def get_shapes_by_category(self, category: str) -> list[str]:
        """Get shapes belonging to a specific category."""

    @abstractmethod
    def get_validation_rules(self) -> dict[str, Any]:
        """Get validation rules for pond dimensions."""
        """Get validation rules for pond dimensions."""
