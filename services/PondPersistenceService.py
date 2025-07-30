"""
Pond Persistence Service for saving and loading pond configurations.

This service handles the serialization and deserialization of pond data,
including dimensions, fish stocking, and metadata.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from PondDimensions import PondDimensions


class PondConfiguration:
    """
    Represents a complete pond configuration that can be saved/loaded.
    """

    def __init__(
        self,
        name: str,
        dimensions: PondDimensions,
        fish_stock: dict[str, int],
        created_at: Optional[datetime] = None,
        description: str = "",
    ):
        self.name = name
        self.dimensions = dimensions
        self.fish_stock = fish_stock
        self.created_at = created_at or datetime.now()
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        """Convert pond configuration to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "dimensions": {
                "length_meters": self.dimensions.length_meters,
                "width_meters": self.dimensions.width_meters,
                "avg_depth_meters": self.dimensions.avg_depth_meters,
                "shape": self.dimensions.shape,
            },
            "fish_stock": self.fish_stock,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PondConfiguration":
        """Create pond configuration from dictionary."""
        dimensions = PondDimensions(
            length_meters=data["dimensions"]["length_meters"],
            width_meters=data["dimensions"]["width_meters"],
            avg_depth_meters=data["dimensions"]["avg_depth_meters"],
            shape=data["dimensions"]["shape"],
        )

        return cls(
            name=data["name"],
            dimensions=dimensions,
            fish_stock=data["fish_stock"],
            created_at=datetime.fromisoformat(data["created_at"]),
            description=data.get("description", ""),
        )


class PondPersistenceService:
    """
    Service for saving and loading pond configurations to/from JSON files.
    """

    def __init__(self, storage_directory: str = "data/saved_ponds"):
        """
        Initialize the persistence service.

        Args:
            storage_directory: Directory where pond configurations will be stored
        """
        self.storage_directory = Path(storage_directory)
        self.storage_directory.mkdir(parents=True, exist_ok=True)

    def save_pond(self, configuration: PondConfiguration) -> str:
        """
        Save a pond configuration to file.

        Args:
            configuration: The pond configuration to save

        Returns:
            str: The filename of the saved configuration

        Raises:
            IOError: If the file cannot be written
        """
        # Create safe filename from pond name
        safe_name = self._sanitize_filename(configuration.name)
        filename = f"{safe_name}.json"
        filepath = self.storage_directory / filename

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(configuration.to_dict(), file, indent=2, ensure_ascii=False)
            return filename
        except OSError as e:
            raise OSError(f"Failed to save pond configuration: {e}") from e

    def load_pond(self, filename: str) -> PondConfiguration:
        """
        Load a pond configuration from file.

        Args:
            filename: The filename (with or without .json extension)

        Returns:
            PondConfiguration: The loaded pond configuration

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file contains invalid data
        """
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"

        filepath = self.storage_directory / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Pond configuration not found: {filename}")

        try:
            with open(filepath, encoding="utf-8") as file:
                data = json.load(file)
            return PondConfiguration.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid pond configuration file: {e}") from e

    def list_saved_ponds(self) -> list[dict[str, Any]]:
        """
        List all saved pond configurations with metadata.

        Returns:
            List of dictionaries containing pond metadata
        """
        pond_list = []

        for filepath in self.storage_directory.glob("*.json"):
            try:
                with open(filepath, encoding="utf-8") as file:
                    data = json.load(file)

                pond_info = {
                    "filename": filepath.stem,
                    "name": data["name"],
                    "description": data.get("description", ""),
                    "created_at": data["created_at"],
                    "shape": data["dimensions"]["shape"],
                    "fish_count": sum(data["fish_stock"].values()),
                }
                pond_list.append(pond_info)
            except (json.JSONDecodeError, KeyError):
                # Skip invalid files
                continue

        # Sort by creation date (newest first)
        pond_list.sort(key=lambda x: x["created_at"], reverse=True)
        return pond_list

    def delete_pond(self, filename: str) -> bool:
        """
        Delete a saved pond configuration.

        Args:
            filename: The filename (with or without .json extension)

        Returns:
            bool: True if deleted successfully, False if file didn't exist
        """
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"

        filepath = self.storage_directory / filename

        if filepath.exists():
            try:
                filepath.unlink()
                return True
            except OSError:
                return False
        return False

    def pond_exists(self, filename: str) -> bool:
        """
        Check if a pond configuration file exists.

        Args:
            filename: The filename (with or without .json extension)

        Returns:
            bool: True if the file exists
        """
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"

        filepath = self.storage_directory / filename
        return filepath.exists()

    def _sanitize_filename(self, name: str) -> str:
        """
        Create a safe filename from a pond name.

        Args:
            name: The pond name

        Returns:
            str: A safe filename
        """
        # Remove invalid characters and limit length
        safe_chars = []
        for char in name:
            if char.isalnum() or char in "-_. ":
                safe_chars.append(char)
            else:
                safe_chars.append("_")

        safe_name = "".join(safe_chars).strip()
        safe_name = safe_name.replace(" ", "_")

        # Limit length and ensure it's not empty
        safe_name = safe_name[:50] if safe_name else "pond"

        return safe_name
