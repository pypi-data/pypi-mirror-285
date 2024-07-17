import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amsdal.configs.constants import CORE_SCHEMAS_PATH as CORE_SCHEMAS_PATH, TYPE_SCHEMAS_PATH as TYPE_SCHEMAS_PATH
from amsdal.configs.main import settings as settings
from amsdal.migration.data_classes import ClassSchema as ClassSchema, ModuleTypes as ModuleTypes
from amsdal_models.schemas.data_models.schema import ObjectSchema
from amsdal_models.schemas.mixins.enrich_schemas_mixin import EnrichSchemasMixin
from collections.abc import Iterator
from pathlib import Path

class BaseClassSchemaLoader(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def iter_app_schemas(self) -> Iterator[ClassSchema]: ...

class JsonClassSchemaLoader(EnrichSchemasMixin, BaseClassSchemaLoader):
    schemas_root_path: Incomplete
    module_type: Incomplete
    def __init__(self, schemas_root_path: Path, module_type: ModuleTypes = ...) -> None: ...
    def iter_app_schemas(self) -> Iterator[ClassSchema]: ...
    def _enriched_user_schemas(self) -> list[ObjectSchema]: ...
    @staticmethod
    def _load_schemas(schemas_path: Path) -> list[ObjectSchema]: ...
    def _load_contrib_schemas(self) -> list[ObjectSchema]: ...
