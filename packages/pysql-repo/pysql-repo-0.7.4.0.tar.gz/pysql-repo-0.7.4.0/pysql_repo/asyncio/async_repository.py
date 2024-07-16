# MODULES
from typing import (
    Any as _Any,
    Callable as _Callable,
    Dict as _Dict,
    List as _List,
    Optional as _Optional,
    Tuple as _Tuple,
    Type as _Type,
    TypeVar as _TypeVar,
    Union as _Union,
    Sequence as _Sequence,
)

# CONTEXTLIB
from contextlib import AbstractAsyncContextManager as _AbstractAsyncContextManager

# SQLALCHEMY
from sqlalchemy import (
    ColumnExpressionArgument as _ColumnExpressionArgument,
    Select as _Select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase as _DeclarativeBase,
    InstrumentedAttribute as _InstrumentedAttribute,
)

# DECORATORS
from pysql_repo._decorators import check_values as _check_values

# UTILS
from pysql_repo._utils import (
    FilterType as _FilterType,
    RelationshipOption as _RelationshipOption,
    async_apply_pagination as _async_apply_pagination,
    build_delete_stmt as _build_delete_stmt,
    build_insert_stmt as _build_insert_stmt,
    build_select_stmt as _build_select_stmt,
    build_update_stmt as _build_update_stmt,
    select_distinct as _select_distinct,
)


_T = _TypeVar("_T", bound=_DeclarativeBase)


class AsyncRepository:
    """
    Represents an asynchronous repository for database operations.

    Attributes:
        _session_factory: The session factory used for creating sessions.

    Methods:
        session_manager: Returns the session factory.
        _select: Selects a single row from the database.
        _select_stmt: Selects a single row from the database using a custom statement.
        _select_all: Selects all rows from the database.
        _select_all_stmt: Selects all rows from the database using a custom statement.
        _select_paginate: Selects a paginated set of rows from the database.
        _select_paginate_stmt: Selects a paginated set of rows from the database using a custom statement.
    """

    def __init__(
        self,
        session_factory: _Callable[..., _AbstractAsyncContextManager[_AsyncSession]],
    ) -> None:
        """
        Initializes the AsyncRepository.

        Args:
            session_factory: A callable that returns an asynchronous context manager
                             for creating and managing database sessions.

        Returns:
            None
        """
        self._session_factory = session_factory

    def session_manager(self) -> _AbstractAsyncContextManager[_AsyncSession]:
        """
        Get a session manager.

        Returns:
            AbstractAsyncContextManager[AsyncSession]: An asynchronous context manager for managing database sessions.
        """
        return self._session_factory()

    async def _select(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        distinct: _Optional[_ColumnExpressionArgument[_Any]] = None,
        filters: _Optional[_FilterType] = None,
        optional_filters: _Optional[_FilterType] = None,
        relationship_options: _Optional[
            _Dict[_InstrumentedAttribute[_Any], _RelationshipOption]
        ] = None,
    ) -> _Optional[_T]:
        """
        Selects a single object from the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            distinct: The distinct column expression.
            filters: The filters to apply.
            optional_filters: The optional filters to apply.
            relationship_options: The relationship options.

        Returns:
            The selected row.

        """
        stmt = _select_distinct(
            model=model,
            expr=distinct,
        )

        return await self._select_stmt(
            __session__,
            stmt=stmt,
            filters=filters,
            optional_filters=optional_filters,
            relationship_options=relationship_options,
        )

    async def _select_stmt(
        self,
        __session__: _AsyncSession,
        /,
        stmt: _Select[_Tuple[_T]],
        filters: _Optional[_FilterType] = None,
        optional_filters: _Optional[_FilterType] = None,
        relationship_options: _Optional[
            _Dict[_InstrumentedAttribute[_Any], _RelationshipOption]
        ] = None,
        group_by: _Optional[_ColumnExpressionArgument[_Any]] = None,
    ) -> _Optional[_T]:
        """
        Selects a single object from the database using a custom statement.

        Args:
            __session__: The session to use.
            stmt: The custom select statement.
            filters: The filters to apply.
            optional_filters: The optional filters to apply.
            relationship_options: The relationship options.
            group_by: The column expression to group by.

        Returns:
            The selected object or None if not found.

        """
        stmt = _build_select_stmt(
            stmt=stmt,
            filters=filters,
            optional_filters=optional_filters,
            relationship_options=relationship_options,
            group_by=group_by,
        )

        result = await __session__.execute(stmt)

        return result.unique().scalar_one_or_none()

    async def _select_all(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        distinct: _Optional[_ColumnExpressionArgument[_Any]] = None,
        filters: _Optional[_FilterType] = None,
        optional_filters: _Optional[_FilterType] = None,
        relationship_options: _Optional[
            _Dict[_InstrumentedAttribute[_Any], _RelationshipOption]
        ] = None,
        order_by: _Optional[_Union[_List[str], str]] = None,
        direction: _Optional[_Union[_List[str], str]] = None,
        limit: _Optional[int] = None,
    ) -> _Sequence[_T]:
        """
        Selects all objects from the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            distinct: The distinct column expressions.
            filters: The filters to apply.
            optional_filters: The optional filters to apply.
            relationship_options: The relationship options.
            order_by: The column(s) to order by.
            direction: The direction of the ordering.
            limit: The maximum number of objects to return.

        Returns:
            A sequence of selected objects.

        """
        stmt = _select_distinct(
            model=model,
            expr=distinct,
        )

        return await self._select_all_stmt(
            __session__,
            stmt=stmt,
            model=model,
            filters=filters,
            optional_filters=optional_filters,
            relationship_options=relationship_options,
            order_by=order_by,
            direction=direction,
            limit=limit,
        )

    async def _select_all_stmt(
        self,
        __session__: _AsyncSession,
        /,
        stmt: _Select[_Tuple[_T]],
        model: _Type[_T],
        filters: _Optional[_FilterType] = None,
        optional_filters: _Optional[_FilterType] = None,
        relationship_options: _Optional[
            _Dict[_InstrumentedAttribute[_Any], _RelationshipOption]
        ] = None,
        group_by: _Optional[_ColumnExpressionArgument[_Any]] = None,
        order_by: _Optional[_Union[_List[str], str]] = None,
        direction: _Optional[_Union[_List[str], str]] = None,
        limit: _Optional[int] = None,
    ) -> _Sequence[_T]:
        """
        Selects all objects from the database using a custom statement.

        Args:
            __session__: The session to use.
            stmt: The custom select statement.
            model: The model class representing the table.
            filters: The filters to apply.
            optional_filters: The optional filters to apply.
            relationship_options: The relationship options.
            group_by: The column expression to group by.
            order_by: The column(s) to order by.
            direction: The direction of the ordering.
            limit: The maximum number of rows to return.

        Returns:
            A sequence of selected objects.

        """
        stmt = _build_select_stmt(
            stmt=stmt,
            model=model,
            filters=filters,
            optional_filters=optional_filters,
            relationship_options=relationship_options,
            group_by=group_by,
            order_by=order_by,
            direction=direction,
            limit=limit,
        )

        result = await __session__.execute(stmt)

        return result.unique().scalars().all()

    async def _select_paginate(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        page: int,
        per_page: int,
        distinct: _Optional[_ColumnExpressionArgument[_Any]] = None,
        filters: _Optional[_FilterType] = None,
        optional_filters: _Optional[_FilterType] = None,
        relationship_options: _Optional[
            _Dict[_InstrumentedAttribute[_Any], _RelationshipOption]
        ] = None,
        order_by: _Optional[_Union[_List[str], str]] = None,
        direction: _Optional[_Union[_List[str], str]] = None,
        limit: _Optional[int] = None,
    ) -> _Tuple[_Sequence[_T], str]:
        """
        Selects a paginated set of objects from the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            page: The page number.
            per_page: The number of items per page.
            distinct: The distinct column expression.
            filters: The filters to apply.
            optional_filters: The optional filters to apply.
            relationship_options: The relationship options.
            order_by: The column(s) to order by.
            direction: The direction of the ordering.
            limit: The maximum number of objects to return.

        Returns:
            A tuple containing the selected objects and pagination information.

        """
        stmt = _select_distinct(
            model=model,
            expr=distinct,
        )

        return await self._select_paginate_stmt(
            __session__,
            stmt=stmt,
            model=model,
            page=page,
            per_page=per_page,
            filters=filters,
            optional_filters=optional_filters,
            relationship_options=relationship_options,
            order_by=order_by,
            direction=direction,
            limit=limit,
        )

    async def _select_paginate_stmt(
        self,
        __session__: _AsyncSession,
        /,
        stmt: _Select[_Tuple[_T]],
        model: _Type[_T],
        page: int,
        per_page: int,
        filters: _Optional[_FilterType] = None,
        optional_filters: _Optional[_FilterType] = None,
        relationship_options: _Optional[
            _Dict[_InstrumentedAttribute[_Any], _RelationshipOption]
        ] = None,
        group_by: _Optional[_ColumnExpressionArgument[_Any]] = None,
        order_by: _Optional[_Union[_List[str], str]] = None,
        direction: _Optional[_Union[_List[str], str]] = None,
        limit: _Optional[int] = None,
    ) -> _Tuple[_Sequence[_T], str]:
        """
        Selects a paginated set of rows from the database using a custom statement.

        Args:
            __session__: The session to use.
            stmt: The custom select statement.
            model: The model class representing the table.
            page: The page number.
            per_page: The number of items per page.
            filters: The filters to apply.
            optional_filters: The optional filters to apply.
            relationship_options: The relationship options.
            group_by: The column expression to group by.
            order_by: The column(s) to order by.
            direction: The direction of the ordering.
            limit: The maximum number of rows to return.

        Returns:
            A tuple containing the selected objects and pagination information.

        """
        stmt = _build_select_stmt(
            stmt=stmt,
            model=model,
            filters=filters,
            optional_filters=optional_filters,
            relationship_options=relationship_options,
            group_by=group_by,
            order_by=order_by,
            direction=direction,
            limit=limit,
        )

        stmt, pagination = await _async_apply_pagination(
            __session__,
            stmt=stmt,
            page=page,
            per_page=per_page,
        )

        result = await __session__.execute(stmt)

        return result.unique().scalars().all(), pagination

    @_check_values(as_list=True)
    async def _bulk_update(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        values: _List[_Dict[str, _Any]],
        flush: bool = False,
        commit: bool = False,
    ) -> None:
        """
        Updates multiple objects in the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            values: A list of dictionaries containing column-value pairs for each object.
            flush: Whether to flush the session after the update.
            commit: Whether to commit the session after the update.

        """
        await __session__.execute(update(model), values)

        if flush:
            await __session__.flush()
        if commit:
            await __session__.commit()

    @_check_values(as_list=False)
    async def _update_all(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        values: _Dict[str, _Any],
        filters: _Optional[_FilterType] = None,
        flush: bool = False,
        commit: bool = False,
    ) -> _Sequence[_T]:
        """
        Updates multiple objects in the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            values: A dictionary of column-value pairs to update.
            filters: The filters to apply.
            flush: Whether to flush the session after the update.
            commit: Whether to commit the session after the update.

        Returns:
            A sequence of updated objects.
        """
        stmt = _build_update_stmt(
            model=model,
            values=values,
            filters=filters,
        )

        result = await __session__.execute(stmt)

        sequence = result.unique().scalars().all()

        if flush:
            await __session__.flush()
        if commit:
            await __session__.commit()

        for item in sequence:
            await __session__.refresh(item)

        return sequence

    @_check_values(as_list=False)
    async def _update(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        values: _Dict[str, _Any],
        filters: _Optional[_FilterType] = None,
        flush: bool = False,
        commit: bool = False,
    ) -> _Optional[_T]:
        """
        Updates a single object in the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            values: A dictionary of column-value pairs to update.
            filters: The filters to apply.
            flush: Whether to flush the session after the update.
            commit: Whether to commit the session after the update.

        Returns:
            The updated object or None if not found.
        """
        stmt = _build_update_stmt(
            model=model,
            values=values,
            filters=filters,
        )

        result = await __session__.execute(stmt)

        item = result.unique().scalar_one_or_none()

        if item is None:
            return None

        if flush:
            await __session__.flush()
        if commit:
            await __session__.commit()

        await __session__.refresh(item)

        return item

    @_check_values(as_list=True)
    async def _add_all(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        values: _List[_Dict[str, _Any]],
        flush: bool = False,
        commit: bool = False,
    ) -> _Sequence[_T]:
        """
        Adds multiple objects to the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            values: A list of dictionaries containing column-value pairs for each object.
            flush: Whether to flush the session after adding the objects.
            commit: Whether to commit the session after adding the objects.

        Returns:
            A sequence of added objects.
        """
        stmt = _build_insert_stmt(model=model)

        result = await __session__.execute(stmt, values)

        sequence = result.unique().scalars().all()

        if flush:
            await __session__.flush()
        if commit:
            await __session__.commit()

        if flush or commit:
            for item in sequence:
                await __session__.refresh(item)

        return sequence

    @_check_values(as_list=False)
    async def _add(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        values: _Dict[str, _Any],
        flush: bool = False,
        commit: bool = False,
    ) -> _T:
        """
        Adds a single object to the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            values: A dictionary of column-value pairs for the object.
            flush: Whether to flush the session after adding the object.
            commit: Whether to commit the session after adding the object.

        Returns:
            The added object.

        """
        stmt = _build_insert_stmt(model=model)

        result = await __session__.execute(stmt, values)

        item = result.unique().scalar_one()

        if flush:
            await __session__.flush()
        if commit:
            await __session__.commit()

        if flush or commit:
            await __session__.refresh(item)

        return item

    async def _delete_all(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        filters: _FilterType,
        flush: bool = True,
        commit: bool = False,
    ) -> bool:
        """
        Deletes multiple objects from the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            filters: The filters to apply.
            flush: Whether to flush the session after the deletion.
            commit: Whether to commit the session after the deletion.

        Returns:
            True if any objects were deleted, False otherwise.
        """
        stmt = _build_delete_stmt(
            model=model,
            filters=filters,
        )

        result = await __session__.execute(stmt)

        sequence = result.unique().scalars().all()

        if len(sequence) == 0:
            return False

        if flush:
            await __session__.flush()
        if commit:
            await __session__.commit()

        return True

    async def _delete(
        self,
        __session__: _AsyncSession,
        /,
        model: _Type[_T],
        filters: _FilterType,
        flush: bool = True,
        commit: bool = False,
    ) -> bool:
        """
        Deletes a single object from the database.

        Args:
            __session__: The session to use.
            model: The model class representing the table.
            filters: The filters to apply.
            flush: Whether to flush the session after the deletion.
            commit: Whether to commit the session after the deletion.

        Returns:
            True if the object was deleted, False otherwise.
        """
        stmt = _build_delete_stmt(
            model=model,
            filters=filters,
        )

        result = await __session__.execute(stmt)

        item = result.unique().scalar_one_or_none()

        if item is None:
            return False

        if flush:
            await __session__.flush()
        if commit:
            await __session__.commit()

        return True
