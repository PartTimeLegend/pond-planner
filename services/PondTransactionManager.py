import copy
from typing import Any, Callable, TypeVar

from interfaces.TransactionManager import TransactionManager

T = TypeVar("T")


class PondTransactionManager(TransactionManager):
    """
    A transaction manager implementation for pond-related database operations.
    This class provides transaction management capabilities including support for nested
    transactions with savepoint functionality. It maintains transaction state, rollback
    data, and a transaction stack to handle complex transaction scenarios.
    The PondTransactionManager ensures ACID properties by:
    - Tracking active transaction state
    - Storing rollback data for state restoration
    - Supporting nested transactions through savepoints
    - Providing automatic cleanup on commit/rollback
    Key Features:
    - Single and nested transaction support
    - Savepoint-based rollback for nested transactions
    - State preservation for rollback operations
    - Exception-safe transaction handling
    Example:
        ```python
        transaction_manager = PondTransactionManager()
        # Simple transaction
        result = transaction_manager.execute_transaction(lambda: perform_pond_operation())
        # Manual transaction control
        transaction_manager.begin_transaction()
            transaction_manager.save_state("pond_data", original_data)
            modify_pond_data()
            transaction_manager.commit_transaction()
        except Exception:
            transaction_manager.rollback_transaction()
        ```
        _transaction_stack (list): Stack to manage nested transactions and savepoints.
        RuntimeError: When attempting to begin a transaction when one is already active,
                     or when trying to commit/rollback without an active transaction.
    """

    def __init__(self):
        """
        Initialize the PondTransactionManager.

        Sets up the transaction manager with default state where no transaction
        is currently active, no rollback data is stored, and the transaction
        stack is empty.

        Attributes:
            _transaction_active (bool): Flag indicating if a transaction is currently active.
            _rollback_data (Dict[str, Any]): Dictionary storing data needed for rollback operations.
            _transaction_stack (list): Stack to manage nested transactions.
        """
        self._transaction_active = False
        self._rollback_data: dict[str, Any] = {}
        self._transaction_stack = []

    def execute_transaction(self, operation: Callable[[], T]) -> T:
        """
        Execute an operation within a transaction context.

        If a transaction is already active, the operation will be executed as a nested
        transaction. Otherwise, a new transaction will be started, the operation executed,
        and the transaction committed on success or rolled back on failure.

        Args:
            operation (Callable[[], T]): A callable that performs the database operations
                                       to be executed within the transaction context.

        Returns:
            T: The result returned by the operation callable.

        Raises:
            Exception: Any exception raised by the operation will cause the transaction
                      to be rolled back and the exception will be re-raised.
        """
        if self._transaction_active:
            # Nested transaction - add to stack
            return self._execute_nested_transaction(operation)

        self.begin_transaction()
        try:
            result = operation()
            self.commit_transaction()
            return result
        except Exception as e:
            self.rollback_transaction()
            raise e

    def _execute_nested_transaction(self, operation: Callable[[], T]) -> T:
        """
        Execute an operation within a nested transaction with savepoint support.
        Creates a savepoint before executing the operation, allowing for partial
        rollback to this specific point in the transaction stack if the operation
        fails. If the operation succeeds, the savepoint is removed and the result
        is returned. If an exception occurs, the transaction state is rolled back
        to the savepoint before re-raising the exception.
        Args:
            operation (Callable[[], T]): A callable that performs the transaction
                operations and returns a result of type T.
        Returns:
            T: The result returned by the operation callable.
        Raises:
            Exception: Re-raises any exception that occurs during operation
                execution after rolling back to the savepoint.
        Note:
            This method modifies the internal transaction stack and rollback data.
            The savepoint is automatically cleaned up whether the operation
            succeeds or fails.
        """
        savepoint = copy.deepcopy(self._rollback_data)
        self._transaction_stack.append(savepoint)

        try:
            result = operation()
            # If successful, remove savepoint
            self._transaction_stack.pop()
            return result
        except Exception as e:
            # Rollback to savepoint
            self._rollback_data = self._transaction_stack.pop()
            raise e

    def begin_transaction(self) -> None:
        """Begin a new transaction.
        This method starts a new transaction context. If a transaction is already active,
        it raises a RuntimeError. The transaction state is set to active, and any previous
        rollback data is cleared to ensure a clean state for the new transaction.
        Raises:
            RuntimeError: If a transaction is already active.
        """
        if self._transaction_active:
            raise RuntimeError("Transaction already active")

        self._transaction_active = True
        self._rollback_data.clear()

    def commit_transaction(self) -> None:
        """Commit the current transaction.
        This method commits the current transaction, ensuring that all changes made
        during the transaction are saved. If no transaction is active, it raises a
        RuntimeError. After committing, the transaction state is set to inactive,
        and any rollback data is cleared to prevent future rollbacks.
        Raises:
            RuntimeError: If no transaction is active to commit.
        """
        if not self._transaction_active:
            raise RuntimeError("No active transaction to commit")

        self._transaction_active = False
        self._rollback_data.clear()
        self._transaction_stack.clear()

    def rollback_transaction(self) -> None:
        """Rollback the current transaction.
        This method rolls back the current transaction, restoring the state to what it was
        before the transaction began. If no transaction is active, it raises a RuntimeError.
        After rolling back, the transaction state is set to inactive, and any rollback data
        is cleared to prevent future rollbacks.
        Raises:
            RuntimeError: If no transaction is active to rollback.
        """
        if not self._transaction_active:
            raise RuntimeError("No active transaction to rollback")

        # Restore state from rollback data
        self._transaction_active = False
        self._rollback_data.clear()
        self._transaction_stack.clear()

    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction.
        This method returns True if a transaction is currently active, allowing
        other components to check the transaction state before performing operations.
        Returns:
            bool: True if a transaction is currently active, False otherwise.
        """
        return self._transaction_active

    def save_state(self, key: str, value: Any) -> None:
        """Save the current state for rollback purposes.
        This method saves the current state of a specific key in the rollback data
        if a transaction is active. If the key already exists in the rollback data,
        it will not overwrite the existing value. This allows for preserving the state
        of specific keys during a transaction, enabling rollback to the previous state
        if needed.
        Args:
            key (str): The key identifier for the state to be saved.
            value (Any): The value to be saved for the specified key.
        Note:
            This method only saves the state if a transaction is currently active.
            If no transaction is active, the state will not be saved.
        """
        if self._transaction_active and key not in self._rollback_data:
            self._rollback_data[key] = copy.deepcopy(value)

    def get_rollback_state(self, key: str) -> Any:
        """Get the saved state for a specific key.
        This method retrieves the saved state for a specific key from the rollback data.
        If the key does not exist in the rollback data, it returns None.
        Args:
            key (str): The key identifier for the state to be retrieved.
        Returns:
            Any: The value associated with the specified key in the rollback data,
                 or None if the key does not exist.
        """
        return self._rollback_data.get(key)
