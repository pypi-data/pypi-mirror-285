# MODULES
from typing import (
    Any as _Any,
    Callable as _Callable,
    Coroutine as _Coroutine,
    ParamSpec as _ParamSpec,
    TypeVar as _TypeVar,
)

# SQLALCHEMY
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession

_P = _ParamSpec("_P")
_T = _TypeVar("_T")


def with_async_session(
    param_session: str = "session",
) -> _Callable[
    [_Callable[_P, _Coroutine[_Any, _Any, _T]]],
    _Callable[_P, _Coroutine[_Any, _Any, _T]],
]:
    """
    Decorator that provides an async session to the decorated method.
    If the session is not provided as a keyword argument, it creates a new session using the session manager.
    The session is then passed as a keyword argument to the decorated method.

    Args:
        param_session (str, optional): The name of the session parameter. Defaults to "session".

    Raises:
        TypeError: If the decorated object is not an instance of AsyncRepository or AsyncService.
        TypeError: If the session is not an instance of AsyncSession.

    Returns:
        Callable: The decorated method.
    """

    def decorator(
        func: _Callable[_P, _Coroutine[_Any, _Any, _T]]
    ) -> _Callable[_P, _Coroutine[_Any, _Any, _T]]:

        async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            self = kwargs.get("self")
            if not isinstance(self, (AsyncRepository, AsyncService)):
                raise TypeError(
                    f"{self.__class__.__name__} must be instance of {AsyncRepository.__name__} or {AsyncService.__name__}"
                )

            session = kwargs.get(param_session)

            if session is None:
                async with self.session_manager() as session:
                    kwargs[param_session] = session
                    return await func(*args, **kwargs)
            elif not isinstance(session, _AsyncSession):
                raise TypeError(
                    f"{param_session} must be instance of {_AsyncSession.__name__}"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


from pysql_repo.asyncio.async_repository import AsyncRepository
from pysql_repo.asyncio.async_service import AsyncService
