from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack

from feature_extractor import extract_features

MODEL_PATH = Path("models/url_model.pkl")
VECTORIZER_PATH = Path("models/vectorizer.pkl")

_MODEL_CACHE: Tuple[Any, Any] | None = None  # (model, vectorizer)
_NUMERIC_COLUMNS: List[str] | None = None


def _load_model_and_vectorizer() -> Tuple[Any, Any]:
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        raise FileNotFoundError("Trained model/vectorizer not found in models/. Run training first.")
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    _MODEL_CACHE = (model, vectorizer)
    return _MODEL_CACHE


def _numeric_columns() -> List[str]:
    global _NUMERIC_COLUMNS
    if _NUMERIC_COLUMNS is not None:
        return _NUMERIC_COLUMNS
    # Infer column order from feature_extractor
    sample_df = extract_features(pd.DataFrame([{"url": "http://example.local", "label": None}]))
    cols = [c for c in sample_df.columns if c != "label"]
    _NUMERIC_COLUMNS = cols
    return cols


def _build_numeric_matrix(urls: List[str]) -> csr_matrix:
    cols = _numeric_columns()
    rows = []
    for url in urls:
        feat_df = extract_features(pd.DataFrame([{"url": url, "label": None}]))
        if feat_df.empty:
            row = {c: 0.0 for c in cols}
        else:
            row = feat_df.iloc[0].to_dict()
            row.pop("label", None)
            # Ensure all columns present and ordered
            row = {c: row.get(c, 0.0) for c in cols}
        rows.append([row[c] for c in cols])
    return csr_matrix(np.array(rows))


def _malicious_probs(model, X) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        classes = list(model.classes_)
        if "malicious" in classes:
            idx = classes.index("malicious")
            return proba[:, idx]
        # default to last column if label not found
        return proba[:, -1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        if scores.ndim > 1:
            # multiclass: pick column for malicious if present
            classes = list(getattr(model, "classes_", []))
            if "malicious" in classes:
                idx = classes.index("malicious")
                scores = scores[:, idx]
            else:
                scores = scores.max(axis=1)
        # sigmoid to probability
        return 1 / (1 + np.exp(-scores))
    preds = model.predict(X)
    return np.array([1.0 if p == "malicious" else 0.0 for p in preds])


def predict_urls(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Pure inference: given a list of URLs, return predicted label and malicious probability.
    """
    model, vectorizer = _load_model_and_vectorizer()
    numeric_matrix = _build_numeric_matrix(urls)
    tfidf_matrix = vectorizer.transform(pd.Series(urls).fillna("").astype(str))
    X = hstack([numeric_matrix, tfidf_matrix])

    probs = _malicious_probs(model, X)
    results: List[Dict[str, Any]] = []
    for url, prob in zip(urls, probs):
        label = "malicious" if prob >= 0.5 else "benign"
        results.append({"url": url, "label": label, "malicious_probability": float(prob)})
    return results


# Backward-compatible API for pipeline
def ml_predict(events: List[Any], feature_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    urls = []
    for event in events:
        url = None
        if getattr(event, "metadata", None):
            meta = event.metadata
            url = meta.get("clean_url") or meta.get("decoded_url") if isinstance(meta, dict) else None
        urls.append(url or getattr(event, "url", ""))

    try:
        preds = predict_urls(urls)
    except FileNotFoundError:
        # fallback if model not available
        return [{"event": e, "label": "Normal", "score": 0.05, "proba": {"malicious": 0.05, "benign": 0.95}} for e in events]

    results = []
    for event, pred in zip(events, preds):
        prob = pred["malicious_probability"]
        label = pred["label"]
        proba = {"malicious": prob, "benign": 1 - prob}
        results.append({"event": event, "label": label, "score": prob, "proba": proba})
    return results
