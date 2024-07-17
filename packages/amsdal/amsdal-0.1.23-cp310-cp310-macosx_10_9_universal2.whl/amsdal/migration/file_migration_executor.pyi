from _typeshed import Incomplete
from amsdal.configs.constants import CORE_MIGRATIONS_PATH as CORE_MIGRATIONS_PATH
from amsdal.configs.main import settings as settings
from amsdal.migration.data_classes import MigrationDirection as MigrationDirection, MigrationFile as MigrationFile, MigrationResult as MigrationResult, ModuleTypes as ModuleTypes
from amsdal.migration.executors.base import BaseMigrationExecutor as BaseMigrationExecutor
from amsdal.migration.executors.state_executor import StateMigrationExecutor as StateMigrationExecutor
from amsdal.migration.file_migration_store import BaseMigrationStore as BaseMigrationStore, FileMigrationStore as FileMigrationStore
from amsdal.migration.migrations import MigrateData as MigrateData, Migration as Migration
from amsdal.migration.migrations_loader import MigrationsLoader as MigrationsLoader
from amsdal.migration.utils import contrib_to_module_root_path as contrib_to_module_root_path
from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.enums import SchemaTypes

logger: Incomplete

class FileMigrationExecutorManager:
    migration_address: Address
    core_loader: Incomplete
    contrib_loaders: Incomplete
    app_loader: Incomplete
    executor: Incomplete
    _applied_migration_files: Incomplete
    store: Incomplete
    def __init__(self, app_migrations_loader: MigrationsLoader, executor: BaseMigrationExecutor, store: BaseMigrationStore | None = None) -> None: ...
    def execute(self, migration_number: int | None = None, module_type: ModuleTypes | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]: ...
    @staticmethod
    def _get_contrib_loaders() -> list[MigrationsLoader]: ...
    def _apply(self, migration_number: int | None = None, module_type: ModuleTypes | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]: ...
    def _apply_migrations(self, loader: MigrationsLoader, module_type: ModuleTypes, migration_number: int | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]: ...
    def _register_schemas(self, executor: BaseMigrationExecutor) -> None: ...
    def _init_state_from_applied_migrations(self, migrations: list[MigrationFile], module_type: ModuleTypes) -> None: ...
    @staticmethod
    def get_migration_class(migration: MigrationFile) -> type['Migration']: ...
    def _is_migration_applied(self, migration: MigrationFile, module_type: ModuleTypes) -> bool: ...
    @staticmethod
    def _map_module_type_to_schema_type(module_type: ModuleTypes) -> SchemaTypes: ...
