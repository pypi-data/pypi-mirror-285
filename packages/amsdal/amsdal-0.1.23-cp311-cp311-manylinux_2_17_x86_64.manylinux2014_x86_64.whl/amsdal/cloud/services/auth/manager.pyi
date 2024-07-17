from amsdal.cloud.enums import AuthType as AuthType
from amsdal.cloud.services.auth.base import AuthHandlerBase as AuthHandlerBase
from amsdal.cloud.services.auth.credentials import CredentialsAuthHandler as CredentialsAuthHandler
from amsdal.cloud.services.auth.token import TokenAuthHandler as TokenAuthHandler
from amsdal.configs.main import settings as settings
from amsdal.errors import AmsdalAuthenticationError as AmsdalAuthenticationError, AmsdalMissingCredentialsError as AmsdalMissingCredentialsError
from amsdal_utils.utils.singleton import Singleton

class AuthManager(metaclass=Singleton):
    _auth_handler: AuthHandlerBase
    def __init__(self, auth_type: AuthType | None = None) -> None: ...
    def authenticate(self) -> None: ...
