from __future__ import annotations

from typing import Any, Dict, List, Optional

import core.ml as ml
import core.rules as rules
import core.score as score
import core.explain as explain


def _safe_url(url: str) -> str:
    return (url or "").strip()


def analyze_urls(urls: List[str]) -> List[Dict[str, Any]]:
    """
    End-to-end inference: ML + rules + risk + explanation.
    Returns one result dict per URL.
    """
    results: List[Dict[str, Any]] = []
    cleaned_urls = [_safe_url(u) for u in urls]

    try:
        ml_outputs = ml.predict_urls(cleaned_urls)
    except Exception:
        # Graceful degradation
        ml_outputs = [{"url": u, "label": "benign", "malicious_probability": 0.05} for u in cleaned_urls]

    for url, ml_out in zip(cleaned_urls, ml_outputs):
        try:
            rule_out = rules.apply_rules_url(url)
        except Exception:
            rule_out = {"rules_triggered": [], "explanations": []}

        rules_triggered = rule_out.get("rules_triggered") or []
        ml_label = ml_out.get("label", "benign")
        ml_prob = float(ml_out.get("malicious_probability", 0.0))

        risk = score.compute_risk(ml_prob, rules_triggered)
        why = explain.generate_why_summary(
            url=url,
            ml_label=ml_label,
            ml_probability=ml_prob,
            rules_triggered=rules_triggered,
            risk_score=risk["risk_score"],
            risk_level=risk["risk_level"],
        )

        results.append(
            {
                "url": url,
                "ml_label": ml_label,
                "ml_probability": ml_prob,
                "rules_triggered": rules_triggered,
                "risk_score": risk["risk_score"],
                "risk_level": risk["risk_level"],
                "why_summary": why,
            }
        )

    return results
