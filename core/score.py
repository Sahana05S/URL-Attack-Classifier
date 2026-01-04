from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .schema import Finding

SEVERITY_WEIGHT = {"critical": 3, "high": 2, "medium": 1, "low": 0}


def _weight(finding: Finding) -> int:
    return SEVERITY_WEIGHT.get(finding.severity.lower(), 0)


def _ip_risk_boost(ip: Optional[str], correlations: Optional[Dict]) -> float:
    if not ip or not correlations:
        return 0.0
    multi = correlations.get("multi_stage", {})
    repeated = correlations.get("repeated", {})
    boost = 0.0
    if multi.get(ip):
        boost += 0.3
    repeated_labels = repeated.get(ip, {})
    if repeated_labels:
        boost += min(0.4, 0.1 * sum(repeated_labels.values()))
    return boost


def rank(findings: List[Finding], ml_results: List[Dict], correlations: Optional[Dict] = None) -> List[Finding]:
    """
    Merge rule and ML findings and return them ordered by severity and confidence,
    with boosts for multi-stage or repeated behavior per IP.
    """
    merged: List[Finding] = list(findings)

    for result in ml_results:
        label = result.get("label")
        if label and label != "Normal":
            ip = getattr(result.get("event"), "source_ip", None)
            boost = _ip_risk_boost(ip, correlations)
            confidence = float(result.get("score", 0.5)) + boost
            merged.append(
                Finding(
                    attack_type=label,
                    severity=str(result.get("severity") or "medium"),
                    confidence=confidence,
                    event=result["event"],
                    details={"source": "ml"},
                )
            )

    return sorted(merged, key=lambda f: (_weight(f), f.confidence), reverse=True)


def compute_risk(ml_prob: float, rules_triggered: List[str]) -> Dict[str, Any]:
    """
    Compute a unified risk score (0-100) and categorical level using ML probability and rule hits.
    """
    base = float(ml_prob) * 60.0
    additions = len(rules_triggered) * 5.0
    bonus = 15.0 if any(r in {"SQL_INJECTION_PATTERN", "XSS_PATTERN"} for r in rules_triggered) else 0.0
    score = min(100.0, max(0.0, base + additions + bonus))

    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    return {"risk_score": int(round(score)), "risk_level": level}


def compute_batch_risk(ml_probs: List[float], rules_list: List[List[str]]) -> List[Dict[str, Any]]:
    return [compute_risk(p, rules) for p, rules in zip(ml_probs, rules_list)]
