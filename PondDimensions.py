from dataclasses import dataclass


@dataclass
class PondDimensions:
    """
    Represents the physical dimensions and shape characteristics of a pond.

    This class stores the essential measurements needed to calculate pond volume,
    surface area, and other properties required for pond planning and management.

    Attributes:
        length_meters (float): The length of the pond in meters (longest dimension)
        width_meters (float): The width of the pond in meters (shortest dimension)
        avg_depth_meters (float): The average depth of the pond in meters
        shape (str): The geometric shape of the pond. Defaults to "rectangular".
            Supported shapes include: rectangular, circular, oval, kidney, L-shaped,
            triangular, hexagonal, octagonal, irregular

    Note:
        For non-rectangular shapes, length_meters and width_meters may represent
        different dimensions (e.g., diameter for circular ponds, or bounding box
        dimensions for irregular shapes).
    """

    length_meters: float
    width_meters: float
    avg_depth_meters: float
    shape: str = (
        "rectangular"  # rectangular, circular, oval, kidney, L-shaped, triangular,
    )
