# MODULES
from typing import TypeVar as _TypeVar, Generic as _Generic

# CONTEXTLIB
from contextlib import AbstractAsyncContextManager as _AbstractAsyncContextManager

# SQLALCHEMY
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession

# MODELS
from pysql_repo.asyncio.async_repository import AsyncRepository as _AsyncRepository


_T = _TypeVar("_T", bound=_AsyncRepository)


class AsyncService(_Generic[_T]):
    """
    Represents a generic asynchronous service.

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
        Initializes the AsyncService.

        Args:
            repository: The repository object.
        """
        self._repository = repository

    def session_manager(self) -> _AbstractAsyncContextManager[_AsyncSession]:
        """
        Returns the session manager from the repository.

        Returns:
            A session manager.
        """
        return self._repository.session_manager()
