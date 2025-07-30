import os

import yaml

from Fish import Fish
from interfaces.data_repository import DataRepository


class YamlFishRepository(DataRepository):
    """
    YAML-based implementation of the fish data repository.
    Handles loading and caching fish data from YAML files.
    """

    def __init__(self, yaml_file_path: str | None = None):
        """
        Initialize the repository with optional custom YAML file path.

        Args:
            yaml_file_path: Custom path to YAML file. If None, uses default location.
        """
        if yaml_file_path is None:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            yaml_file_path = os.path.join(script_dir, "fish_database.yaml")

        self._yaml_file_path = yaml_file_path
        self._fish_cache: dict[str, Fish] = {}
        self._load_fish_data()

    def _load_fish_data(self) -> None:
        """
        Load fish data from YAML file with proper error handling and validation.

        Raises:
            FileNotFoundError: If YAML file is not found
            yaml.YAMLError: If YAML file is invalid
            KeyError: If required fish data fields are missing
            ValueError: If fish data contains invalid values
        """
        try:
            with open(self._yaml_file_path, encoding="utf-8") as file:
                data = yaml.safe_load(file)

            self._fish_cache.clear()
            for fish_key, fish_data in data["fish_species"].items():
                # Validate required fields
                required_fields = [
                    "name",
                    "adult_length_cm",
                    "bioload_factor",
                    "min_liters_per_fish",
                ]
                for field in required_fields:
                    if field not in fish_data:
                        raise KeyError(
                            f"Missing required field '{field}' for fish '{fish_key}'"
                        )
                    if fish_data[field] is None:
                        raise ValueError(
                            f"Field '{field}' cannot be None for fish '{fish_key}'"
                        )

                # Validate numeric fields
                if fish_data["adult_length_cm"] <= 0:
                    raise ValueError(
                        f"adult_length_cm must be positive for fish '{fish_key}'"
                    )
                if fish_data["bioload_factor"] <= 0:
                    raise ValueError(
                        f"bioload_factor must be positive for fish '{fish_key}'"
                    )
                if fish_data["min_liters_per_fish"] <= 0:
                    raise ValueError(
                        f"min_liters_per_fish must be positive for fish '{fish_key}'"
                    )

                self._fish_cache[fish_key] = Fish.from_dict(fish_data)

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Fish database file not found: {self._yaml_file_path}"
            ) from exc
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}") from e
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid fish data: {e}") from e

    def get_all_fish(self) -> dict[str, Fish]:
        """
        Retrieve a copy of all fish data from the repository.

        Returns:
            Dict[str, Fish]: A dictionary containing all fish entries where keys are
                            fish identifiers and values are Fish objects. Returns a
                            copy to prevent external modification of the internal cache.
        """
        return self._fish_cache.copy()

    def get_fish_by_key(self, fish_key: str) -> Fish:
        """
        Get a specific fish by its key.

        Args:
            fish_key: The key identifier for the fish

        Returns:
            Fish: The fish object

        Raises:
            KeyError: If fish key is not found
        """
        if fish_key.lower() not in self._fish_cache:
            raise KeyError(f"Fish key '{fish_key}' not found in database")
        return self._fish_cache[fish_key.lower()]

    def fish_exists(self, fish_key: str) -> bool:
        """
        Check if a fish exists in the repository by its key.

        Args:
            fish_key (str): The key identifier for the fish to check.

        Returns:
            bool: True if the fish exists in the cache, False otherwise.

        Note:
            The comparison is case-insensitive as the fish_key is converted to lowercase.
        """
        return fish_key.lower() in self._fish_cache

    def get_fish_keys(self) -> list[str]:
        """
        Get a sorted list of all fish keys from the fish cache.

        Returns:
            list[str]: A sorted list of fish keys (identifiers) available in the repository.
        """
        return sorted(self._fish_cache.keys())
