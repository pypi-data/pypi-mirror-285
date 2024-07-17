from _typeshed import Incomplete
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config: Incomplete
    ADMIN_USER_EMAIL: str | None
    ADMIN_USER_PASSWORD: str | None
    AUTH_JWT_KEY: str | None
    AUTH_TOKEN_EXPIRATION: int
    REQUIRE_DEFAULT_AUTHORIZATION: bool

auth_settings: Incomplete
