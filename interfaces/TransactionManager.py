from abc import ABC, abstractmethod
from typing import Callable, TypeVar

T = TypeVar('T')


class TransactionManager(ABC):
    """
    Abstract interface for transaction management following ACID principles.
    Ensures Atomicity, Consistency, Isolation, and Durability of operations.
    """

    @abstractmethod
    def execute_transaction(self, operation: Callable[[], T]) -> T:
        """
        Execute an operation within a transaction context.
        Ensures ACID properties are maintained.
        """

    @abstractmethod
    def begin_transaction(self) -> None:
        """Begin a new transaction."""

    @abstractmethod
    def commit_transaction(self) -> None:
        """Commit the current transaction."""

    @abstractmethod
    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""

    @abstractmethod
    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction."""
