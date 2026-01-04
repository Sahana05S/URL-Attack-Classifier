from __future__ import annotations

from typing import List
from urllib.parse import unquote

from .types import Event


def normalize_events(events: List[Event]) -> List[Event]:
    normalized: List[Event] = []
    for event in events:
        raw_url = (event.url or "").strip()
        decoded_url = unquote(raw_url)
        cleaned_url = decoded_url.strip()
        if cleaned_url and "://" not in cleaned_url and not cleaned_url.startswith("/"):
            cleaned_url = f"/{cleaned_url}"

        method = (event.method or "").strip().lower() or None
        meta = dict(event.metadata or {})
        meta.update({"decoded_url": decoded_url, "clean_url": cleaned_url})

        normalized.append(
            Event(
                url=cleaned_url,
                timestamp=event.timestamp,
                status_code=event.status_code,
                source_ip=(event.source_ip or "").strip() or None,
                user_agent=(event.user_agent or "").strip() or None,
                method=method,
                referer=(event.referer or "").strip() or None,
                request_id=(event.request_id or "").strip() or None,
                metadata=meta,
            )
        )
    return normalized
