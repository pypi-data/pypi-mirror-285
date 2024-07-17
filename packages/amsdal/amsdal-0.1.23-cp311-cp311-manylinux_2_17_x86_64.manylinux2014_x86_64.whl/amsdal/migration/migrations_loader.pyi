from _typeshed import Incomplete
from amsdal.migration.data_classes import MigrationFile as MigrationFile, ModuleTypes as ModuleTypes
from collections.abc import Iterator
from pathlib import Path

class MigrationsLoader:
    _migrations_path: Incomplete
    _module_type: Incomplete
    _module_name: Incomplete
    _migrations_files: Incomplete
    def __init__(self, migrations_dir: Path, module_type: ModuleTypes, module_name: str | None = None) -> None: ...
    @property
    def has_initial_migration(self) -> bool: ...
    @property
    def last_migration_number(self) -> int: ...
    def __iter__(self) -> Iterator[MigrationFile]: ...
    def _load_migration_files(self) -> None: ...
