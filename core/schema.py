from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Event:
    """Normalized request/response level event."""

    url: str
    timestamp: Optional[datetime] = None
    status_code: Optional[int] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    method: Optional[str] = None
    referer: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Finding:
    """Represents a detection outcome attached to an event."""

    attack_type: str
    severity: str
    confidence: float
    event: Event
    details: Dict[str, Any] = field(default_factory=dict)

    def short_reason(self) -> str:
        return self.details.get("reason") or self.attack_type
