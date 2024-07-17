import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amsdal.migration.base_migration_schemas import BaseMigrationSchemas as BaseMigrationSchemas, DefaultMigrationSchemas as DefaultMigrationSchemas
from amsdal.migration.executors.base import BaseMigrationExecutor as BaseMigrationExecutor
from amsdal_utils.models.enums import SchemaTypes as SchemaTypes
from collections.abc import Callable as Callable
from typing import Any

class Operation(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def forward(self, executor: BaseMigrationExecutor) -> None: ...
    @abstractmethod
    def forward_schema(self, executor: BaseMigrationExecutor) -> None: ...
    @abstractmethod
    def backward(self, executor: BaseMigrationExecutor) -> None: ...

class SchemaOperation(Operation):
    forward_args: list[Any]
    backward_args: list[Any]
    forward_method_name: str
    backward_method_name: str
    def forward(self, executor: BaseMigrationExecutor) -> None: ...
    def forward_schema(self, executor: BaseMigrationExecutor) -> None: ...
    def backward(self, executor: BaseMigrationExecutor) -> None: ...

class CreateClass(SchemaOperation):
    forward_method_name: str
    backward_method_name: str
    forward_args: Incomplete
    backward_args: Incomplete
    def __init__(self, class_name: str, new_schema: dict[str, Any], schema_type: SchemaTypes) -> None: ...

class UpdateClass(SchemaOperation):
    forward_method_name: str
    backward_method_name: str
    forward_args: Incomplete
    backward_args: Incomplete
    def __init__(self, class_name: str, old_schema: dict[str, Any], new_schema: dict[str, Any], schema_type: SchemaTypes) -> None: ...

class DeleteClass(SchemaOperation):
    forward_method_name: str
    backward_method_name: str
    forward_args: Incomplete
    backward_args: Incomplete
    def __init__(self, class_name: str, old_schema: dict[str, Any], schema_type: SchemaTypes) -> None: ...

class MigrationSchemas(DefaultMigrationSchemas): ...

class MigrateData(Operation):
    @staticmethod
    def noop(schemas: MigrationSchemas) -> None: ...
    forward_migration: Incomplete
    backward_migration: Incomplete
    def __init__(self, forward_migration: Callable[[MigrationSchemas | BaseMigrationSchemas], None], backward_migration: Callable[[MigrationSchemas | BaseMigrationSchemas], None]) -> None: ...
    def forward(self, executor: BaseMigrationExecutor) -> None: ...
    def backward(self, executor: BaseMigrationExecutor) -> None: ...
    def forward_schema(self, executor: BaseMigrationExecutor) -> None: ...

class Migration:
    operations: list[Operation]
