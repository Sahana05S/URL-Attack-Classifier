from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import joblib
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

from feature_extractor import build_feature_matrix


RANDOM_STATE = 42


def train_logistic(X_train, y_train) -> LogisticRegression:
    clf = LogisticRegression(
        max_iter=1000,
        solver="liblinear",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)
    return clf


def train_svm(X_train, y_train) -> LinearSVC:
    clf = LinearSVC(random_state=RANDOM_STATE)
    clf.fit(X_train, y_train)
    return clf


def train_random_forest(X_train, y_train) -> RandomForestClassifier:
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    clf.fit(X_train, y_train)
    return clf


def evaluate(model, X, y) -> Dict[str, float]:
    preds = model.predict(X)
    return {
        "accuracy": accuracy_score(y, preds),
        "precision": precision_score(y, preds, pos_label="malicious", average="binary", zero_division=0),
        "recall": recall_score(y, preds, pos_label="malicious", average="binary", zero_division=0),
        "f1": f1_score(y, preds, pos_label="malicious", average="binary", zero_division=0),
        "confusion_matrix": confusion_matrix(y, preds).tolist(),
    }


def main() -> None:
    X_train, X_val, X_test, y_train, y_val, y_test, vectorizer = build_feature_matrix()

    print("[info] Training Logistic Regression ...")
    log_reg = train_logistic(X_train, y_train)

    print("[info] Training Linear SVM ...")
    svm = train_svm(X_train, y_train)

    print("[info] Training Random Forest ...")
    rf = train_random_forest(X_train, y_train)

    print("[info] Evaluating models on validation set ...")
    val_results = {
        "logistic_val": evaluate(log_reg, X_val, y_val),
        "svm_val": evaluate(svm, X_val, y_val),
        "rf_val": evaluate(rf, X_val, y_val),
    }

    # Select best model by val F1
    best_name = max(val_results.items(), key=lambda kv: kv[1]["f1"])[0]
    if "logistic" in best_name:
        best_model = log_reg
    elif "svm" in best_name:
        best_model = svm
    else:
        best_model = rf
    print(f"[info] Best model on val: {best_name} (f1={val_results[best_name]['f1']:.3f})")

    print("[info] Evaluating best model on test set ...")
    test_results = {
        "best_test": evaluate(best_model, X_test, y_test),
    }

    print("[info] Evaluating models on test set ...")
    test_results.update(
        {
            "logistic_test": evaluate(log_reg, X_test, y_test),
            "svm_test": evaluate(svm, X_test, y_test),
            "rf_test": evaluate(rf, X_test, y_test),
        }
    )

    def print_report(name: str, metrics: Dict[str, float]):
        print(f"\n=== {name} ===")
        print(
            f"accuracy={metrics['accuracy']:.3f}  "
            f"precision={metrics['precision']:.3f}  "
            f"recall={metrics['recall']:.3f}  "
            f"f1={metrics['f1']:.3f}"
        )
        print(f"confusion_matrix={metrics['confusion_matrix']}")

    for name, metrics in val_results.items():
        print_report(name, metrics)
    for name, metrics in test_results.items():
        print_report(name, metrics)

    # Comparison summary table
    print("\n=== Model Comparison (val vs test) ===")
    header = f"{'Model':<10} {'Val F1':>8} {'Test F1':>10} {'Precision':>10} {'Recall':>8}"
    print(header)
    print("-" * len(header))
    for short_name, pretty in [("logistic", "LogReg"), ("svm", "LinearSVM"), ("rf", "RandomForest")]:
        val = val_results.get(f"{short_name}_val")
        tst = test_results.get(f"{short_name}_test")
        if not val or not tst:
            continue
        marker = "*" if short_name in best_name else " "
        print(
            f"{marker}{pretty:<9} {val['f1']:.3f}{'':>4} {tst['f1']:.3f}{'':>6} "
            f"{tst['precision']:.3f}{'':>5} {tst['recall']:.3f}"
        )
    print(f"\n[*] Best model selected: {best_name}")

    # Persist best model and vectorizer
    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, models_dir / "url_model.pkl")
    joblib.dump(vectorizer, models_dir / "vectorizer.pkl")
    print(f"[info] Saved best model to {models_dir / 'url_model.pkl'}")
    print(f"[info] Saved vectorizer to {models_dir / 'vectorizer.pkl'}")


if __name__ == "__main__":
    main()
