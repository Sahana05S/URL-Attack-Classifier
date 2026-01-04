from __future__ import annotations

import re
from typing import Any, Dict, List
from urllib.parse import urlparse

from .schema import Event, Finding

SQL_PATTERN = re.compile(
    r"('|\%27)\s*or\s*1=1|--|union\s+select|\%3d|\%27", re.IGNORECASE
)
XSS_PATTERN = re.compile(
    r"<script|javascript:|onerror=|onload=|\%3cscript\%3e", re.IGNORECASE
)
SUSPICIOUS_KEYWORDS = ["login", "verify", "update", "secure", "admin", "cmd", "wp", "shell", "exec"]
ABUSED_TLDS_HIGH = {"tk", "ml", "ga", "cf"}
ABUSED_TLDS_MEDIUM = {"ru", "cn", "xyz"}


def _is_ipv4(host: str) -> bool:
    if not host:
        return False
    host = host.split(":")[0]  # strip port
    parts = host.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def _tld(host: str) -> str:
    host = host.split(":")[0] if host else ""
    if "." not in host:
        return ""
    return host.rsplit(".", 1)[-1].lower()


def apply_rules_url(url: str) -> Dict[str, Any]:
    """
    Detect well-known malicious URL patterns and return rule hits + explanations.
    Does NOT assign a final label or score.
    """
    rules_triggered: List[str] = []
    explanations: List[str] = []

    target = url or ""
    parsed = urlparse(target if "://" in target else f"http://example.local{target}")
    host = parsed.netloc
    lower_url = target.lower()

    # SQLi
    if SQL_PATTERN.search(lower_url):
        rules_triggered.append("SQL_INJECTION_PATTERN")
        explanations.append("SQLi indicators found (e.g., UNION/OR=1).")

    # XSS
    if XSS_PATTERN.search(lower_url):
        rules_triggered.append("XSS_PATTERN")
        explanations.append("XSS indicators found (e.g., <script>, javascript:).")

    # Suspicious keywords
    if any(kw in lower_url for kw in SUSPICIOUS_KEYWORDS):
        rules_triggered.append("SUSPICIOUS_KEYWORD")
        explanations.append("Suspicious keywords present (login/verify/update/etc.).")

    # IP-based URL
    if _is_ipv4(host):
        rules_triggered.append("IP_BASED_URL")
        explanations.append("Domain is a raw IPv4 address.")

    # Abused TLDs
    tld = _tld(host)
    if tld in ABUSED_TLDS_HIGH:
        rules_triggered.append("ABUSED_TLD")
        explanations.append(f"High-risk TLD detected: .{tld}")
    elif tld in ABUSED_TLDS_MEDIUM:
        rules_triggered.append("ABUSED_TLD")
        explanations.append(f"Medium-risk TLD detected: .{tld}")

    return {"rules_triggered": rules_triggered, "explanations": explanations}


# Legacy compatibility for existing pipeline usage
def _apply_rules_features(features: List[dict]) -> List[Finding]:
    findings: List[Finding] = []
    severity_map = {
        "SQL_INJECTION_PATTERN": "high",
        "XSS_PATTERN": "medium",
        "SUSPICIOUS_KEYWORD": "low",
        "IP_BASED_URL": "medium",
        "ABUSED_TLD": "low",
    }
    attack_map = {
        "SQL_INJECTION_PATTERN": "SQL Injection",
        "XSS_PATTERN": "XSS",
        "SUSPICIOUS_KEYWORD": "Suspicious",
        "IP_BASED_URL": "Suspicious",
        "ABUSED_TLD": "Suspicious",
    }

    for row in features:
        event: Event = row["event"]
        url = (event.metadata or {}).get("clean_url") if event.metadata else None
        url = url or event.url or ""
        detection = apply_rules_url(url)
        triggers = detection["rules_triggered"]
        if not triggers:
            continue
        confidence = min(0.6 + 0.05 * (len(triggers) - 1), 0.95)
        for trig in triggers:
            findings.append(
                Finding(
                    attack_type=attack_map.get(trig, "Suspicious"),
                    severity=severity_map.get(trig, "medium"),
                    confidence=confidence,
                    event=event,
                    details={"rule": trig, "explanations": detection["explanations"]},
                )
            )
    return findings


def rule_detect(events: List[Event]) -> List[Dict]:
    """
    Wrapper for compatibility; returns per-event labels based on apply_rules.
    """
    results: List[Dict] = []
    for event in events:
        url = (event.metadata or {}).get("clean_url") if event.metadata else None
        url = url or event.url or ""
        detection = apply_rules_url(url)
        label = (
            "Normal"
            if not detection["rules_triggered"]
            else ("SQL Injection" if "SQL_INJECTION_PATTERN" in detection["rules_triggered"] else detection["rules_triggered"][0])
        )
        confidence = 0.05 if not detection["rules_triggered"] else min(0.6 + 0.05 * (len(detection["rules_triggered"]) - 1), 0.95)
        results.append({"event": event, "label": label, "hits": detection["rules_triggered"], "confidence": confidence})
    return results


def apply_rules_legacy(features: List[dict]) -> List[Finding]:
    return _apply_rules_features(features)


def apply_rules(arg):  # type: ignore
    """
    Dispatcher:
    - If passed a URL string, return rule triggers/explanations.
    - If passed feature rows (list of dicts with 'event'), return findings (legacy pipeline support).
    """
    if isinstance(arg, str):
        return apply_rules_url(arg)
    if isinstance(arg, list) and arg and isinstance(arg[0], dict) and "event" in arg[0]:
        return _apply_rules_features(arg)
    return []
