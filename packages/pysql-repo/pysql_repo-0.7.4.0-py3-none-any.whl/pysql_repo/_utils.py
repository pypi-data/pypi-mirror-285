# MODULES
from dataclasses import dataclass, field
import json
from typing import (
    cast,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    TypeAlias,
    Union,
)

# SQLALCHEMY
from sqlalchemy import (
    ColumnExpressionArgument,
    Delete,
    Select,
    UnaryExpression,
    Update,
    and_,
    asc,
    delete,
    desc,
    insert,
    select,
    distinct,
    tuple_,
    func,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    noload,
    lazyload,
    joinedload,
    subqueryload,
    selectinload,
    raiseload,
    contains_eager,
)
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.dml import ReturningDelete, ReturningInsert, ReturningUpdate
from sqlalchemy.sql.elements import Null, BinaryExpression

# Enum
from pysql_repo._constants.enum import LoadingTechnique, Operators

FilterType: TypeAlias = Dict[
    Union[InstrumentedAttribute[Any], Tuple[InstrumentedAttribute[Any], ...]], Any
]

_T = TypeVar("_T", bound=DeclarativeBase)

_T_SELECT_UPDATE = TypeVar("_T_SELECT_UPDATE", bound=Union[Select[Any], Update])

_T_SELECT_UPDATE_DELETE = TypeVar(
    "_T_SELECT_UPDATE_DELETE", bound=Union[Select[Any], Update, Delete]
)


@dataclass
class RelationshipOption:
    """
    Represents options for a relationship between two entities.

    Attributes:
        lazy (LoadingTechnique): The loading technique for the relationship.
        added_criteria (Optional[BinaryExpression]): Additional criteria for the relationship.
        children (Dict[InstrumentedAttribute, "RelationshipOption"]): Child relationships.
    """

    lazy: LoadingTechnique
    added_criteria: Optional[BinaryExpression[Any]] = field(default=None)
    children: Optional[Dict[InstrumentedAttribute[Any], "RelationshipOption"]] = field(
        default=None
    )


def build_select_stmt(
    stmt: Select[Any],
    model: Optional[Type[_T]] = None,
    filters: Optional[FilterType] = None,
    optional_filters: Optional[FilterType] = None,
    relationship_options: Optional[
        Dict[InstrumentedAttribute[Any], RelationshipOption]
    ] = None,
    group_by: Optional[ColumnExpressionArgument[Any]] = None,
    order_by: Optional[Union[List[str], str]] = None,
    direction: Optional[Union[List[str], str]] = None,
    limit: Optional[int] = None,
) -> Select[Tuple[_T]]:
    """
    Builds and returns a select statement with optional filters, group by, order by, and limit clauses.

    Args:
        stmt (Select[Tuple[_T]]): The base SELECT statement.
        model (Optional[Type[_T]]): The model class associated with the SELECT statement.
        filters (Optional[_FilterType]): The filters to apply to the SELECT statement.
        optional_filters (Optional[_FilterType]): The optional filters to apply to the SELECT statement.
        relationship_options (Optional[Dict[InstrumentedAttribute, RelationshipOption]]): The relationship options to apply to the SELECT statement.
        group_by (Optional[ColumnExpressionArgument]): The columns to group the SELECT statement by.
        order_by (Optional[Union[List[str], str]]): The columns to order the SELECT statement by.
        direction (Optional[Union[List[str], str]]): The direction of the ordering.
        limit (int): The maximum number of rows to return.

    Returns:
        Select[Tuple[_T]]: The modified SELECT statement.
    """
    stmt = apply_relationship_options(
        stmt=stmt,
        relationship_options=relationship_options,
    )

    stmt = apply_filters(
        stmt=stmt,
        filter_dict=filters,
    )
    stmt = apply_filters(
        stmt=stmt,
        filter_dict=optional_filters,
        with_optional=True,
    )

    stmt = apply_group_by(
        stmt=stmt,
        group_by=group_by,
    )

    if model is not None:
        stmt = apply_order_by(
            stmt=stmt,
            model=model,
            order_by=order_by,
            direction=direction,
        )

    return apply_limit(
        stmt=stmt,
        limit=limit,
    )


def build_update_stmt(
    model: Type[_T],
    values: Dict[Any, Any],
    filters: Optional[FilterType] = None,
) -> ReturningUpdate[Tuple[_T]]:
    """
    Build and delete an update statement for the given model, values, and filters.

    Args:
        model (Type[_T]): The model class to update.
        values (Dict): A dictionary containing the column-value pairs to update.
        filters (Optional[_FilterType], optional): The filters to apply to the update statement. Defaults to None.

    Returns:
        ReturningUpdate[Tuple[_T]]: The SQL update statement.
    """
    return (
        apply_filters(
            stmt=update(model),
            filter_dict=filters,
        )
        .values(values)
        .returning(model)
    )


def build_insert_stmt(
    model: Type[_T],
) -> ReturningInsert[Tuple[_T]]:
    """
    Build and return an insert statement for the given model.

    Args:
        model (Type[_T]): The model class to build the insert statement for.

    Returns:
        ReturningInsert[Tuple[_T]]: The insert statement with a returning clause.
    """
    return insert(model).returning(model)


def build_delete_stmt(
    model: Type[_T],
    filters: FilterType,
) -> ReturningDelete[Tuple[_T]]:
    """
    Build and return a delete statement for the given model and filters.

    Args:
        model (Type[_T]): The model class to delete from.
        filters (_FilterType): The filters to apply to the delete statement.

    Returns:
        ReturningDelete[Tuple[_T]]: The delete statement with applied filters.
    """
    return apply_filters(
        stmt=delete(model),
        filter_dict=filters,
    ).returning(model)


def select_distinct(
    model: Type[_T],
    expr: Optional[ColumnExpressionArgument[Any]] = None,
) -> Select[Tuple[_T]]:
    """
    Selects distinct values from a column expression.

    Args:
        model: The model type to select from.
        expr: The column expression to select distinct values from.

    Returns:
        A SQLAlchemy Select object that selects distinct values from the given column expression.
        If the column expression is None, it selects all columns from the model.
    """
    return select(distinct(expr)) if expr is not None else select(model)


def apply_group_by(
    stmt: Select[Tuple[_T]],
    group_by: Optional[ColumnExpressionArgument[Any]] = None,
) -> Select[Tuple[_T]]:
    """
    Apply the GROUP BY clause to the given SQL statement.

    Args:
        stmt (Select[Tuple[_T]]): The SQL statement to apply the GROUP BY clause to.
        group_by (ColumnExpressionArgument): The column or expression to group by.

    Returns:
        Select[Tuple[_T]]: The modified SQL statement with the GROUP BY clause applied.
    """
    return stmt.group_by(group_by) if group_by is not None else stmt


def apply_relationship_options(
    stmt: _T_SELECT_UPDATE,
    relationship_options: Optional[
        Dict[InstrumentedAttribute[Any], RelationshipOption]
    ] = None,
    parents: Optional[List[InstrumentedAttribute[Any]]] = None,
) -> _T_SELECT_UPDATE:
    """
    Apply relationship options to a SQLAlchemy statement.

    Args:
        stmt (_T_SELECT_UPDATE): The SQLAlchemy statement to apply the relationship options to.
        relationship_options (Dict[InstrumentedAttribute, RelationshipOption]): A dictionary of relationship options.
        parents (List[InstrumentedAttribute], optional): The list of parent relationships. Defaults to None.

    Returns:
        _T_SELECT_UPDATE: The modified SQLAlchemy statement with the applied relationship options.
    """

    def get_load(
        loading_technique: LoadingTechnique,
        items: List[InstrumentedAttribute[Any]],
        extra_conditions: Optional[BinaryExpression[Any]] = None,
    ) -> _AbstractLoad:
        items_post = []
        for item in items:
            if extra_conditions is not None:
                items_post.append(item.and_(*extra_conditions))
            else:
                items_post.append(item)

        match loading_technique:
            case LoadingTechnique.CONTAINS_EAGER:
                return contains_eager(*items_post)
            case LoadingTechnique.LAZY:
                return lazyload(*items_post)
            case LoadingTechnique.JOINED:
                return joinedload(*items_post)
            case LoadingTechnique.SUBQUERY:
                return subqueryload(*items_post)
            case LoadingTechnique.SELECTIN:
                return selectinload(*items_post)
            case LoadingTechnique.RAISE:
                return raiseload(*items_post)
            case LoadingTechnique.NOLOAD:
                return noload(*items_post)

    if relationship_options is None:
        return stmt

    for relationship, sub_relationships in relationship_options.items():
        if any(
            [
                relationship is None,
                not isinstance(relationship, InstrumentedAttribute),
                sub_relationships is None,
                not isinstance(sub_relationships, RelationshipOption),
            ]
        ):
            continue

        sub_items = [relationship] if parents is None else [*parents, relationship]

        load = get_load(
            loading_technique=sub_relationships.lazy,
            items=sub_items,
            extra_conditions=sub_relationships.added_criteria,
        )

        if load is not None:
            stmt = cast(_T_SELECT_UPDATE, stmt.options(load))

        if (children := sub_relationships.children) is not None:
            stmt = apply_relationship_options(
                stmt,
                relationship_options=children,
                parents=sub_items,
            )

    return stmt


def apply_filters(
    stmt: _T_SELECT_UPDATE_DELETE,
    filter_dict: Optional[FilterType] = None,
    with_optional: bool = False,
) -> _T_SELECT_UPDATE_DELETE:
    """
    Apply filters to the given statement.

    Args:
        stmt (_T_SELECT_UPDATE_DELETE): The statement to apply filters to.
        filter_dict (_FilterType): The dictionary containing the filters.
        with_optional (bool, optional): Whether to include optional filters. Defaults to False.

    Returns:
        _T_SELECT_UPDATE_DELETE: The statement with applied filters.
    """
    filters = get_filters(
        filters=filter_dict,
        with_optional=with_optional,
    )

    return (
        stmt
        if len(filters) == 0
        else cast(_T_SELECT_UPDATE_DELETE, stmt.filter(and_(*filters)))
    )


def apply_order_by(
    stmt: Select[Tuple[_T]],
    model: Type[_T],
    order_by: Optional[Union[List[str], str]] = None,
    direction: Optional[Union[List[str], str]] = None,
) -> Select[Tuple[_T]]:
    """
    Apply order by clause to the given SQLAlchemy select statement.

    Args:
        stmt (Select[Tuple[_T]]): The SQLAlchemy select statement.
        model (Type[_T]): The model class.
        order_by (Union[List[str], str]): The column(s) to order by.
        direction (Union[List[str], str]): The direction(s) of the ordering.

    Returns:
        Select[Tuple[_T]]: The modified SQLAlchemy select statement with order by clause.
    """
    if order_by is None or direction is None:
        return stmt

    if isinstance(order_by, str):
        order_by = [order_by]

    if isinstance(direction, str):
        direction = [direction]

    if len(order_by) != len(direction):
        raise ValueError("order_by length must be equals to direction length")

    order_by_list: List[UnaryExpression[Any]] = []
    for column, dir in zip(order_by, direction):
        if dir == "desc":
            order_by_list.append(desc(getattr(model, column)))
        elif dir == "asc":
            order_by_list.append(asc(getattr(model, column)))

    return stmt.order_by(*order_by_list)


def apply_pagination(
    __session__: Session,
    /,
    stmt: Select[Any],
    page: int,
    per_page: int,
) -> Tuple[Select[Any], str]:
    """
    Apply pagination to a SQLAlchemy select statement.

    Args:
        __session__ (Session): The SQLAlchemy session object.
        stmt (Select[Tuple[_T]]): The select statement to apply pagination to.
        page (int): The page number.
        per_page (int): The number of results per page.

    Returns:
        Tuple[Select[Tuple[_T]], str]: A tuple containing the modified select statement
        with pagination applied, and a JSON string representing the pagination information.
    """
    total_results = __session__.scalar(
        select(func.count()).select_from(stmt.subquery())
    )

    return _apply_pagination(
        stmt=stmt,
        total_results=total_results or 0,
        page=page,
        per_page=per_page,
    )


async def async_apply_pagination(
    __session__: AsyncSession,
    /,
    stmt: Select[Tuple[_T]],
    page: int,
    per_page: int,
) -> Tuple[Select[Tuple[_T]], str]:
    """
    Apply pagination to a SQLAlchemy select statement asynchronously.

    Args:
        __session__ (AsyncSession): The SQLAlchemy async session.
        stmt (Select[Tuple[_T]]): The select statement to apply pagination to.
        page (int): The page number.
        per_page (int): The number of results per page.

    Returns:
        Tuple[Select[Tuple[_T]], str]: A tuple containing the modified select statement
        with pagination applied, and a JSON string representing the pagination details.
    """
    total_results = await __session__.scalar(
        select(func.count()).select_from(stmt.subquery())
    )

    return _apply_pagination(
        stmt=stmt,
        total_results=total_results or 0,
        page=page,
        per_page=per_page,
    )


def _apply_pagination(
    stmt: Select[Tuple[_T]], total_results: int, page: int, per_page: int
) -> Tuple[Select[Tuple[_T]], str]:

    total_pages = (total_results + per_page - 1) // per_page

    pagination_dict = {
        "total": total_results,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }

    pagination = json.dumps(pagination_dict)

    stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    return stmt, pagination


def apply_limit(
    stmt: Select[Tuple[_T]],
    limit: Optional[int] = None,
) -> Select[Tuple[_T]]:
    """
    Apply a limit to the given SQL statement.

    Args:
        stmt (Select[Tuple[_T]]): The SQL statement to apply the limit to.
        limit (int): The maximum number of rows to return.

    Returns:
        Select[Tuple[_T]]: The modified SQL statement with the limit applied.
    """
    return stmt.limit(limit) if limit is not None else stmt


def get_conditions_from_dict(
    values: FilterType,
    with_optional: bool = False,
) -> List[ColumnExpressionArgument[Any]]:
    """
    Convert a dictionary of filter conditions into a list of SQLAlchemy conditions.

    Args:
        values (dict): A dictionary containing the filter conditions.
        with_optional (bool, optional): Whether to include optional conditions with a value of None. Defaults to False.

    Returns:
        List[ColumnExpressionArgument]: A list of SQLAlchemy conditions.

    """

    def is_value_null(value: Any) -> bool:
        return value is None or isinstance(value, Null)

    conditions = []
    for key, value in values.items():
        if type(value) is set:
            value = list(value)
        elif type(value) is dict:
            for k, v in value.items():
                if with_optional and v is None:
                    continue

                match k:
                    case Operators.EQUAL:
                        conditions.append(key == v)
                    case Operators.IEQUAL:
                        if not is_value_null(v):
                            conditions.append(func.lower(key) == func.lower(v))
                        else:
                            conditions.append(key == v)
                    case Operators.DIFFERENT:
                        conditions.append(key != v)
                    case Operators.IDIFFERENT:
                        if not is_value_null(v):
                            conditions.append(func.lower(key) != func.lower(v))
                        else:
                            conditions.append(key != v)
                    case Operators.LIKE:
                        if not is_value_null(v):
                            if isinstance(key, InstrumentedAttribute):
                                conditions.append(key.like(v))
                        else:
                            conditions.append(key == v)
                    case Operators.NOT_LIKE:
                        if not is_value_null(v):
                            if isinstance(key, InstrumentedAttribute):
                                conditions.append(~key.like(v))
                        else:
                            conditions.append(key != v)
                    case Operators.ILIKE:
                        if not is_value_null(v):
                            if isinstance(key, InstrumentedAttribute):
                                conditions.append(key.ilike(v))
                        else:
                            conditions.append(key == v)
                    case Operators.NOT_ILIKE:
                        if not is_value_null(v):
                            if isinstance(key, InstrumentedAttribute):
                                conditions.append(~key.ilike(v))
                        else:
                            conditions.append(key != v)
                    case Operators.BETWEEN:
                        if len(v) != 2:
                            continue
                        if v[0] is not None:
                            conditions.append(key > v[0])
                        if v[1] is not None:
                            conditions.append(key < v[1])
                    case Operators.BETWEEN_OR_EQUAL:
                        if len(v) != 2:
                            continue
                        if v[0] is not None:
                            conditions.append(key >= v[0])
                        if v[1] is not None:
                            conditions.append(key <= v[1])
                    case Operators.SUPERIOR:
                        conditions.append(key > v)
                    case Operators.INFERIOR:
                        conditions.append(key < v)
                    case Operators.SUPERIOR_OR_EQUAL:
                        conditions.append(key >= v)
                    case Operators.INFERIOR_OR_EQUAL:
                        conditions.append(key <= v)
                    case Operators.IN:
                        v = v if isinstance(v, Iterable) else [v]
                        if isinstance(key, tuple):
                            conditions.append(tuple_(*key).in_(v))
                        else:
                            conditions.append(key.in_(v))
                    case Operators.IIN:
                        v = v if isinstance(v, Iterable) else [v]
                        if isinstance(key, tuple):
                            conditions.append(
                                tuple_(*(func.lower(key_) for key_ in key)).in_(
                                    [
                                        func.lower(v_) if not is_value_null(v) else v_
                                        for v_ in v
                                    ]
                                )
                            )
                        else:
                            conditions.append(
                                func.lower(key).in_(
                                    [
                                        func.lower(v_) if not is_value_null(v) else v_
                                        for v_ in v
                                    ]
                                )
                            )
                    case Operators.NOT_IN:
                        v = v if isinstance(v, Iterable) else [v]
                        if isinstance(key, tuple):
                            conditions.append(tuple_(*key).notin_(v))
                        else:
                            conditions.append(key.notin_(v))

                    case Operators.NOT_IIN:
                        v = v if isinstance(v, Iterable) else [v]
                        if isinstance(key, tuple):
                            conditions.append(
                                tuple_(*(func.lower(key_) for key_ in key)).notin_(
                                    [
                                        func.lower(v_) if not is_value_null(v) else v_
                                        for v_ in v
                                    ]
                                )
                            )
                        else:
                            conditions.append(
                                func.lower(key).notin_(
                                    [
                                        func.lower(v_) if not is_value_null(v) else v_
                                        for v_ in v
                                    ]
                                )
                            )
                    case Operators.HAS:
                        v = get_filters(
                            v,
                            with_optional=with_optional,
                        )
                        for condition in v:
                            if isinstance(key, InstrumentedAttribute):
                                conditions.append(key.has(condition))
                    case Operators.ANY:
                        v = get_filters(
                            v,
                            with_optional=with_optional,
                        )

                        if len(v) == 0:
                            continue

                        if isinstance(key, InstrumentedAttribute):
                            conditions.append(key.any(and_(*v)))

    return conditions


def get_filters(
    filters: Optional[FilterType] = None,
    with_optional: bool = False,
) -> List[ColumnExpressionArgument[Any]]:
    """
    Get the conditions for filtering data based on the given filters.

    Args:
        filters (dict): The filters to apply on the data.
        with_optional (bool, optional): Whether to include optional filters. Defaults to False.

    Returns:
        List[ColumnExpressionArgument]: The conditions for filtering the data.
    """
    if filters is None:
        return []
    if not isinstance(filters, dict):
        raise TypeError("<filters> must be type of <dict>")

    conditions = []
    for filter_c in [{x: y} for x, y in filters.items()]:
        if type(filter_c) is not dict:
            continue

        conditions_from_dict = get_conditions_from_dict(
            filter_c,
            with_optional=with_optional,
        )
        conditions.extend(conditions_from_dict)

    return conditions
