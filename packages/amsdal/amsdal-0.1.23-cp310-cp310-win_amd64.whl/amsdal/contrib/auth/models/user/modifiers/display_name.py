@property  # type: ignore[misc]
def display_name(self) -> str:  # type: ignore[no-untyped-def]
    return self.email


def __str__(self) -> str:  # type: ignore[no-untyped-def]  # noqa: N807
    return f'User(email={self.email})'


def __repr__(self) -> str:  # type: ignore[no-untyped-def]  # noqa: N807
    return str(self)
