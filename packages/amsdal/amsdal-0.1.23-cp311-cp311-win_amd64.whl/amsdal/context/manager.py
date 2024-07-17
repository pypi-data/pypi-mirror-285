from contextvars import ContextVar
from typing import Any

_CONTEXT: ContextVar[dict[str, Any] | None] = ContextVar('_context', default=None)


class AmsdalContextManager:
    @classmethod
    def get_context(cls) -> dict[str, Any]:
        _context = _CONTEXT.get()

        if _context is not None:
            return _context

        new_context: dict[str, Any] = {}
        cls.set_context(new_context)

        return new_context

    @classmethod
    def set_context(cls, context: dict[str, Any]) -> None:
        _CONTEXT.set(context)

    @classmethod
    def add_to_context(cls, key: str, value: Any) -> None:
        context = cls.get_context()

        context[key] = value

        cls.set_context(context)
