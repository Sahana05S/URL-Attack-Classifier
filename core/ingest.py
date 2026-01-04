from __future__ import annotations

import io
from datetime import datetime
from typing import List, Tuple

import pandas as pd

from .types import Event

SUPPORTED_COLUMNS = {
    "timestamp",
    "ts",
    "ip",
    "source_ip",
    "method",
    "url",
    "status_code",
    "user_agent",
    "referer",
    "request_id",
}


def _maybe_int(value):
    if pd.isna(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _maybe_str(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def _parse_timestamp(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return datetime.utcnow()
    try:
        return pd.to_datetime(value).to_pydatetime()
    except Exception:
        return datetime.utcnow()


def load_csv(file_bytes: bytes) -> Tuple[List[Event], pd.DataFrame]:
    """
    Read CSV bytes and emit Event objects.
    Returns both the events and the raw DataFrame for downstream use.
    """
    buffer = io.BytesIO(file_bytes)
    df = pd.read_csv(buffer)

    events: List[Event] = []
    for row in df.to_dict(orient="records"):
        ts_value = row.get("timestamp", row.get("ts"))
        metadata = {k: v for k, v in row.items() if k not in SUPPORTED_COLUMNS}

        ip_value = _maybe_str(row.get("ip")) or _maybe_str(row.get("source_ip")) or "unknown"

        events.append(
            Event(
                url=str(row.get("url", "") or ""),
                timestamp=_parse_timestamp(ts_value),
                status_code=_maybe_int(row.get("status_code")),
                source_ip=ip_value,
                user_agent=_maybe_str(row.get("user_agent")),
                method=(_maybe_str(row.get("method")) or "GET").upper(),
                referer=_maybe_str(row.get("referer")),
                request_id=_maybe_str(row.get("request_id")),
                metadata=metadata,
            )
        )

    return events, df
