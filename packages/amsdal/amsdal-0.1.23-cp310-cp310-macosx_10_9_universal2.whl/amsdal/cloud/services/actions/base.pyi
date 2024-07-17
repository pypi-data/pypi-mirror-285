import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amsdal.cloud.client import AuthClientService as AuthClientService
from amsdal.cloud.constants import ENCRYPT_PUBLIC_KEY as ENCRYPT_PUBLIC_KEY
from amsdal.cloud.enums import ResponseStatus as ResponseStatus
from amsdal.cloud.models.base import ResponseBaseModel as ResponseBaseModel
from amsdal.configs.main import settings as settings
from amsdal.errors import AmsdalCloudAlreadyDeployedError as AmsdalCloudAlreadyDeployedError, AmsdalCloudError as AmsdalCloudError
from enum import Enum
from typing import Any

class AuthErrorCodes(str, Enum):
    INVALID_EMAIL: str
    MISSING_CREDENTIALS: str
    INVALID_CREDENTIALS: str
    INVALID_APPLICATION_UUID: str
    CLIENT_IS_INACTIVE: str
    CLIENT_ALREADY_EXISTS: str
    DEPLOY_FAILED: str
    DEPLOY_ALREADY_EXISTS: str
    DEPLOY_NOT_IN_DEPLOYED_STATUS: str
    DESTROY_FAILED: str
    DEPLOY_NOT_FOUND: str
    INVALID_DEPENDENCY: str
    EXPOSE_DB_ACCESS_FAILED: str
    APPLICATION_ALREADY_EXISTS: str
    MULTIPLE_APPLICATIONS_FOUND: str
    MAXIMUM_APPLICATIONS_REACHED: str
    INTERNAL_SECRET: str
    BA_DOES_NOT_EXIST: str
    INVALID_IP_ADDRESS: str
    MONITORING_NOT_FOUND: str
    INVALID_ENVIRONMENT_NAME: str
    SAME_ENVIRONMENT_NAME: str
    ENVIRONMENT_NOT_FOUND: str
    ENVIRONMENT_NOT_DEPLOYED: str
    MAXIMUM_DEPLOYS_PER_APPLICATION_REACHED: str
    CANNOT_DELETE_ENVIRONMENT: str

FRIENDLY_ERROR_MESSAGES: Incomplete

class CloudActionBase(ABC, metaclass=abc.ABCMeta):
    auth_client: Incomplete
    def __init__(self) -> None: ...
    @abstractmethod
    def action(self, *args: Any, **kwargs: Any) -> Any: ...
    def _credentials_data(self) -> bytes: ...
    @staticmethod
    def _input(msg: str) -> str: ...
    @staticmethod
    def _print(msg: str) -> None: ...
    def execute_transaction(self, transaction_name: str, data: dict[str, Any]) -> dict[str, Any]: ...
    def process_errors(self, response: ResponseBaseModel) -> None: ...
