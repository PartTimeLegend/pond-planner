from abc import ABC, abstractmethod
from typing import Dict
from Fish import Fish


class DataRepository(ABC):
    """
    Abstract interface for fish data access following the Repository pattern.
    This allows for different data sources (YAML, JSON, database) while maintaining
    the same interface for the business logic.
    """

    @abstractmethod
    def get_all_fish(self) -> Dict[str, Fish]:
        """Get all available fish with their properties."""

    @abstractmethod
    def get_fish_by_key(self, fish_key: str) -> Fish:
        """Get a specific fish by its key."""

    @abstractmethod
    def fish_exists(self, fish_key: str) -> bool:
        """Check if a fish exists in the database."""

    @abstractmethod
    def get_fish_keys(self) -> list[str]:
        """Get all available fish keys."""
