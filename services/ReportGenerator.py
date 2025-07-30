from calculators.EquipmentCalculator import EquipmentCalculator
from calculators.stocking_calculator import StockingCalculator
from calculators.volume_calculator import VolumeCalculator
from interfaces.data_repository import DataRepository
from interfaces.shape_repository import ShapeRepository
from PondDimensions import PondDimensions
from repositories.YamlShapeRepository import YamlShapeRepository


class ReportGenerator:
    """
    Generates comprehensive pond planning reports.
    """

    def __init__(
        self, fish_repository: DataRepository, shape_repository: ShapeRepository = None
    ):
        """
        Initialize with dependencies.

        Args:
            fish_repository: Fish data repository
            shape_repository: Shape data repository
        """
        self._fish_repository = fish_repository
        self._shape_repository = shape_repository or YamlShapeRepository()
        self._stocking_calculator = StockingCalculator(fish_repository)
        self._volume_calculator = VolumeCalculator(self._shape_repository)

    def generate_comprehensive_report(
        self, dimensions: PondDimensions, fish_stock: dict[str, int]
    ) -> str:
        """
        Generate a comprehensive pond planning report.

        Args:
            dimensions: Pond dimensions
            fish_stock: Current fish stock

        Returns:
            str: Formatted report
        """
        if not dimensions:
            return "Error: Pond dimensions not set"

        try:
            volume = self._volume_calculator.calculate_volume_liters(dimensions)
            required_volume = self._stocking_calculator.calculate_required_volume(
                fish_stock
            )
            bioload = self._stocking_calculator.calculate_bioload(fish_stock)
            pump_lph, pump_category = EquipmentCalculator.calculate_pump_size(
                volume, bioload
            )
            filter_specs = EquipmentCalculator.calculate_filter_specifications(
                volume, bioload
            )
            recommendations = self._stocking_calculator.get_stocking_recommendations(
                volume
            )

            return self._format_report(
                dimensions,
                volume,
                fish_stock,
                required_volume,
                bioload,
                pump_lph,
                pump_category,
                filter_specs,
                recommendations,
            )

        except Exception as e:
            return f"Error generating report: {str(e)}"

    def _format_report(
        self,
        dimensions: PondDimensions,
        volume: float,
        fish_stock: dict[str, int],
        required_volume: float,
        bioload: float,
        pump_lph: int,
        pump_category: str,
        filter_specs: dict[str, str],
        recommendations: dict[str, int],
    ) -> str:
        """
        Format the report with all calculated data.
        Args:
            dimensions: Pond dimensions
            volume: Total pond volume in liters
            fish_stock: Current fish stock
            required_volume: Required volume for current stock
            bioload: Total bioload factor
            pump_lph: Required pump size in LPH
            pump_category: Bioload category for pump
            filter_specs: Filter specifications
            recommendations: Maximum stocking recommendations
        Returns:
            str: Formatted report string
        """

        report = f"""
POND PLANNING REPORT
====================

Pond Specifications:
- Dimensions: {dimensions.length_meters}m x {dimensions.width_meters}m x {dimensions.avg_depth_meters}m
- Shape: {dimensions.shape.title()}
- Total Volume: {volume:,.0f} liters

Current Fish Stock:
"""

        if fish_stock:
            for fish_type, quantity in fish_stock.items():
                fish = self._fish_repository.get_fish_by_key(fish_type)
                report += f"- {fish.name}: {quantity} fish\n"

            is_adequate = volume >= required_volume
            report += f"""
Stocking Analysis:
- Required Volume: {required_volume:,.0f} liters
- Available Volume: {volume:,.0f} liters
- Status: {"✓ Adequate" if is_adequate else "⚠ Overstocked"}
- Total Bioload: {bioload:.1f}
"""
        else:
            report += "- No fish currently stocked\n"

        report += f"""
Equipment Recommendations:
- Pump Size: {pump_lph:,} LPH ({pump_category})
- {filter_specs["biological_filter"]}
- UV Sterilizer: {filter_specs["uv_sterilizer"]}
- Mechanical Filter: {filter_specs["mechanical_filter"]}

Maximum Stocking Recommendations:
"""
        for fish_name, max_count in recommendations.items():
            report += f"- {fish_name}: {max_count} fish max\n"

        return report
