from typing import Dict

from interfaces.DataRepository import DataRepository


class StockingCalculator:
    """
    Handles fish stocking calculations and validations.
    Follows Single Responsibility Principle by focusing on stocking logic.
    """

    def __init__(self, fish_repository: DataRepository):
        """
        Initialize with a fish data repository.

        Args:
            fish_repository: Implementation of DataRepository interface
        """
        self._fish_repository = fish_repository

    def calculate_required_volume(self, fish_stock: Dict[str, int]) -> float:
        """
        Calculate the total volume required for optimal housing of all fish in the stock.

        This method iterates through the fish stock, retrieves minimum space requirements
        for each species from the repository, and calculates the total volume needed
        to ensure healthy living conditions for all fish.

        Args:
            fish_stock (Dict[str, int]): Dictionary mapping fish type keys to quantities.
                                       Fish types must exist in the repository.

        Returns:
            float: Total volume in liters required to house all fish according to
                  species-specific minimum space requirements. Returns 0.0 if stock is empty.

        Raises:
            KeyError: If any fish type in the stock is not found in the repository.
            ValueError: If fish data contains invalid values (None or negative).

        Note:
            - Based on minimum liters per fish for each species in repository
            - Assumes optimal water conditions and proper filtration
            - Does not account for fish compatibility or territorial requirements
            - Ignores fish types with zero or negative quantities
            - Calculation: sum of (min_liters_per_fish × quantity) for each species

        Example:
            >>> stock = {"goldfish": 5, "koi": 2}  # 5×75L + 2×950L = 2275L
            >>> required = calculator.calculate_required_volume(stock)
            >>> print(f"Required: {required:,.0f} liters")
        """
        total_liters = 0
        for fish_type, quantity in fish_stock.items():
            if quantity <= 0:
                continue

            fish = self._fish_repository.get_fish_by_key(fish_type)

            # Defensive check for None values
            if fish.min_liters_per_fish is None:
                raise ValueError(
                    f"Fish '{fish_type}' has invalid min_liters_per_fish value (None)"
                )
            if fish.min_liters_per_fish <= 0:
                raise ValueError(
                    f"Fish '{fish_type}' has invalid min_liters_per_fish value ({fish.min_liters_per_fish})"
                )

            total_liters += fish.min_liters_per_fish * quantity
        return total_liters

    def calculate_bioload(self, fish_stock: Dict[str, int]) -> float:
        """
        Calculate the total bioload factor for all fish in the stock.

        Bioload represents the biological waste production and oxygen consumption
        impact of the fish population. Higher bioload requires more powerful
        filtration and circulation systems.

        Args:
            fish_stock (Dict[str, int]): Dictionary mapping fish type keys to quantities.
                                       Fish types must exist in the repository.

        Returns:
            float: Total bioload value representing cumulative biological impact.
                  Baseline species have factor 1.0; higher values indicate greater
                  waste production. Returns 0.0 if stock is empty.

        Raises:
            KeyError: If any fish type in the stock is not found in the repository.
            ValueError: If fish data contains invalid values (None or negative).

        Note:
            - Bioload factors are relative values (1.0 = baseline, >1.0 = higher waste)
            - Used for calculating pump flow rates and filter requirements
            - Does not account for fish age, feeding frequency, or water temperature
            - Ignores fish types with zero or negative quantities
            - Calculation: sum of (bioload_factor × quantity) for each species

        Example:
            >>> stock = {"goldfish": 5, "koi": 2}  # 5×1.0 + 2×2.5 = 10.0
            >>> bioload = calculator.calculate_bioload(stock)
            >>> print(f"Total bioload: {bioload}")
        """
        total_bioload = 0
        for fish_type, quantity in fish_stock.items():
            if quantity <= 0:
                continue

            fish = self._fish_repository.get_fish_by_key(fish_type)

            # Defensive check for None values
            if fish.bioload_factor is None:
                raise ValueError(
                    f"Fish '{fish_type}' has invalid bioload_factor value (None)"
                )
            if fish.bioload_factor <= 0:
                raise ValueError(
                    f"Fish '{fish_type}' has invalid bioload_factor value ({fish.bioload_factor})"
                )

            total_bioload += fish.bioload_factor * quantity
        return total_bioload

    def get_stocking_recommendations(self, pond_volume_liters: float) -> Dict[str, int]:
        """
        Calculate the maximum number of each fish species that can be stocked in the pond.

        This method determines theoretical maximum stocking levels based on pond volume
        and species-specific minimum space requirements. Results assume optimal
        conditions and should be adjusted for practical considerations.

        Args:
            pond_volume_liters (float): Available pond volume in liters. Must be positive.

        Returns:
            Dict[str, int]: Dictionary mapping fish display names to maximum recommended
                          quantities. Keys are user-friendly fish names, values are
                          maximum counts based purely on space requirements.

        Raises:
            ValueError: If pond volume is not positive, or if fish data is invalid.
            RuntimeError: If fish repository is inaccessible.

        Note:
            - Calculations based solely on minimum space requirements per species
            - Assumes optimal water conditions and maintenance
            - Does not consider fish compatibility, territorial behavior, or feeding competition
            - Results are theoretical maximums; practical stocking should be lower
            - May need adjustment for actual filtration capacity and maintenance schedule
            - Uses fish display names (not internal keys) for user-friendly results

        Example:
            >>> recommendations = calculator.get_stocking_recommendations(5000.0)
            >>> for fish_name, max_count in recommendations.items():
            ...     if max_count > 10:  # Show only realistic options
            ...         print(f"{fish_name}: up to {max_count}")
        """
        if pond_volume_liters <= 0:
            raise ValueError("Pond volume must be positive")

        recommendations = {}
        all_fish = self._fish_repository.get_all_fish()

        for fish in all_fish.values():
            # Defensive check for None values
            if fish.min_liters_per_fish is None:
                continue  # Skip fish with invalid data
            if fish.min_liters_per_fish <= 0:
                continue  # Skip fish with invalid requirements

            max_count = int(pond_volume_liters / fish.min_liters_per_fish)
            recommendations[fish.name] = max_count

        return recommendations

    def validate_stocking(
        self, fish_stock: Dict[str, int], pond_volume_liters: float
    ) -> bool:
        """
        Validate if the current stocking level is within the pond's capacity.

        This method compares the total volume required by the current fish stock
        against the available pond volume to determine if the pond is adequately
        sized or overstocked.

        Args:
            fish_stock (Dict[str, int]): Current fish stock mapping types to quantities.
            pond_volume_liters (float): Available pond volume in liters.

        Returns:
            bool: True if the pond has adequate volume for the current stock
                 (pond volume >= required volume), False if overstocked.

        Raises:
            KeyError: If any fish type in stock is not found in repository.
            ValueError: If pond volume is negative.

        Note:
            - Validation based on minimum space requirements only
            - Does not account for fish growth, filtration capacity, or maintenance
            - Returns True for equal volumes (exactly adequate)
            - Useful for determining if additional fish can be added
            - Should be combined with bioload and filtration capacity checks

        Example:
            >>> stock = {"goldfish": 10, "koi": 3}
            >>> is_adequate = calculator.validate_stocking(stock, 5000.0)
            >>> if not is_adequate:
            ...     print("Warning: Pond may be overstocked")
        """
        required_volume = self.calculate_required_volume(fish_stock)
        return pond_volume_liters >= required_volume
        return pond_volume_liters >= required_volume
