from contextvars import ContextVar
from typing import Any

_CONTEXT: ContextVar[dict[str, Any] | None]

class AmsdalContextManager:
    @classmethod
    def get_context(cls) -> dict[str, Any]: ...
    @classmethod
    def set_context(cls, context: dict[str, Any]) -> None: ...
    @classmethod
    def add_to_context(cls, key: str, value: Any) -> None: ...
