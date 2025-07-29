# hexagonal, octagonal, irregular

from calculators.EquipmentCalculator import EquipmentCalculator
from calculators.StockingCalculator import StockingCalculator
from calculators.VolumeCalculator import VolumeCalculator
from interfaces.DataRepository import DataRepository
from interfaces.ShapeRepository import ShapeRepository
from interfaces.TransactionManager import TransactionManager
from interfaces.ValidationService import ValidationService
from PondDimensions import PondDimensions
from repositories.YamlFishRepository import YamlFishRepository
from repositories.YamlShapeRepository import YamlShapeRepository
from services.PondPersistenceService import PondConfiguration, PondPersistenceService
from services.PondStockManager import PondStockManager
from services.PondTransactionManager import PondTransactionManager
from services.PondValidationService import PondValidationService
from services.ReportGenerator import ReportGenerator


class PondPlanner:
    """
    Main facade class for pond planning system following SOLID principles.

    This class acts as a facade, coordinating between different specialized services
    and calculators. It follows the Single Responsibility Principle by delegating
    specific responsibilities to dedicated classes.

    Uses dependency injection to allow for different data sources and implementations.
    """

    def __init__(
        self,
        fish_repository: DataRepository = None,
        validation_service: ValidationService = None,
        transaction_manager: TransactionManager = None,
        shape_repository: ShapeRepository = None,
    ):
        """
        Initialize pond planner with optional dependency injection.

        Args:
            fish_repository: Optional fish data repository. Defaults to YAML implementation.
            validation_service: Optional validation service. Defaults to pond validation.
            transaction_manager: Optional transaction manager. Defaults to pond transaction manager.
            shape_repository: Optional shape repository. Defaults to YAML implementation.
        """
        # Use dependency injection with default fallbacks (Open/Closed Principle)
        self._fish_repository = fish_repository or YamlFishRepository()
        self._shape_repository = shape_repository or YamlShapeRepository()
        self._validation_service = validation_service or PondValidationService(
            self._shape_repository
        )
        self._transaction_manager = transaction_manager or PondTransactionManager()

        # Initialize services with proper dependencies
        self._stock_manager = PondStockManager(
            self._fish_repository, self._validation_service, self._transaction_manager
        )
        self._report_generator = ReportGenerator(
            self._fish_repository, self._shape_repository
        )
        self._stocking_calculator = StockingCalculator(self._fish_repository)
        self._volume_calculator = VolumeCalculator(self._shape_repository)
        self._persistence_service = PondPersistenceService()

        # Pond state
        self.dimensions: PondDimensions = None

    def set_dimensions(
        self, length: float, width: float, depth: float, shape: str = "rectangular"
    ) -> None:
        """
        Set the dimensions and shape of the pond with validation and transaction support.

        This method validates the provided dimensions and shape, then atomically updates
        the pond dimensions. If validation fails, no changes are made to the pond state.

        Args:
            length (float): The length of the pond in meters. Must be positive.
            width (float): The width of the pond in meters. Must be positive.
            depth (float): The average depth of the pond in meters. Must be positive.
            shape (str, optional): The shape of the pond. Defaults to "rectangular".
                                 Must be one of the supported shapes from the shape repository.

        Raises:
            ValueError: If any dimension is not positive, or if the shape is not supported.
            RuntimeError: If a transaction error occurs during the operation.

        Note:
            This operation is atomic - either all dimensions are set successfully,
            or the pond state remains unchanged.

        Example:
            >>> planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")
            >>> planner.set_dimensions(4.0, 4.0, 2.0, "circular")
        """

        def _set_dimensions_operation():
            # Validate all inputs
            dimension_errors = self._validation_service.validate_dimensions(
                length, width, depth
            )
            shape_errors = self._validation_service.validate_pond_shape(shape)

            all_errors = dimension_errors + shape_errors
            if all_errors:
                raise ValueError(f"Invalid dimensions: {'; '.join(all_errors)}")

            # Save current state for rollback
            self._transaction_manager.save_state("dimensions", self.dimensions)

            # Set new dimensions
            self.dimensions = PondDimensions(length, width, depth, shape)

        self._transaction_manager.execute_transaction(_set_dimensions_operation)

    def add_fish_batch(self, fish_batch: dict[str, int]) -> None:
        """
        Add multiple fish types in a single atomic operation.

        This method demonstrates ACID compliance by ensuring that either all fish
        are added successfully, or none are added at all. All fish types and
        quantities are validated before any changes are made to the stock.

        Args:
            fish_batch (Dict[str, int]): Dictionary mapping fish type names to quantities.
                                       All fish types must exist in the database and
                                       all quantities must be positive integers.

        Raises:
            ValueError: If any fish type is unknown, any quantity is invalid,
                       or if the fish_batch data structure is malformed.
            RuntimeError: If a transaction error occurs during the operation.

        Example:
            >>> batch = {"goldfish": 10, "koi": 3, "shubunkin": 5}
            >>> planner.add_fish_batch(batch)
        """
        self._stock_manager.bulk_add_fish(fish_batch)

    def calculate_volume_liters(self) -> float:
        """
        Calculate the total volume of the pond in liters using the volume calculator.

        This method uses the configured shape repository and volume calculator to
        compute the pond volume based on the current dimensions and shape. The
        calculation takes into account shape-specific formulas and multipliers.

        Returns:
            float: The volume of the pond in liters. Precision depends on the
                  shape complexity and calculation method used.

        Raises:
            ValueError: If pond dimensions are not set, or if dimensions are invalid.
            KeyError: If the pond shape is not found in the shape repository.

        Note:
            The volume is calculated as surface area × depth, with shape-specific
            area calculations applied based on the pond's shape configuration.

        Example:
            >>> planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")
            >>> volume = planner.calculate_volume_liters()
            >>> print(f"Pond volume: {volume:,.0f} liters")
        """
        if not self.dimensions:
            raise ValueError("Pond dimensions not set")

        return self._volume_calculator.calculate_volume_liters(self.dimensions)

    # Properties for accessing internal state (following encapsulation)
    @property
    def fish_stock(self) -> dict[str, int]:
        """Get current fish stock (read-only)."""
        return self._stock_manager.get_stock()

    @property
    def fish_database(self) -> dict[str, any]:
        """
        Get fish database for backwards compatibility.

        This method provides access to the complete fish database by delegating
        to the fish repository. It maintains backward compatibility for existing
        code that expects to access fish data through this method.

        Returns:
            Dict[str, any]: A dictionary containing all fish data from the repository,
                           where keys are fish identifiers and values contain fish
                           information and properties.

        Note:
            This method is provided for backwards compatibility. New code should
            consider using the fish repository directly for better separation of concerns.
        """
        return self._fish_repository.get_all_fish()

    def add_fish(self, fish_type: str, quantity: int):
        """
        Add fish to the pond's stock inventory with validation and transaction support.

        This method validates the fish type against the database and ensures the
        quantity is valid before adding to the stock. The operation is performed
        within a transaction context for consistency.

        Args:
            fish_type (str): The type of fish to add. Must be a valid fish type
                           from the fish database. Lookup is case-insensitive.
            quantity (int): The number of fish to add to the stock. Must be positive.

        Raises:
            ValueError: If the fish_type is not found in the database, or if
                       the quantity is not positive.
            RuntimeError: If a transaction error occurs during the operation.

        Note:
            - Fish type lookup is case-insensitive for user convenience
            - If fish of this type already exist in stock, quantities are added together
            - The operation is atomic and will rollback on any error

        Example:
            >>> planner.add_fish("goldfish", 5)
            >>> planner.add_fish("Koi", 3)  # Case-insensitive
        """
        self._stock_manager.add_fish(fish_type, quantity)

    def remove_fish(self, fish_type: str, quantity: int):
        """
        Remove a specified quantity of fish from the pond's fish stock.

        This method safely removes fish from the stock with proper validation
        and transaction support. If the removal would result in negative stock,
        the fish type is removed entirely from the stock.

        Args:
            fish_type (str): The type of fish to remove. Case-insensitive lookup.
            quantity (int): The number of fish to remove. Must be positive.

        Raises:
            ValueError: If the quantity is not positive.
            RuntimeError: If a transaction error occurs during the operation.

        Note:
            - Fish type lookup is case-insensitive
            - If quantity exceeds current stock, all fish of that type are removed
            - If stock reaches zero, the fish type is removed from the dictionary
            - If the fish type doesn't exist in stock, no action is taken (no error)
            - The operation is atomic and will rollback on any error

        Example:
            >>> planner.remove_fish("goldfish", 2)  # Remove 2 goldfish
            >>> planner.remove_fish("koi", 100)     # Removes all koi if < 100 in stock
        """
        self._stock_manager.remove_fish(fish_type, quantity)

    def calculate_required_volume(self) -> float:
        """
        Calculate the total volume of water required for all fish in the current stock.

        This method iterates through all fish types and their quantities in the current
        fish stock, retrieves the minimum water requirements for each fish type from
        the fish database, and calculates the total volume needed for optimal fish health.

        Returns:
            float: The total volume in liters required to house all fish in the stock.
                  This is the sum of (minimum liters per fish × quantity) for each fish type.

        Raises:
            KeyError: If any fish type in the stock is not found in the database
                     (this should not happen with proper validation).

        Note:
            - Calculation is based on minimum space requirements per fish species
            - Does not account for compatibility between different fish species
            - Assumes optimal water conditions and filtration
            - Returns 0.0 if no fish are currently in stock

        Example:
            >>> # Stock contains 2 goldfish (75L each) and 1 koi (950L)
            >>> required = planner.calculate_required_volume()
            >>> print(f"Required volume: {required} liters")  # Outputs: 1100.0 liters
        """
        return self._stocking_calculator.calculate_required_volume(
            self._stock_manager.get_stock()
        )

    def calculate_bioload(self) -> float:
        """
        Calculate the total bioload of all fish in the pond.

        The bioload represents the biological waste production and oxygen consumption
        of the fish stock. It is calculated by summing the product of each fish type's
        bioload factor and its quantity in the pond. Higher bioload values indicate
        greater impact on water quality and filtration requirements.

        Returns:
            float: The total bioload value for all fish in the pond. Higher values
                  indicate greater biological impact on the pond ecosystem and
                  increased filtration/circulation requirements.

        Raises:
            KeyError: If any fish type in the stock is not found in the database.

        Note:
            - Bioload factors are relative values (1.0 = baseline, >1.0 = higher waste)
            - Used for calculating pump, filter, and UV sterilizer requirements
            - Does not account for fish age, feeding frequency, or water temperature
            - Returns 0.0 if no fish are currently in stock

        Example:
            >>> # Stock contains 5 goldfish (1.0 each) and 2 koi (2.5 each)
            >>> bioload = planner.calculate_bioload()
            >>> print(f"Total bioload: {bioload}")  # Outputs: 10.0
        """
        return self._stocking_calculator.calculate_bioload(
            self._stock_manager.get_stock()
        )

    def calculate_pump_size(self) -> tuple[int, str]:
        """
        Calculate the required pump size for the pond based on volume and bioload.

        This method determines the pump flow rate needed to maintain proper water
        circulation by calculating a base turnover rate and adjusting it based on
        the pond's bioload. Higher bioload requires increased circulation.

        Returns:
            Tuple[int, str]: A tuple containing:
                - required_lph (int): Required pump flow rate in liters per hour
                - category (str): Bioload category classification:
                    * "Light bioload" (≤5 points)
                    * "Medium bioload" (6-15 points)
                    * "Heavy bioload" (>15 points)

        Raises:
            ValueError: If pond dimensions are not set, or if calculated values are invalid.

        Note:
            - Base calculation assumes complete water turnover every 2 hours
            - Bioload adds 10% flow increase per bioload point above baseline
            - Categories help users understand filtration complexity requirements
            - Recommendations assume standard pond setup and maintenance

        Example:
            >>> flow_rate, category = planner.calculate_pump_size()
            >>> print(f"Pump requirement: {flow_rate:,} LPH ({category})")
        """
        if not self.dimensions:
            raise ValueError("Pond dimensions not set")

        volume = self.calculate_volume_liters()
        bioload = self.calculate_bioload()
        return EquipmentCalculator.calculate_pump_size(volume, bioload)

    def calculate_filter_size(self) -> dict[str, str]:
        """
        Calculate the required filtration system specifications based on pond volume and bioload.

        This method determines the appropriate biological filter size, UV sterilizer wattage,
        and mechanical filter requirements. The calculations scale with both pond size and
        the biological load from fish waste production.

        Returns:
            Dict[str, str]: A dictionary containing filtration specifications:
                - 'biological_filter': Required filter media volume in liters
                - 'uv_sterilizer': Required UV sterilizer wattage in watts
                - 'mechanical_filter': Recommended pre-filter micron capability

        Raises:
            ValueError: If pond dimensions are not set, or if calculated values are invalid.

        Note:
            - Biological filter sized as 5-15% of pond volume based on bioload
            - UV sterilizer uses 1W per 190-285L depending on bioload intensity
            - Mechanical filter recommendation is based on typical pond requirements
            - Higher bioload increases all filtration requirements proportionally

        Example:
            >>> filters = planner.calculate_filter_size()
            >>> for component, spec in filters.items():
            ...     print(f"{component}: {spec}")
        """
        if not self.dimensions:
            raise ValueError("Pond dimensions not set")

        volume = self.calculate_volume_liters()
        bioload = self.calculate_bioload()
        return EquipmentCalculator.calculate_filter_specifications(volume, bioload)

    def get_stocking_recommendations(self) -> dict[str, int]:
        """
        Calculate the maximum number of each fish type that can be stocked in the pond.

        This method determines stocking recommendations based on the pond's available
        volume and each fish species' minimum space requirements. The calculations
        assume optimal conditions and proper filtration.

        Returns:
            Dict[str, int]: A dictionary mapping fish display names to their maximum
                          recommended quantities for the pond. Keys are fish names (str)
                          and values are maximum counts (int).

        Raises:
            ValueError: If pond dimensions have not been set.
            KeyError: If fish database is corrupted or inaccessible.

        Note:
            - Calculations based on minimum liters per fish requirement for each species
            - Recommendations assume optimal conditions (good filtration, regular maintenance)
            - Does not account for fish compatibility or territorial behavior
            - May need adjustment based on actual filtration capacity and maintenance schedule
            - Results show theoretical maximum; practical stocking may be lower

        Example:
            >>> recommendations = planner.get_stocking_recommendations()
            >>> for fish_name, max_count in recommendations.items():
            ...     if max_count > 0:
            ...         print(f"{fish_name}: up to {max_count} fish")
        """
        if not self.dimensions:
            raise ValueError("Pond dimensions not set")

        volume = self.calculate_volume_liters()
        return self._stocking_calculator.get_stocking_recommendations(volume)

    def get_available_shapes(self) -> list[str]:
        """
        Get a list of all available pond shapes from the shape repository.

        This method retrieves the complete list of supported pond shapes that can
        be used with the set_dimensions method. The shapes are loaded from the
        configured shape repository (typically YAML configuration).

        Returns:
            List[str]: A sorted list of strings representing the different pond shapes
                      that can be selected for pond planning. Includes geometric shapes
                      like rectangular, circular, and oval, as well as decorative
                      options like kidney, l-shaped, and figure-8 shapes.

        Raises:
            RuntimeError: If the shape repository is inaccessible or corrupted.

        Note:
            - Shape list is loaded from external configuration for extensibility
            - New shapes can be added by updating the shape repository
            - Each shape has specific calculation formulas and validation rules
            - Shape names are case-insensitive when used with set_dimensions

        Example:
            >>> shapes = planner.get_available_shapes()
            >>> print("Available shapes:", ", ".join(shapes))
        """
        return self._shape_repository.get_shape_keys()

    def get_shapes_by_category(self, category: str) -> list[str]:
        """
        Get shapes belonging to a specific category from the shape repository.

        This method allows filtering of available shapes by category, helping
        users find shapes that match their design preferences or requirements.

        Args:
            category (str): The category name to filter by. Common categories include:
                          - "geometric": Standard geometric shapes (rectangular, circular, etc.)
                          - "organic": Natural, curved shapes (kidney, teardrop, etc.)
                          - "complex": Multi-part or decorative shapes (figure-8, star, etc.)

        Returns:
            List[str]: A list of shape names belonging to the specified category.
                      Returns empty list if category doesn't exist.

        Note:
            - Categories are defined in the shape repository configuration
            - Category lookup is case-insensitive for user convenience
            - Useful for UI organization and guided shape selection
            - Categories may overlap (shapes can belong to multiple categories)

        Example:
            >>> geometric_shapes = planner.get_shapes_by_category("geometric")
            >>> print(f"Geometric shapes: {', '.join(geometric_shapes)}")
        """
        return self._shape_repository.get_shapes_by_category(category)

    def get_fish_types_list(self) -> list[str]:
        """
        Get a sorted list of all available fish type identifiers from the fish database.

        This method returns the internal fish type keys used by the system, which
        can be used with add_fish, remove_fish, and other fish-related methods.

        Returns:
            List[str]: A sorted list of fish type identifiers (keys) from the fish database.
                      These are typically lowercase, underscore-separated strings.

        Raises:
            RuntimeError: If the fish database is inaccessible or corrupted.

        Note:
            - Returns internal fish type keys, not display names
            - Use fish_database property to get full fish information including display names
            - Fish type keys are case-insensitive when used in other methods
            - List is sorted alphabetically for consistent ordering

        Example:
            >>> fish_types = planner.get_fish_types_list()
            >>> for fish_type in fish_types[:5]:  # Show first 5
            ...     fish = planner.fish_database[fish_type]
            ...     print(f"{fish_type}: {fish.name}")
        """
        return sorted(self.fish_database.keys())

    def generate_report(self) -> str:
        """
        Generate a comprehensive pond planning report with specifications, analysis, and recommendations.

        This method creates a detailed text report that includes pond dimensions, current fish
        stock, stocking analysis with bioload calculations, equipment sizing recommendations,
        and maximum stocking guidelines. The report provides all information needed for
        pond planning and equipment purchasing decisions.

        Returns:
            str: A formatted multi-line string containing the complete pond planning report.
                Returns an error message if pond dimensions are not set or if report
                generation fails due to data issues.

        Raises:
            No exceptions are raised - errors are captured and returned as error messages
            in the report string for user-friendly error handling.

        Note:
            - Report generation delegates to the ReportGenerator service
            - Includes pond specifications, fish stock, stocking analysis, and equipment recommendations
            - Provides both current status and maximum capacity information
            - Equipment recommendations scale with pond volume and current bioload
            - Report format is designed for both screen display and printing

        The report includes:
            - Pond specifications (dimensions, shape, volume)
            - Current fish stock listing with species names
            - Stocking analysis with adequacy assessment (adequate/overstocked)
            - Equipment recommendations (pump, biological filter, UV sterilizer, mechanical filter)
            - Maximum stocking recommendations by fish species

        Example:
            >>> report = planner.generate_report()
            >>> print(report)
            >>> # Or save to file
            >>> with open("pond_plan.txt", "w") as f:
            ...     f.write(report)
        """
        return self._report_generator.generate_comprehensive_report(
            self.dimensions, self._stock_manager.get_stock()
        )

    def save_pond(self, name: str, description: str = "") -> str:
        """
        Save the current pond configuration to file.

        Args:
            name: Name for the saved pond configuration
            description: Optional description of the pond

        Returns:
            str: Filename of the saved configuration

        Raises:
            ValueError: If no pond dimensions are set
            OSError: If the file cannot be saved

        Example:
            >>> planner.set_dimensions(5, 3, 1.5, "rectangular")
            >>> planner.add_fish("goldfish", 10)
            >>> filename = planner.save_pond("My Garden Pond", "Beautiful koi pond")
            >>> print(f"Saved as: {filename}")
        """
        if self.dimensions is None:
            raise ValueError("Cannot save pond: no dimensions set")

        configuration = PondConfiguration(
            name=name,
            dimensions=self.dimensions,
            fish_stock=self._stock_manager.get_stock(),
            description=description,
        )

        return self._persistence_service.save_pond(configuration)

    def load_pond(self, filename: str) -> None:
        """
        Load a pond configuration from file.

        Args:
            filename: Filename of the saved configuration (with or without .json extension)

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the file contains invalid data

        Example:
            >>> planner.load_pond("my_garden_pond")
            >>> print(f"Loaded pond: {planner.dimensions.shape}")
        """
        configuration = self._persistence_service.load_pond(filename)

        # Load dimensions
        self.dimensions = configuration.dimensions

        # Load fish stock
        self._stock_manager.clear_stock()
        for fish_type, quantity in configuration.fish_stock.items():
            self._stock_manager.add_fish(fish_type, quantity)

    def list_saved_ponds(self) -> list[dict[str, any]]:
        """
        List all saved pond configurations.

        Returns:
            List of dictionaries with pond metadata

        Example:
            >>> ponds = planner.list_saved_ponds()
            >>> for pond in ponds:
            ...     print(f"{pond['name']}: {pond['fish_count']} fish")
        """
        return self._persistence_service.list_saved_ponds()

    def delete_saved_pond(self, filename: str) -> bool:
        """
        Delete a saved pond configuration.

        Args:
            filename: Filename of the configuration to delete

        Returns:
            bool: True if deleted successfully, False if file didn't exist

        Example:
            >>> success = planner.delete_saved_pond("old_pond")
            >>> print("Deleted" if success else "File not found")
        """
        return self._persistence_service.delete_pond(filename)

    def pond_exists(self, filename: str) -> bool:
        """
        Check if a saved pond configuration exists.

        Args:
            filename: Filename to check

        Returns:
            bool: True if the configuration exists

        Example:
            >>> if planner.pond_exists("my_pond"):
            ...     planner.load_pond("my_pond")
        """
        return self._persistence_service.pond_exists(filename)

    def get_fish_stock(self) -> dict[str, int]:
        """
        Get the current fish stock in the pond.

        Returns:
            Dictionary mapping fish types to quantities

        Example:
            >>> stock = planner.get_fish_stock()
            >>> print(f"Current fish: {stock}")
        """
        return self._stock_manager.get_stock()
