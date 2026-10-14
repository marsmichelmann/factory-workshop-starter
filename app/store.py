"""Link storage.

The store is in memory on purpose: it keeps the starter small. Every restart
starts empty.
"""

import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime

CODE_LENGTH = 6


@dataclass
class Link:
    code: str
    url: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class LinkStore:
    """Holds links in a dict keyed by code."""

    def __init__(self) -> None:
        self._links: dict[str, Link] = {}

    def add(self, url: str) -> Link:
        code = _new_code()
        while code in self._links:
            code = _new_code()
        link = Link(code=code, url=url)
        self._links[code] = link
        return link

    def get(self, code: str) -> Link | None:
        return self._links.get(code)

    def all(self) -> list[Link]:
        """Every link, newest first."""
        return sorted(self._links.values(), key=lambda link: link.created_at, reverse=True)


def _new_code() -> str:
    # token_urlsafe gives about 1.3 chars per byte; trim to the exact length.
    return secrets.token_urlsafe(CODE_LENGTH)[:CODE_LENGTH]
