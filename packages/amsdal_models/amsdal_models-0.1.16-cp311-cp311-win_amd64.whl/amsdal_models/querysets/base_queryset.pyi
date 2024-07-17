from _typeshed import Incomplete
from amsdal_models.classes.model import Model as Model
from amsdal_models.querysets.errors import BulkOperationError as BulkOperationError, MultipleObjectsReturnedError as MultipleObjectsReturnedError, ObjectDoesNotExistError as ObjectDoesNotExistError
from amsdal_models.querysets.executor import DEFAULT_DB_ALIAS as DEFAULT_DB_ALIAS, Executor as Executor
from amsdal_utils.query.utils import Q
from typing import Any, Generic, TypeVar
from typing_extensions import Self

logger: Incomplete
ModelType = TypeVar('ModelType', bound='Model')

class QuerySetBase(Generic[ModelType]):
    """
    Base class for QuerySets.
    """
    _entity: Incomplete
    _paginator: Incomplete
    _order_by: Incomplete
    _query_specifier: Incomplete
    _conditions: Incomplete
    _using: Incomplete
    def __init__(self, entity: type[ModelType]) -> None: ...
    @property
    def entity_name(self) -> str: ...
    def using(self, value: str) -> Self: ...
    @classmethod
    def _from_queryset(cls, queryset: QuerySetBase) -> Self: ...
    def _copy(self) -> Self: ...
    def __copy__(self) -> Self: ...
    def only(self, fields: list[str]) -> Self:
        """
        Limit the number of fields to be returned.


        :param fields: the fields to be returned
        :type fields: list[str]

        :rtype: Self
        """
    def distinct(self, fields: list[str]) -> Self:
        """
        Return only distinct (different) values.

        :param fields: the fields to be distinct
        :type fields: list[str]

        :rtype: Self
        """
    def filter(self, *args: Q, **kwargs: Any) -> Self:
        """
        Apply filters to the query. The filters are combined with AND.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: Self
        """
    def exclude(self, *args: Q, **kwargs: Any) -> Self:
        """
        Exclude filters from the query. The filters are combined with AND.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: Self
        """
    def _execute_query(self) -> list[dict[str, Any]]: ...
    def _execute_count(self) -> int: ...
    def _filter(self, *args: Q, negated: bool = ..., **kwargs: Any) -> Self: ...
    def order_by(self, *args: str) -> Self:
        """
        Order the query by the given fields.

        :param args: the fields to order by
        :type args: str

        :rtype: Self
        """
    def __getitem__(self, index: slice | int) -> Self: ...
    def _create_instance(self, *, _is_partial: bool, **kwargs: Any) -> ModelType: ...
    def latest(self) -> Self: ...
    def _check_type(self, obj: ModelType) -> None: ...
    def bulk_update(self, objs: list[ModelType], using: str | None = ...) -> None: ...
    def bulk_create(self, objs: list[ModelType], using: str | None = ...) -> None: ...
    def bulk_delete(self, objs: list[ModelType], using: str | None = ...) -> None: ...

class QuerySet(QuerySetBase[ModelType], Generic[ModelType]):
    """
    Interface to access the database.
    """
    def get(self, *args: Q, **kwargs: Any) -> QuerySetOneRequired[ModelType]:
        """
        Change the QuerySet to a QuerySetOneRequired. Query execution will return a single item or raise an error.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: QuerySetOneRequired
        """
    def get_or_none(self, *args: Q, **kwargs: Any) -> QuerySetOne[ModelType]:
        """
        Change the QuerySet to a QuerySetOne. Query execution will return a single item or None.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: QuerySetOneRequired
        """
    def first(self, *args: Q, **kwargs: Any) -> QuerySetOne[ModelType]:
        """
        Change the QuerySet to a QuerySetOne. Query execution will return the first item or None.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: QuerySetOneRequired
        """
    def count(self) -> QuerySetCount[ModelType]:
        """
        Change the QuerySet to a QuerySetCount. Query execution will return the count of items.
        """
    def execute(self) -> list[ModelType]:
        """
        Return the list of items.

        :rtype: list[ModelType]
        """
    def only(self, fields: list[str]) -> Self: ...
    def distinct(self, fields: list[str]) -> Self: ...
    def filter(self, *args: Q, **kwargs: Any) -> Self: ...
    def exclude(self, *args: Q, **kwargs: Any) -> Self: ...
    def order_by(self, *args: str) -> Self: ...

class QuerySetOne(QuerySetBase[ModelType], Generic[ModelType]):
    """
    QuerySet class for models. QuerySet is executed to a single model object or None.
    """
    _raise_on_multiple: bool
    def __init__(self, entity: type[ModelType]) -> None: ...
    def only(self, fields: list[str]) -> Self: ...
    def distinct(self, fields: list[str]) -> Self: ...
    def filter(self, *args: Q, **kwargs: Any) -> Self: ...
    def exclude(self, *args: Q, **kwargs: Any) -> Self: ...
    def order_by(self, *args: str) -> Self: ...
    def execute(self) -> ModelType | None:
        """
        Query the database and return the single item or None.

        :raises MultipleObjectsReturnedError: If multiple items are found.

        :rtype: Model | None
        """

class QuerySetOneRequired(QuerySetOne[ModelType], Generic[ModelType]):
    """
    QuerySet class for models. QuerySet is executed to a single model object or raises an error.
    """
    def only(self, fields: list[str]) -> Self: ...
    def distinct(self, fields: list[str]) -> Self: ...
    def filter(self, *args: Q, **kwargs: Any) -> Self: ...
    def exclude(self, *args: Q, **kwargs: Any) -> Self: ...
    def order_by(self, *args: str) -> Self: ...
    def execute(self) -> ModelType:
        """
        Return the single item.

        :raises ObjectDoesNotExistError: If no items are found.

        :rtype: Model

        """

class QuerySetCount(QuerySetBase[ModelType], Generic[ModelType]):
    """
    QuerySet class for models. QuerySet is executed to a count of items.
    """
    def only(self, fields: list[str]) -> Self: ...
    def distinct(self, fields: list[str]) -> Self: ...
    def filter(self, *args: Q, **kwargs: Any) -> Self: ...
    def exclude(self, *args: Q, **kwargs: Any) -> Self: ...
    def order_by(self, *args: str) -> Self: ...
    def execute(self) -> int:
        """
        Return the count of items.

        :rtype: int
        """
