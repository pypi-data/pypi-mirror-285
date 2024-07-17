import logging
from typing import Any
from typing import Generic

from amsdal_utils.models.enums import Versions
from amsdal_utils.query.utils import Q

from amsdal_models.querysets.base_queryset import ModelType
from amsdal_models.querysets.base_queryset import QuerySet
from amsdal_models.querysets.base_queryset import QuerySetOne
from amsdal_models.querysets.base_queryset import QuerySetOneRequired
from amsdal_models.querysets.executor import LAKEHOUSE_DB_ALIAS

logger = logging.getLogger(__name__)


class BaseManager(Generic[ModelType]):
    """
    Base manager for creating QuerySets for models.
    """

    model: type[ModelType]

    def copy(self, cls: type[ModelType]) -> 'BaseManager':
        manager = self.__class__()
        manager.model = cls

        return manager

    def get_queryset(self) -> QuerySet[ModelType]:
        return QuerySet(self.model)

    def using(self, value: str) -> QuerySet[ModelType]:
        return self.get_queryset().using(value)

    def all(self) -> QuerySet[ModelType]:
        return self.get_queryset()

    def only(self, fields: list[str]) -> QuerySet[ModelType]:
        return self.get_queryset().only(fields=fields)

    def distinct(self, fields: list[str]) -> QuerySet[ModelType]:
        return self.get_queryset().distinct(fields=fields)

    def filter(self, *args: Q, **kwargs: Any) -> QuerySet[ModelType]:
        return self.get_queryset().filter(*args, **kwargs)

    def exclude(self, *args: Q, **kwargs: Any) -> QuerySet[ModelType]:
        return self.get_queryset().exclude(*args, **kwargs)

    def get(self, *args: Q, **kwargs: Any) -> QuerySetOneRequired[ModelType]:
        return self.get_queryset().get(*args, **kwargs)

    def get_or_none(self, *args: Q, **kwargs: Any) -> QuerySetOne[ModelType]:
        return self.get_queryset().get_or_none(*args, **kwargs)

    def first(self, *args: Q, **kwargs: Any) -> QuerySetOne[ModelType]:
        return self.get_queryset().first(*args, **kwargs)

    def latest(self) -> QuerySet[ModelType]:
        return self.get_queryset().latest()

    def previous_version(self, obj: ModelType) -> ModelType | None:
        object_id = obj.get_metadata().address.object_id
        object_version = obj.get_metadata().prior_version

        return self.get_specific_version(object_id, object_version)

    def next_version(self, obj: ModelType) -> ModelType | None:
        object_id = obj.get_metadata().address.object_id
        object_version = obj.get_metadata().next_version

        return self.get_specific_version(object_id, object_version)

    def get_specific_version(self, object_id: str, object_version: str | None) -> ModelType | None:
        if not object_version:
            return None

        return (
            self.get_queryset()
            .using(LAKEHOUSE_DB_ALIAS)
            .get(
                _address__class_version=Versions.ALL,
                _address__object_id=object_id,
                _address__object_version=object_version,
            )
            .execute()
        )

    def bulk_update(self, objs: list[ModelType], using: str | None = None) -> None:
        self.get_queryset().bulk_update(objs, using=using)

    def bulk_create(self, objs: list[ModelType], using: str | None = None) -> None:
        self.get_queryset().bulk_create(objs, using=using)

    def bulk_delete(self, objs: list[ModelType], using: str | None = None) -> None:
        self.get_queryset().bulk_delete(objs, using=using)
