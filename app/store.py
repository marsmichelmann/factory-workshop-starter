"""Link storage.

The store is in memory on purpose: it keeps the starter small. Every restart
starts empty.
"""

import secrets
import threading
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

CODE_LENGTH = 6


@dataclass
class Link:
    code: str
    url: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    clicks: int = 0
    last_clicked_at: datetime | None = None


class LinkStore:
    """Holds links in a dict keyed by code."""

    def __init__(self) -> None:
        self._links: dict[str, Link] = {}
        self._lock = threading.Lock()

    def add(self, url: str) -> Link:
        with self._lock:
            code = _new_code()
            while code in self._links:
                code = _new_code()
            link = Link(code=code, url=url)
            self._links[code] = link
            return link

    def get(self, code: str) -> Link | None:
        with self._lock:
            return self._links.get(code)

    def all(self) -> list[Link]:
        """Every link, newest first."""
        with self._lock:
            return sorted(self._links.values(), key=lambda link: link.created_at, reverse=True)

    def record_click(self, code: str) -> Link | None:
        """Count one click on a link; None if the code is unknown."""
        with self._lock:
            link = self._links.get(code)
            if link is None:
                return None
            link.clicks += 1
            link.last_clicked_at = datetime.now(UTC)
            return link

    def snapshot(self, code: str) -> Link | None:
        """A copy of a link, so readers never see clicks and last_clicked_at half-updated."""
        with self._lock:
            link = self._links.get(code)
            return replace(link) if link is not None else None


def _new_code() -> str:
    # token_urlsafe gives about 1.3 chars per byte; trim to the exact length.
    return secrets.token_urlsafe(CODE_LENGTH)[:CODE_LENGTH]
