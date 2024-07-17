from amsdal_models.classes.model import Model
from amsdal_models.schemas.data_models.schema import ObjectSchema, PropertyData
from amsdal_utils.models.data_models.address import Address as Address
from amsdal_utils.models.enums import SchemaTypes as SchemaTypes
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class Action(str, Enum):
    CREATED: str
    UPDATED: str
    NO_ACTION: str

@dataclass
class ClassSaveResult:
    action: Action
    instance: Model
    def __init__(self, action, instance) -> None: ...

@dataclass
class ClassUpdateResult:
    is_updated: bool
    class_instance: Model
    def __init__(self, is_updated, class_instance) -> None: ...

@dataclass
class MigrateResult:
    class_instance: Model
    is_table_created: bool
    is_data_migrated: bool
    def __init__(self, class_instance, is_table_created, is_data_migrated) -> None: ...

class ModuleTypes(str, Enum):
    APP: str
    CORE: str
    CONTRIB: str

@dataclass
class MigrationFile:
    path: Path
    type: ModuleTypes
    number: int
    module: str | None = ...
    applied_at: float | None = ...
    stored_address: Address | None = ...
    @property
    def is_initial(self) -> bool: ...
    def __init__(self, path, type, number, module=..., applied_at=..., stored_address=...) -> None: ...

@dataclass
class ClassSchema:
    object_schema: ObjectSchema
    type: ModuleTypes
    def __init__(self, object_schema, type) -> None: ...

class OperationTypes(str, Enum):
    CREATE_CLASS: str
    UPDATE_CLASS: str
    DELETE_CLASS: str

@dataclass
class MigrateOperation:
    type: OperationTypes
    class_name: str
    schema_type: SchemaTypes
    old_schema: ObjectSchema | PropertyData | None = ...
    new_schema: ObjectSchema | PropertyData | None = ...
    def __init__(self, type, class_name, schema_type, old_schema=..., new_schema=...) -> None: ...

class MigrationDirection(str, Enum):
    FORWARD: str
    BACKWARD: str

@dataclass
class MigrationResult:
    direction: MigrationDirection
    migration: MigrationFile
    def __init__(self, direction, migration) -> None: ...
