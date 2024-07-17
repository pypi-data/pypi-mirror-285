from amsdal.migration.data_classes import MigrateOperation as MigrateOperation, OperationTypes as OperationTypes
from pathlib import Path
from typing import ClassVar

class FileMigrationWriter:
    template_path: Path
    data_template_path: Path
    operation_name_map: ClassVar[dict[OperationTypes, str]]
    @classmethod
    def write(cls, file_path: Path, operations: list[MigrateOperation]) -> None: ...
    @classmethod
    def write_data_migration(cls, file_path: Path) -> None: ...
    @classmethod
    def render(cls, operations: list[MigrateOperation]) -> str: ...
    @classmethod
    def render_operation(cls, operation: MigrateOperation) -> str: ...
    @classmethod
    def reformat(cls, content: str) -> str: ...
