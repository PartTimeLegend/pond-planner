from dataclasses import dataclass


@dataclass
class Fish:
    """
    Represents a fish species with its characteristics for pond planning.
    This class stores essential information about fish species needed for calculating
    pond capacity, bioload, and stocking requirements.
    Attributes:
        name (str): The common or scientific name of the fish species.
        adult_length_cm (float): The expected adult length of the fish in centimeters.
        bioload_factor (float): A multiplier representing the fish's waste production
            relative to other species. Higher values indicate more waste production.
        min_liters_per_fish (int): The minimum water volume in liters required per
            individual fish of this species for healthy living conditions.
    """

    name: str
    adult_length_cm: float
    bioload_factor: float  # waste production multiplier
    min_liters_per_fish: int

    @classmethod
    def from_dict(cls, data: dict) -> "Fish":
        """
        Create a Fish instance from a dictionary of data.

        Args:
            data (dict): Dictionary containing fish data with keys:
                name, adult_length_cm, bioload_factor, min_liters_per_fish

        Returns:
            Fish: A new Fish instance created from the provided data
        """
        return cls(
            name=data["name"],
            adult_length_cm=data["adult_length_cm"],
            bioload_factor=data["bioload_factor"],
            min_liters_per_fish=data["min_liters_per_fish"],
        )
