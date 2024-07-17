from _typeshed import Incomplete
from amsdal.__about__ import __version__ as __version__
from amsdal.cloud.client import AuthClientService as AuthClientService
from amsdal.cloud.constants import ENCRYPT_PUBLIC_KEY as ENCRYPT_PUBLIC_KEY, SYNC_KEY as SYNC_KEY
from amsdal.cloud.services.actions.create_session import CreateSessionAction as CreateSessionAction
from amsdal.cloud.services.auth.base import AuthHandlerBase as AuthHandlerBase
from amsdal.cloud.services.auth.token import TokenAuthHandler as TokenAuthHandler
from amsdal.errors import AmsdalAuthenticationError as AmsdalAuthenticationError
from amsdal.schemas.manager import SchemaManager as SchemaManager

class CredentialsAuthHandler(AuthHandlerBase):
    __access_key_id: Incomplete
    __secret_access_key: Incomplete
    __fernet: Incomplete
    auth_client: Incomplete
    def __init__(self, access_key_id: str | None, secret_access_key: str | None) -> None: ...
    def _create_session(self) -> str: ...
    def _get_public_key(self) -> str: ...
    def _decode_public_key(self, key: str) -> str: ...
    def validate_credentials(self) -> None: ...
