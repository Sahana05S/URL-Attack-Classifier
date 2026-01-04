from __future__ import annotations

from typing import Any, Dict, List
from urllib.parse import urlparse

from .types import Event


def extract_features(events: List[Event]) -> List[Dict[str, Any]]:
    feature_rows: List[Dict[str, Any]] = []
    for event in events:
        parsed = urlparse(event.url or "")
        path = parsed.path or ""
        query = parsed.query or ""
        url_lower = (event.url or "").lower()

        feature_rows.append(
            {
                "event": event,
                "path": path,
                "query": query,
                "url_length": len(event.url or ""),
                "has_query": bool(query),
                "has_extension": "." in path.split("/")[-1] if path else False,
                "contains_sql": any(token in url_lower for token in ["union", "select", "--", "' or"]),
                "contains_traversal": "../" in url_lower or "..\\" in url_lower,
                "status_code": event.status_code,
                "source_ip": event.source_ip,
            }
        )
    return feature_rows
