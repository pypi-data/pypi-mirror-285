# MODULES
from typing import TypeVar, Generic

# CONTEXTLIB
from contextlib import AbstractContextManager

# SQLALCHEMY
from sqlalchemy.orm import Session

# MODELS
from pysql_repo._repository import Repository


_T = TypeVar("_T", bound=Repository)


class Service(Generic[_T]):
    """
    Represents a generic service class.

    Attributes:
        _repository: The repository object.

    Methods:
        session_manager: Returns the session factory.
    """

    def __init__(
        self,
        repository: _T,
    ) -> None:
        """
        Initializes the Service.

        Args:
            repository: The repository object.
        """

        self._repository = repository

    def session_manager(self) -> AbstractContextManager[Session]:
        """
        Returns the session manager from the repository.

        Returns:
            A session manager.
        """
        return self._repository.session_manager()
