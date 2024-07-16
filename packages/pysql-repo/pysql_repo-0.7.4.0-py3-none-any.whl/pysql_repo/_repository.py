# MODULES
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    Sequence,
)

# CONTEXTLIB
from contextlib import AbstractContextManager

# SQLALCHEMY
from sqlalchemy import ColumnExpressionArgument, Select, update
from sqlalchemy.orm import DeclarativeBase, Session, InstrumentedAttribute, Session

# DECORATORS
from pysql_repo._decorators import check_values as _check_values

# UTILS
from pysql_repo._utils import (
    FilterType,
    RelationshipOption,
    build_delete_stmt as _build_delete_stmt,
    build_insert_stmt as _build_insert_stmt,
    build_select_stmt as _build_select_stmt,
    build_update_stmt as _build_update_stmt,
    select_distinct as _select_distinct,
    apply_pagination as _apply_pagination,
)


_T = TypeVar("_T", bound=DeclarativeBase)


class Repository:
    """
    Represents a repository for database operations.

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
        session_factory: Callable[..., AbstractContextManager[Session]],
    ) -> None:
        """
        Initializes the Repository.

        Args:
            session_factory: A callable that returns a context manager
                             for creating and managing database sessions.

        Returns:
            None
        """
        self._session_factory = session_factory

    def session_manager(self) -> AbstractContextManager[Session]:
        """
        Get a session manager.

        Returns:
            AbstractContextManager[Session]: An context manager for managing database sessions.
        """
        return self._session_factory()

    def _select(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        distinct: Optional[ColumnExpressionArgument[Any]] = None,
        filters: Optional[FilterType] = None,
        optional_filters: Optional[FilterType] = None,
        relationship_options: Optional[
            Dict[InstrumentedAttribute[Any], RelationshipOption]
        ] = None,
    ) -> Optional[_T]:
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
            The selected object or None if not found.
        """
        stmt = _select_distinct(
            model=model,
            expr=distinct,
        )

        return self._select_stmt(
            __session__,
            stmt=stmt,
            filters=filters,
            optional_filters=optional_filters,
            relationship_options=relationship_options,
        )

    def _select_stmt(
        self,
        __session__: Session,
        /,
        stmt: Select[Tuple[_T]],
        filters: Optional[FilterType] = None,
        optional_filters: Optional[FilterType] = None,
        relationship_options: Optional[
            Dict[InstrumentedAttribute[Any], RelationshipOption]
        ] = None,
        group_by: Optional[ColumnExpressionArgument[Any]] = None,
    ) -> Optional[_T]:
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

        return __session__.execute(stmt).unique().scalar_one_or_none()

    def _select_all(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        distinct: Optional[ColumnExpressionArgument[Any]] = None,
        filters: Optional[FilterType] = None,
        optional_filters: Optional[FilterType] = None,
        relationship_options: Optional[
            Dict[InstrumentedAttribute[Any], RelationshipOption]
        ] = None,
        order_by: Optional[Union[List[str], str]] = None,
        direction: Optional[Union[List[str], str]] = None,
        limit: Optional[int] = None,
    ) -> Sequence[_T]:
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

        return self._select_all_stmt(
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

    def _select_all_stmt(
        self,
        __session__: Session,
        /,
        stmt: Select[Tuple[_T]],
        model: Type[_T],
        filters: Optional[FilterType] = None,
        optional_filters: Optional[FilterType] = None,
        relationship_options: Optional[
            Dict[InstrumentedAttribute[Any], RelationshipOption]
        ] = None,
        group_by: Optional[ColumnExpressionArgument[Any]] = None,
        order_by: Optional[Union[List[str], str]] = None,
        direction: Optional[Union[List[str], str]] = None,
        limit: Optional[int] = None,
    ) -> Sequence[_T]:
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

        return __session__.execute(stmt).unique().scalars().all()

    def _select_paginate(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        page: int,
        per_page: int,
        distinct: Optional[ColumnExpressionArgument[Any]] = None,
        filters: Optional[FilterType] = None,
        optional_filters: Optional[FilterType] = None,
        relationship_options: Optional[
            Dict[InstrumentedAttribute[Any], RelationshipOption]
        ] = None,
        order_by: Optional[Union[List[str], str]] = None,
        direction: Optional[Union[List[str], str]] = None,
        limit: Optional[int] = None,
    ) -> Tuple[Sequence[_T], str]:
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

        return self._select_paginate_stmt(
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

    def _select_paginate_stmt(
        self,
        __session__: Session,
        /,
        stmt: Select[Tuple[_T]],
        model: Type[_T],
        page: int,
        per_page: int,
        filters: Optional[FilterType] = None,
        optional_filters: Optional[FilterType] = None,
        relationship_options: Optional[
            Dict[InstrumentedAttribute[Any], RelationshipOption]
        ] = None,
        group_by: Optional[ColumnExpressionArgument[Any]] = None,
        order_by: Optional[Union[List[str], str]] = None,
        direction: Optional[Union[List[str], str]] = None,
        limit: Optional[int] = None,
    ) -> Tuple[Sequence[_T], str]:
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

        stmt, pagination = _apply_pagination(
            __session__,
            stmt=stmt,
            page=page,
            per_page=per_page,
        )

        return __session__.execute(stmt).unique().scalars().all(), pagination

    @_check_values(as_list=True)
    def _bulk_update(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        values: List[Dict[str, Any]],
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
        __session__.execute(update(model), values)

        if flush:
            __session__.flush()
        if commit:
            __session__.commit()

    @_check_values(as_list=False)
    def _update_all(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        values: Dict[str, Any],
        filters: Optional[FilterType] = None,
        flush: bool = False,
        commit: bool = False,
    ) -> Sequence[_T]:
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

        sequence = __session__.execute(stmt).unique().scalars().all()

        if flush:
            __session__.flush()
        if commit:
            __session__.commit()

        for item in sequence:
            __session__.refresh(item)

        return sequence

    @_check_values(as_list=False)
    def _update(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        values: Dict[str, Any],
        filters: Optional[FilterType] = None,
        flush: bool = False,
        commit: bool = False,
    ) -> Optional[_T]:
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

        item = __session__.execute(stmt).unique().scalar_one_or_none()

        if item is None:
            return None

        if flush:
            __session__.flush()
        if commit:
            __session__.commit()

        __session__.refresh(item)

        return item

    @_check_values(as_list=True)
    def _add_all(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        values: List[Dict[str, Any]],
        flush: bool = False,
        commit: bool = False,
    ) -> Sequence[_T]:
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

        sequence = __session__.execute(stmt, values).unique().scalars().all()

        if flush:
            __session__.flush()
        if commit:
            __session__.commit()

        if flush or commit:
            for item in sequence:
                __session__.refresh(item)

        return sequence

    @_check_values(as_list=False)
    def _add(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        values: Dict[str, Any],
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

        item = __session__.execute(stmt, values).unique().scalar_one()

        if flush:
            __session__.flush()
        if commit:
            __session__.commit()

        if flush or commit:
            __session__.refresh(item)

        return item

    def _delete_all(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        filters: FilterType,
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

        sequence = __session__.execute(stmt).unique().scalars().all()

        if len(sequence) == 0:
            return False

        if flush:
            __session__.flush()
        if commit:
            __session__.commit()

        return True

    def _delete(
        self,
        __session__: Session,
        /,
        model: Type[_T],
        filters: FilterType,
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

        item = __session__.execute(stmt).unique().scalar_one_or_none()

        if item is None:
            return False

        if flush:
            __session__.flush()
        if commit:
            __session__.commit()

        return True
