import sys
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse, urlunparse

import pandas as pd
from sklearn.model_selection import train_test_split


RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/combined_dataset.csv")
PROCESSED_DIR = Path("data/processed")
TRAIN_FILE = PROCESSED_DIR / "train.csv"
VAL_FILE = PROCESSED_DIR / "val.csv"
TEST_FILE = PROCESSED_DIR / "test.csv"
URL_CANDIDATES = ["url", "URL", "Url", "link", "Link"]
MALICIOUS_KEYWORDS = ["phish", "malware", "attack", "malicious"]


def find_url_column(columns: List[str]) -> Optional[str]:
    for candidate in URL_CANDIDATES:
        if candidate in columns:
            return candidate
    return None


def infer_label(filename: str) -> str:
    name = filename.lower()
    return "malicious" if any(key in name for key in MALICIOUS_KEYWORDS) else "benign"


def clean_url(value: str) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().strip('"').strip("'")


def canonicalize_url(raw: str) -> Optional[str]:
    """
    Normalize URLs while accepting path-only inputs.
    - Prefix path-only URLs with http://example.local for parsing
    - Remove fragments, preserve query
    - Normalize scheme/domain
    - Reject URLs longer than 3000 characters or unparsable
    """
    cleaned = clean_url(raw)
    if not cleaned:
        return None

    is_path_only = cleaned.startswith("/")
    to_parse = cleaned if not is_path_only else f"http://example.local{cleaned}"

    try:
        parsed = urlparse(to_parse)
    except Exception:
        return None

    if parsed.scheme not in ("http", "https"):
        return None

    # Reconstruct without fragment
    normalized = urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "/",
            parsed.params,
            parsed.query,
            "",  # drop fragment
        )
    )

    if len(normalized) > 3000:
        return None

    return normalized


def main() -> None:
    print(f"[info] Ensuring output directories exist: {RAW_DIR}, {OUTPUT_FILE.parent}, {PROCESSED_DIR}")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not any(RAW_DIR.glob("*.csv")):
        print(f"[warn] No CSV files found in {RAW_DIR}. Nothing to process.")
        sys.exit(0)

    rows = []
    print(f"[info] Loading datasets from {RAW_DIR} ...")
    for csv_path in RAW_DIR.glob("*.csv"):
        try:
            df = pd.read_csv(csv_path, encoding="utf-8", encoding_errors="replace")
        except Exception as exc:
            print(f"[warn] Skipping {csv_path.name}: unable to read CSV ({exc})")
            continue

        url_col = find_url_column(df.columns.tolist())
        if not url_col:
            print(f"[warn] Skipping {csv_path.name}: no URL column found")
            continue

        label = infer_label(csv_path.name)
        urls = (
            df[url_col]
            .dropna()
            .astype(str)
            .map(canonicalize_url)
            .dropna()
            .tolist()
        )

        print(f"[info] {csv_path.name}: extracted {len(urls)} URLs with label '{label}'")
        for url in urls:
            rows.append({"url": url, "label": label, "source": csv_path.name})

    if not rows:
        print("[info] No data found to merge.")
        sys.exit(0)

    print("[info] Cleaning and deduplicating URLs ...")
    output_df = pd.DataFrame(rows).drop_duplicates(subset=["url"])

    # Optional balancing after deduplication
    print("[info] Checking class balance ...")
    counts = output_df["label"].value_counts()
    if len(counts) >= 2:
        majority_label = counts.idxmax()
        minority_label = counts.idxmin()
        maj_count = counts.max()
        min_count = counts.min()
        print(f"[info] Label counts before balancing: {counts.to_dict()}")
        if maj_count > 3 * min_count:
            target = 3 * min_count
            balanced_majority = (
                output_df[output_df["label"] == majority_label]
                .sample(n=target, random_state=42, replace=False)
            )
            balanced_minority = output_df[output_df["label"] == minority_label]
            output_df = pd.concat([balanced_majority, balanced_minority], ignore_index=True)
            print(
                f"[info] Balanced dataset to {majority_label}:{minority_label} = "
                f"{len(balanced_majority)}:{len(balanced_minority)}"
            )
        else:
            print("[info] Balance within threshold; no undersampling applied.")
    else:
        print("[info] Only one class present; skipping balancing.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_FILE, index=False)
    print(f"[info] Combined dataset written to {OUTPUT_FILE} ({len(output_df)} rows).")

    print("[info] Splitting dataset (stratified 70/15/15) ...")
    train_df, temp_df = train_test_split(
        output_df, test_size=0.30, stratify=output_df["label"], random_state=42, shuffle=True
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df["label"], random_state=42, shuffle=True
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(TRAIN_FILE, index=False)
    val_df.to_csv(VAL_FILE, index=False)
    test_df.to_csv(TEST_FILE, index=False)

    print("[info] Splits written:")
    print(f"  Train: {TRAIN_FILE} ({len(train_df)})")
    print(f"  Val:   {VAL_FILE} ({len(val_df)})")
    print(f"  Test:  {TEST_FILE} ({len(test_df)})")
    print("[info] Label distribution:")
    for name, df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        counts = df["label"].value_counts().to_dict()
        print(f"  {name}: {counts}")


if __name__ == "__main__":
    main()
