from __future__ import annotations

import pandas as pd
import re
import math
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


def _safe_parse(url: str):
    if not isinstance(url, str):
        return None
    if url.startswith("/"):
        url = f"http://example.local{url}"
    try:
        return urlparse(url)
    except Exception:
        return None


def _count_digits(text: str) -> int:
    return sum(ch.isdigit() for ch in text or "")


def _count_special(text: str) -> int:
    return len(re.findall(r"[^a-zA-Z0-9]", text or ""))


def _count_keywords(text: str, keywords) -> int:
    lowered = (text or "").lower()
    return sum(kw in lowered for kw in keywords)


def _has_ip(domain: str) -> int:
    if not domain:
        return 0
    # Simple IPv4 check
    parts = domain.split(".")
    if len(parts) != 4:
        return 0
    for part in parts:
        if not part.isdigit():
            return 0
        val = int(part)
        if val < 0 or val > 255:
            return 0
    return 1


def _tld_risk(domain: str) -> int:
    if not domain or "." not in domain:
        return 1
    tld = domain.rsplit(".", 1)[-1].lower()
    if tld in {"tk", "ml", "ga", "cf"}:
        return 3
    if tld in {"ru", "cn", "xyz"}:
        return 2
    return 1


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    entropy = 0.0
    for c in counts.values():
        p = c / length
        entropy -= p * math.log2(p)
    return entropy


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with columns ['url', 'label'], return a DataFrame
    with engineered numeric features and the label.
    """
    suspicious_keywords = ["login", "verify", "update", "secure", "admin", "cmd", "wp", "shell", "exec"]
    feature_rows = []
    for _, row in df.iterrows():
        url = row.get("url", "")
        parsed = _safe_parse(url)
        if not parsed:
            continue

        domain = parsed.netloc or ""
        path = parsed.path or ""
        query = parsed.query or ""
        url_len = len(url)
        num_digits = _count_digits(url)
        num_special = _count_special(url)
        num_upper = sum(ch.isupper() for ch in url or "")
        keyword_count = _count_keywords(url, suspicious_keywords)
        has_ip = _has_ip(domain)
        tld_risk = _tld_risk(domain)

        safe_div = lambda num: (num / url_len) if url_len else 0.0

        feature_rows.append(
            {
                "url_length": url_len,
                "domain_length": len(domain),
                "path_length": len(path),
                "query_length": len(query),
                "num_digits": num_digits,
                "num_special_chars": num_special,
                "num_subdomains": max(0, domain.count(".") - 1) if domain else 0,
                "digit_ratio": safe_div(num_digits),
                "symbol_ratio": safe_div(num_special),
                "uppercase_ratio": safe_div(num_upper),
                "shannon_entropy": _entropy(url),
                "suspicious_keyword_count": keyword_count,
                "has_ip_address": has_ip,
                "tld_risk_score": tld_risk,
                "label": row.get("label"),
            }
        )

    return pd.DataFrame(feature_rows)


def build_tfidf_features(urls: pd.Series):
    """
    Build character-level TF-IDF features for a series of URLs.
    Returns (sparse_matrix, fitted_vectorizer).
    """
    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        max_features=5000,
        lowercase=True,
    )
    X = vectorizer.fit_transform(urls.fillna("").astype(str))
    return X, vectorizer


def build_feature_matrix(processed_dir: Path = Path("data/processed")):
    """
    Build combined numeric + TF-IDF feature matrices for train/val/test splits.
    Returns: X_train, X_val, X_test, y_train, y_val, y_test, vectorizer
    """
    train_path = processed_dir / "train.csv"
    val_path = processed_dir / "val.csv"
    test_path = processed_dir / "test.csv"

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)

    # Numeric features
    train_num = extract_features(train_df)
    val_num = extract_features(val_df)
    test_num = extract_features(test_df)

    y_train = train_num.pop("label")
    y_val = val_num.pop("label")
    y_test = test_num.pop("label")

    # TF-IDF (fit on train, apply to val/test)
    tfidf_train, vectorizer = build_tfidf_features(train_df["url"])
    tfidf_val = vectorizer.transform(val_df["url"].fillna("").astype(str))
    tfidf_test = vectorizer.transform(test_df["url"].fillna("").astype(str))

    # Concatenate numeric + tfidf
    X_train = hstack([csr_matrix(train_num.values), tfidf_train])
    X_val = hstack([csr_matrix(val_num.values), tfidf_val])
    X_test = hstack([csr_matrix(test_num.values), tfidf_test])

    return X_train, X_val, X_test, y_train, y_val, y_test, vectorizer
