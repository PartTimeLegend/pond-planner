import os
from typing import Any, Dict, List

import yaml

from interfaces.ShapeRepository import ShapeRepository


class YamlShapeRepository(ShapeRepository):
    """
    YAML-based implementation of the shape repository.
    Handles loading and caching pond shape data from YAML files.
    """

    def __init__(self, yaml_file_path: str = None):
        """
        Initialize the repository with optional custom YAML file path.

        Args:
            yaml_file_path: Custom path to YAML file. If None, uses default location.
        """
        if yaml_file_path is None:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            yaml_file_path = os.path.join(script_dir, "pond_shapes.yaml")

        self._yaml_file_path = yaml_file_path
        self._shapes_cache: Dict[str, Dict[str, Any]] = {}
        self._categories_cache: Dict[str, List[str]] = {}
        self._validation_rules: Dict[str, Any] = {}
        self._load_shape_data()

    def _load_shape_data(self) -> None:
        """
        Load shape data from YAML file with proper error handling.

        Raises:
            FileNotFoundError: If YAML file is not found
            yaml.YAMLError: If YAML file is invalid
            KeyError: If required shape data fields are missing
        """
        try:
            with open(self._yaml_file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            self._shapes_cache = data["pond_shapes"]
            self._categories_cache = data.get("shape_categories", {})
            self._validation_rules = data.get("validation_rules", {})

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Pond shapes file not found: {self._yaml_file_path}"
            ) from exc
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing pond shapes YAML file: {e}") from e
        except KeyError as e:
            raise KeyError(f"Missing required field in pond shapes data: {e}") from e

    def get_all_shapes(self) -> Dict[str, Dict[str, Any]]:
        """Get all available pond shapes with their properties."""
        return self._shapes_cache.copy()

    def get_shape_by_key(self, shape_key: str) -> Dict[str, Any]:
        """
        Get a specific shape by its key.

        Args:
            shape_key: The key identifier for the shape

        Returns:
            Dict[str, Any]: The shape configuration

        Raises:
            KeyError: If shape key is not found
        """
        shape_key_lower = shape_key.lower()
        if shape_key_lower not in self._shapes_cache:
            raise KeyError(f"Shape key '{shape_key}' not found in database")
        return self._shapes_cache[shape_key_lower].copy()

    def shape_exists(self, shape_key: str) -> bool:
        """
        Check if a shape exists in the repository.
        Args:
            shape_key: The key identifier for the shape
        Returns:
            bool: True if shape exists, False otherwise
        """
        return shape_key.lower() in self._shapes_cache

    def get_shape_keys(self) -> List[str]:
        """
        Retrieve all available shape keys from the repository.

        Returns:
            List[str]: A sorted list of shape keys available in the shapes cache.
                The keys are returned in alphabetical order for consistent ordering.
        """
        # Return a sorted list of shape keys
        return sorted(self._shapes_cache.keys())

    def get_shapes_by_category(self, category: str) -> List[str]:
        """
        Retrieve a list of shape names for a given category.
        Args:
            category (str): The category name to search for shapes. Case-insensitive.
        Returns:
            List[str]: A list of shape names belonging to the specified category.
                        Returns an empty list if the category is not found.
        """
        return self._categories_cache.get(category.lower(), [])

    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for pond dimensions.
        Returns:
            Dict[str, Any]: A copy of the validation rules dictionary.
        """
        return self._validation_rules.copy()
