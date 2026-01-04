from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .types import Event


class SessionStore:
    """
    In-memory session store keyed by source IP.

    Useful for quick correlation across multiple events coming from the same
    client during a single Streamlit session.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, List[Event]] = {}

    def add_event(self, event: Event) -> None:
        ip = event.source_ip or "unknown"
        self._sessions.setdefault(ip, []).append(event)

    def get_events(self, ip: str) -> List[Event]:
        return list(self._sessions.get(ip, []))

    def iter_sessions(self) -> Iterable[tuple[str, List[Event]]]:
        for ip, events in self._sessions.items():
            yield ip, list(events)

    def clear(self, ip: Optional[str] = None) -> None:
        if ip is None:
            self._sessions.clear()
        else:
            self._sessions.pop(ip, None)

    def __len__(self) -> int:
        return sum(len(events) for events in self._sessions.values())
