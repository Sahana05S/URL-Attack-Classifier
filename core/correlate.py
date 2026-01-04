from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Sequence

from .store import SessionStore
from .types import Event, Finding


def correlate_sessions(
    events: List[Event],
    findings: List[Finding],
    ml_results: Sequence[Dict[str, Any]],
    store: SessionStore,
) -> Dict[str, Any]:
    """
    Group events by IP, derive attack stages, and build ordered chains.
    """
    for event in events:
        store.add_event(event)

    def stage_for_label(label: str) -> str:
        key = (label or "").lower()
        if key in ["normal", "benign"]:
            return "benign"
        if key in ["directory traversal"]:
            return "reconnaissance"
        if key in ["sql injection", "command injection", "xss"]:
            return "exploitation"
        if key in ["ssrf"]:
            return "lateral movement"
        return "suspicious"

    # Pre-index findings per event for quick lookup
    findings_by_event = defaultdict(list)
    for f in findings:
        findings_by_event[f.event].append(f)

    # Build per-IP attack chains
    chains: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    attack_density: Counter[str] = Counter()
    repeated: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for idx, event in enumerate(events):
        ip = event.source_ip or "unknown"
        event_findings: List[Finding] = findings_by_event.get(event, [])
        ml_entry: Optional[Dict[str, Any]] = ml_results[idx] if idx < len(ml_results) else None

        # Determine primary label
        label = event_findings[0].attack_type if event_findings else (ml_entry.get("label") if ml_entry else "Normal")
        stage = stage_for_label(label)
        hits = []
        for f in event_findings:
            detail_hits = f.details.get("hits") if f.details else None
            if isinstance(detail_hits, list):
                hits.extend(detail_hits)
            elif detail_hits:
                hits.append(str(detail_hits))

        attack_density[ip] += 0 if label.lower() in ["normal", "benign"] else 1
        repeated[ip][label] += 1

        chains[ip].append(
            {
                "order": idx,
                "timestamp": event.timestamp,
                "label": label,
                "stage": stage,
                "hits": hits,
                "ml": ml_entry or {},
                "findings": event_findings,
            }
        )

    session_counts = {ip: len(evts) for ip, evts in store.iter_sessions()}

    multi_stage_flags = {
        ip: len({entry["stage"] for entry in chain if entry["stage"] != "benign"}) > 1
        for ip, chain in chains.items()
    }

    repeated_attempts = {
        ip: {label: count for label, count in labels.items() if count > 1}
        for ip, labels in repeated.items()
    }

    return {
        "sessions": session_counts,
        "attack_density": dict(attack_density),
        "chains": dict(chains),
        "multi_stage": multi_stage_flags,
        "repeated": repeated_attempts,
    }


def correlate_sequences(
    events: List[Event],
    findings: List[Finding],
    ml_results: Sequence[Dict[str, Any]],
    store: SessionStore,
) -> Dict[str, Any]:
    """
    Alias for correlate_sessions for clearer intent when building ordered chains.
    """
    return correlate_sessions(events, findings, ml_results, store)
