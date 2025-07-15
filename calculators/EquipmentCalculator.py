from typing import Dict, Tuple


class EquipmentCalculator:
    """
    Handles equipment sizing calculations for pond systems.
    Follows Single Responsibility Principle by focusing on equipment calculations.
    """

    @staticmethod
    def calculate_pump_size(pond_volume_liters: float, bioload: float) -> Tuple[int, str]:
        """
        Calculate the required pump size based on volume and bioload.

        Args:
            pond_volume_liters: Pond volume in liters
            bioload: Total bioload factor

        Returns:
            Tuple[int, str]: Required flow rate in LPH and bioload category
        """
        if pond_volume_liters <= 0:
            raise ValueError("Pond volume must be positive")
        if bioload < 0:
            raise ValueError("Bioload cannot be negative")

        # Base turnover: complete water change every 2 hours
        base_flow = pond_volume_liters / 2

        # Adjust for bioload (10% increase per bioload point)
        bioload_multiplier = 1 + (bioload / 10)
        required_lph = int(base_flow * bioload_multiplier)

        # Determine bioload category
        if bioload <= 5:
            category = "Light bioload"
        elif bioload <= 15:
            category = "Medium bioload"
        else:
            category = "Heavy bioload"

        return required_lph, category

    @staticmethod
    def calculate_filter_specifications(pond_volume_liters: float, bioload: float) -> Dict[str, str]:
        """
        Calculate filtration system specifications.

        Args:
            pond_volume_liters: Pond volume in liters
            bioload: Total bioload factor

        Returns:
            Dict[str, str]: Filter specifications
        """
        if pond_volume_liters <= 0:
            raise ValueError("Pond volume must be positive")
        if bioload < 0:
            raise ValueError("Bioload cannot be negative")

        # Biological filter volume (5-15% of pond volume based on bioload)
        bio_filter_percent = min(15, 5 + bioload)
        bio_filter_liters = int(pond_volume_liters * bio_filter_percent / 100)

        # UV sterilizer wattage (varies with bioload)
        uv_watts_per_liter = 1/285 if bioload <= 10 else 1/190
        uv_watts = int(pond_volume_liters * uv_watts_per_liter)

        return {
            "biological_filter": f"{bio_filter_liters} liters filter media",
            "uv_sterilizer": f"{uv_watts} watts",
            "mechanical_filter": "Pre-filter with 50-100 micron capability"
        }
