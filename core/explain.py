from __future__ import annotations

from typing import Any, Dict, List, Optional

from .schema import Finding


def summarize(findings: List[Finding], correlations: Dict[str, Any]) -> Dict[str, str]:
    if not findings:
        return {"summary": "No attacks detected in this upload.", "top_ip": ""}

    top_ip = ""
    attack_density = correlations.get("attack_density") or {}
    if attack_density:
        top_ip = max(attack_density, key=attack_density.get)

    summary = f"{len(findings)} potential issues detected."
    if top_ip:
        summary += f" Most activity observed from {top_ip}."

    return {"summary": summary, "top_ip": top_ip}


def explain_row(
    final_label: str,
    rule_hits: Optional[List[str]] = None,
    ml_label: Optional[str] = None,
    ml_proba: Optional[Dict[str, float]] = None,
) -> str:
    """
    Produce a concise human-readable explanation for a row of results.
    Detects rule/ML disagreement and surfaces top reasons.
    """
    rule_hits = rule_hits or []
    ml_label = ml_label or "Normal"
    ml_proba = ml_proba or {}

    parts: List[str] = []
    if final_label != "Normal":
        parts.append(f"Flagged as {final_label}.")
    else:
        parts.append("No rule match; ML considered normal.")

    if rule_hits:
        parts.append(f"Rule signatures hit: {', '.join(rule_hits)}.")

    # ML confidence snippet
    top_ml = sorted(ml_proba.items(), key=lambda kv: kv[1], reverse=True) if ml_proba else []
    if top_ml:
        top_label, top_prob = top_ml[0]
        parts.append(f"ML top class: {top_label} ({top_prob:.2f}).")

    # Disagreement detection
    if final_label != "Normal" and (ml_label == "Normal"):
        parts.append("ML disagrees (predicted Normal).")
    elif final_label == "Normal" and (ml_label != "Normal"):
        parts.append(f"ML suspects {ml_label}, needs review.")
    elif final_label != ml_label and ml_label:
        parts.append(f"Rule/ML differ (ML: {ml_label}).")

    return " ".join(parts)


_RULE_MAP = {
    "SQL_INJECTION_PATTERN": "SQL injection style payloads",
    "XSS_PATTERN": "cross-site scripting indicators",
    "SUSPICIOUS_KEYWORD": "suspicious keywords",
    "IP_BASED_URL": "direct IP-based access",
    "ABUSED_TLD": "use of a high-risk top-level domain",
}


def generate_why_summary(
    url: str,
    ml_label: str,
    ml_probability: float,
    rules_triggered: List[str],
    risk_score: int,
    risk_level: str,
) -> str:
    """
    Produce a concise, human-readable explanation for why a URL was flagged.
    """
    ml_conf_pct = int(round(ml_probability * 100))
    sentences = []
    sentences.append(f"The ML model predicts this URL as {ml_label} with {ml_conf_pct}% confidence.")

    if rules_triggered:
        readable = [_RULE_MAP.get(r, r.replace('_', ' ').title()) for r in rules_triggered[:3]]
        if len(readable) > 1:
            sentences.append(f"It also matches known {', '.join(readable[:-1])} and {readable[-1]}.")
        else:
            sentences.append(f"It also matches known {readable[0]}.")
    else:
        sentences.append("No explicit attack signatures were detected.")

    sentences.append(f"This results in a {risk_level} risk score of {risk_score}, indicating a strong likelihood of abuse.")

    return " ".join(sentences)
