from _typeshed import Incomplete
from enum import Enum

class AuthType(Enum):
    CREDENTIALS: Incomplete
    TOKEN: Incomplete

class DeployType(str, Enum):
    lakehouse_only: str
    include_state_db: str

class StateOption(str, Enum):
    sqlite: str
    postgres: str

class LakehouseOption(str, Enum):
    spark: str
    postgres: str
    postgres_immutable: str

class ResponseStatus(str, Enum):
    success: str
    error: str
