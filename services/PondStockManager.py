from interfaces.data_repository import DataRepository
from interfaces.TransactionManager import TransactionManager
from interfaces.ValidationService import ValidationService


class PondStockManager:
    """
    Manages fish stock operations with validation and transaction support.
    """

    def __init__(
        self,
        fish_repository: DataRepository,
        validation_service: ValidationService,
        transaction_manager: TransactionManager,
    ):
        """
        Initialize with dependencies (Dependency Inversion Principle).

        Args:
            fish_repository: Implementation of DataRepository interface
            validation_service: Implementation of ValidationService interface
            transaction_manager: Implementation of TransactionManager interface
        """
        self._fish_repository = fish_repository
        self._validation_service = validation_service
        self._transaction_manager = transaction_manager
        self._fish_stock: dict[str, int] = {}

    def add_fish(self, fish_type: str, quantity: int) -> None:
        """
        Add fish to the stock with comprehensive validation and transaction support.

        This method validates the fish type against the repository, ensures the quantity
        is valid using the validation service, and performs the addition within a
        transaction context to ensure ACID properties are maintained.

        Args:
            fish_type (str): Type of fish to add. Must exist in the fish repository.
                           Lookup is case-insensitive for user convenience.
            quantity (int): Number of fish to add. Must be positive integer.

        Raises:
            ValueError: If fish type is unknown in the repository, or if quantity
                       validation fails (not positive, exceeds maximum allowed).
            RuntimeError: If transaction fails or cannot be completed.

        Note:
            - Operation is atomic: either completes fully or makes no changes
            - Fish type validation includes repository existence check
            - Quantity validation includes range checking (positive, under maximum)
            - Current state is saved for rollback before any changes
            - If fish type already exists in stock, quantities are summed

        Example:
            >>> manager.add_fish("goldfish", 5)
            >>> manager.add_fish("KOI", 2)  # Case-insensitive
        """

        def _add_operation():
            # Validate inputs
            quantity_errors = self._validation_service.validate_fish_quantity(quantity)
            if quantity_errors:
                raise ValueError(f"Invalid quantity: {'; '.join(quantity_errors)}")

            fish_key = fish_type.lower()
            if not self._fish_repository.fish_exists(fish_key):
                raise ValueError(f"Unknown fish type: {fish_type}")

            # Save current state for potential rollback
            self._transaction_manager.save_state("fish_stock", self._fish_stock)

            # Perform operation
            self._fish_stock[fish_key] = self._fish_stock.get(fish_key, 0) + quantity

        self._transaction_manager.execute_transaction(_add_operation)

    def remove_fish(self, fish_type: str, quantity: int) -> None:
        """
        Remove fish from the stock with validation and transaction support.

        This method safely removes fish from the stock while maintaining data
        integrity. If the removal would create negative stock, the fish type
        is removed entirely. Operations are performed within transaction context.

        Args:
            fish_type (str): Type of fish to remove. Case-insensitive lookup.
            quantity (int): Number of fish to remove. Must be positive integer.

        Raises:
            ValueError: If quantity validation fails (not positive, exceeds maximum).
            RuntimeError: If transaction fails or cannot be completed.

        Note:
            - Operation is atomic: either completes fully or makes no changes
            - If fish type doesn't exist in stock, operation succeeds silently
            - If quantity exceeds current stock, all fish of that type are removed
            - Fish type entry is deleted from stock when quantity reaches zero
            - Current state is saved for rollback before any changes
            - No error if attempting to remove non-existent fish type

        Example:
            >>> manager.remove_fish("goldfish", 2)
            >>> manager.remove_fish("koi", 100)  # Removes all if < 100 in stock
        """

        def _remove_operation():
            # Validate inputs
            quantity_errors = self._validation_service.validate_fish_quantity(quantity)
            if quantity_errors:
                raise ValueError(f"Invalid quantity: {'; '.join(quantity_errors)}")

            fish_key = fish_type.lower()
            if fish_key not in self._fish_stock:
                return  # Nothing to remove

            # Save current state for potential rollback
            self._transaction_manager.save_state("fish_stock", self._fish_stock)

            # Perform operation
            new_quantity = max(0, self._fish_stock[fish_key] - quantity)
            if new_quantity == 0:
                del self._fish_stock[fish_key]
            else:
                self._fish_stock[fish_key] = new_quantity

        self._transaction_manager.execute_transaction(_remove_operation)

    def bulk_add_fish(self, fish_additions: dict[str, int]) -> None:
        """
        Add multiple fish types in a single transaction ensuring Atomicity.

        This method validates all fish types and quantities before making any changes,
        ensuring that either all fish are added successfully or no changes are made.
        This demonstrates ACID transaction properties in practice.

        Args:
            fish_additions (Dict[str, int]): Dictionary mapping fish types to quantities.
                                           All fish types must exist in repository and
                                           all quantities must be positive integers.

        Raises:
            ValueError: If any fish type is unknown, any quantity is invalid, or if
                       the input data structure is malformed.
            RuntimeError: If transaction fails or cannot be completed.

        Note:
            - Operation follows "fail fast" principle: all validation before any changes
            - Completely atomic: either all fish added or none added
            - Validates entire input structure before starting transaction
            - Checks existence of all fish types in repository
            - Validates all quantities using validation service
            - Current state saved for rollback before any modifications
            - More efficient than multiple individual add_fish calls

        Example:
            >>> batch = {
            ...     "goldfish": 10,
            ...     "koi": 3,
            ...     "shubunkin": 5
            ... }
            >>> manager.bulk_add_fish(batch)
        """

        def _bulk_add_operation():
            # Validate all data first (fail fast)
            stock_errors = self._validation_service.validate_fish_stock_data(
                fish_additions
            )
            if stock_errors:
                raise ValueError(f"Invalid fish stock data: {'; '.join(stock_errors)}")

            # Check all fish types exist
            for fish_type in fish_additions.keys():
                if not self._fish_repository.fish_exists(fish_type.lower()):
                    raise ValueError(f"Unknown fish type: {fish_type}")

            # Save current state
            self._transaction_manager.save_state("fish_stock", self._fish_stock)

            # Perform all additions
            for fish_type, quantity in fish_additions.items():
                fish_key = fish_type.lower()
                self._fish_stock[fish_key] = (
                    self._fish_stock.get(fish_key, 0) + quantity
                )

        self._transaction_manager.execute_transaction(_bulk_add_operation)

    def get_stock(self) -> dict[str, int]:
        """
        Get a defensive copy of the current fish stock.

        This method returns a copy of the internal fish stock to prevent external
        modification of the manager's internal state, following encapsulation principles.

        Returns:
            Dict[str, int]: Copy of current fish stock mapping fish type keys to quantities.
                          Returns empty dictionary if no fish are stocked.

        Note:
            - Returns defensive copy to maintain encapsulation
            - Fish type keys are lowercase internal identifiers
            - Quantities reflect current stock levels after all operations
            - Safe to modify returned dictionary without affecting internal state
            - Use fish repository to get display names and other fish information

        Example:
            >>> stock = manager.get_stock()
            >>> print(f"Current stock: {stock}")
            >>> stock["goldfish"] = 999  # Safe: doesn't affect manager's internal state
        """
        return self._fish_stock.copy()

    def clear_stock(self) -> None:
        """
        Clear all fish from the stock inventory.

        This method removes all fish from the stock, resetting the inventory to
        empty state. Operation is immediate and does not use transaction context.

        Note:
            - Irreversible operation: all stock data is lost
            - Does not use transaction context (immediate effect)
            - Useful for resetting stock or starting fresh calculations
            - No validation required as operation cannot fail

        Example:
            >>> manager.clear_stock()
            >>> assert manager.get_stock_count() == 0
        """
        self._fish_stock.clear()

    def get_stock_count(self) -> int:
        """
        Get the total number of individual fish across all types in the stock.

        This method sums the quantities of all fish types to provide the total
        number of individual fish currently in the stock inventory.

        Returns:
            int: Total number of individual fish across all species in stock.
                Returns 0 if no fish are currently stocked.

        Note:
            - Counts individual fish, not fish types
            - Useful for capacity and bioload calculations
            - Result reflects current state after all add/remove operations

        Example:
            >>> # Stock contains 5 goldfish and 3 koi
            >>> total = manager.get_stock_count()
            >>> print(f"Total fish: {total}")  # Outputs: 8
        """
        return sum(self._fish_stock.values())

    def has_fish(self, fish_type: str) -> bool:
        """
        Check if a specific fish type is currently present in the stock.

        This method checks whether the specified fish type has any quantity
        in the current stock inventory.

        Args:
            fish_type (str): The fish type to check for. Case-insensitive lookup.

        Returns:
            bool: True if the fish type exists in stock with quantity > 0,
                 False if not present or quantity is 0.

        Note:
            - Fish type lookup is case-insensitive
            - Returns False for fish types with 0 quantity (should not happen due to cleanup)
            - Useful for conditional operations and stock validation

        Example:
            >>> if manager.has_fish("goldfish"):
            ...     print("Goldfish are in stock")
            >>> else:
            ...     print("No goldfish currently stocked")
        """
        return fish_type.lower() in self._fish_stock
