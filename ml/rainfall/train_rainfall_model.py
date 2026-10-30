"""
WaterWatch AI - Rainfall Model Training Engine
Trains, validates, compares, and serializes machine learning models for
rainfall-based waterlogging risk prediction on Nagpur locality datasets.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import joblib

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    brier_score_loss, classification_report
)
from sklearn.model_selection import StratifiedKFold

# Ensure package imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml.rainfall.validate_dataset import validate_dataset

FEATURE_COLUMNS = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "rainfall_prev_72h_mm",
    "drainage_capacity_proxy"
]

TARGET_COLUMN = "waterlogging_observed"


def train_and_evaluate(
    csv_path: str = None,
    output_dir: str = None,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Executes full training and evaluation pipeline for rainfall models.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    if csv_path is None:
        csv_path = project_root / "waterwatch_ai_nagpur_localities.csv"
        if not csv_path.exists():
            csv_path = project_root / "waterwatch_ai_nagpur_localities_sample.csv"
    else:
        csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Rainfall dataset not found at: {csv_path}")

    # Validate dataset first
    print(f"Validating dataset at: {csv_path}")
    val_findings = validate_dataset(csv_path, generate_reports=True)
    if not val_findings["is_valid"]:
        raise ValueError(f"Dataset validation failed: {val_findings['critical_errors']}")

    df = pd.read_csv(csv_path)

    # Chronological sort for temporal integrity
    df["dt"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("dt").reset_index(drop=True)

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].astype(int)

    n_samples = len(df)
    train_end = int(n_samples * 0.70)
    val_end = int(n_samples * 0.85)

    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_val, y_val = X.iloc[train_end:val_end], y.iloc[train_end:val_end]
    X_test, y_test = X.iloc[val_end:], y.iloc[val_end:]

    print(f"Data split (Chronological): Train={len(X_train)} ({y_train.sum()} pos), "
          f"Val={len(X_val)} ({y_val.sum()} pos), Test={len(X_test)} ({y_test.sum()} pos)")

    # Define candidate classifiers
    candidate_clfs = {
        "MajorityBaseline": DummyClassifier(strategy="most_frequent"),
        "LogisticRegression": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=random_state
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, max_depth=6, min_samples_leaf=5,
            class_weight="balanced", random_state=random_state
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=100, max_depth=4, learning_rate=0.05,
            class_weight="balanced", random_state=random_state
        )
    }

    eval_results = {}
    fitted_pipelines = {}

    for name, clf in candidate_clfs.items():
        if name == "MajorityBaseline":
            pipe = Pipeline([("clf", clf)])
        else:
            pipe = Pipeline([("scaler", StandardScaler()), ("clf", clf)])

        pipe.fit(X_train, y_train)
        fitted_pipelines[name] = pipe

        # Predictions on Test set
        test_preds = pipe.predict(X_test)
        if hasattr(pipe, "predict_proba"):
            test_probs = pipe.predict_proba(X_test)[:, 1]
        else:
            test_probs = np.zeros(len(X_test))

        acc = accuracy_score(y_test, test_preds)
        prec = precision_score(y_test, test_preds, zero_division=0)
        rec = recall_score(y_test, test_preds, zero_division=0)
        f1 = f1_score(y_test, test_preds, zero_division=0)
        brier = brier_score_loss(y_test, test_probs) if hasattr(pipe, "predict_proba") else None
        
        try:
            roc_auc = roc_auc_score(y_test, test_probs)
        except Exception:
            roc_auc = None

        try:
            pr_auc = average_precision_score(y_test, test_probs)
        except Exception:
            pr_auc = None

        cm = confusion_matrix(y_test, test_preds).tolist()

        eval_results[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4) if roc_auc is not None else None,
            "pr_auc": round(float(pr_auc), 4) if pr_auc is not None else None,
            "brier_score": round(float(brier), 4) if brier is not None else None,
            "confusion_matrix": cm
        }
        print(f"[{name}] Acc: {acc:.3f}, Prec: {prec:.3f}, Rec: {rec:.3f}, F1: {f1:.3f}, "
              f"ROC-AUC: {roc_auc if roc_auc is not None else 0.0:.3f}, PR-AUC: {pr_auc if pr_auc is not None else 0.0:.3f}")

    # Determine best model based on PR-AUC / F1
    trained_models = {k: v for k, v in eval_results.items() if k != "MajorityBaseline"}
    best_name = max(trained_models.keys(), key=lambda k: trained_models[k]["f1_score"])
    best_pipeline = fitted_pipelines[best_name]
    print(f"\nSelected Best Supervised Model: {best_name} (F1: {eval_results[best_name]['f1_score']})")

    # Save artifacts
    ml_rainfall_dir = project_root / "ml" / "rainfall"
    models_rainfall_dir = project_root / "models" / "rainfall"
    reports_dir = project_root / "reports"

    for d in [ml_rainfall_dir, models_rainfall_dir, reports_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Save model pipelines
    joblib.dump(best_pipeline, ml_rainfall_dir / "rainfall_model.joblib")
    joblib.dump(best_pipeline, models_rainfall_dir / "synthetic_rainfall_model.joblib")
    print(f"Saved best model pipeline to {ml_rainfall_dir / 'rainfall_model.joblib'}")

    # 2. Extract feature coefficients / importances if available
    feature_importance = {}
    clf_obj = best_pipeline.named_steps["clf"]
    if hasattr(clf_obj, "feature_importances_"):
        for f, imp in zip(FEATURE_COLUMNS, clf_obj.feature_importances_):
            feature_importance[f] = round(float(imp), 4)
    elif hasattr(clf_obj, "coef_"):
        for f, coef in zip(FEATURE_COLUMNS, clf_obj.coef_[0]):
            feature_importance[f] = round(float(coef), 4)

    # 3. Model Metadata
    metadata = {
        "model_name": best_name,
        "model_type": type(clf_obj).__name__,
        "model_version": "1.0.0-synthetic",
        "training_data": {
            "source_file": csv_path.name,
            "provenance": "SYNTHETIC_EXPERIMENTAL",
            "locality_scope": "Nagpur Localities (Demonstration)",
            "total_samples": n_samples,
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "test_samples": len(X_test),
            "positive_class_ratio_train": round(float(y_train.mean()), 4),
            "positive_class_ratio_test": round(float(y_test.mean()), 4),
            "split_type": "Chronological Holdout (70/15/15) to prevent rolling window leakage"
        },
        "feature_schema": {
            "feature_order": FEATURE_COLUMNS,
            "feature_descriptions": {
                "rainfall_1h_mm": "Acute 1-hour rainfall accumulation in mm",
                "rainfall_3h_mm": "Cumulative 3-hour rainfall accumulation in mm",
                "rainfall_6h_mm": "Cumulative 6-hour rainfall accumulation in mm",
                "rainfall_24h_mm": "Cumulative 24-hour rainfall accumulation in mm",
                "rainfall_prev_72h_mm": "Antecedent 72-hour soil saturation rainfall in mm",
                "drainage_capacity_proxy": "Synthetic locality runoff clearance rate (index in [0.0, 1.0])"
            },
            "excluded_features": [
                "severity (100% target leakage)",
                "location_id / location_name (locality memorization bias prevention)"
            ]
        },
        "feature_importance_or_coefficients": feature_importance,
        "evaluation_metrics_test_set": eval_results[best_name],
        "all_model_evaluations": eval_results,
        "operational_warnings": [
            "Trained on synthetic demonstration records, not real Nagpur Municipal Corporation (NMC) field incident telemetry.",
            "Do NOT treat model score as a calibrated real-world flooding probability.",
            "High test metrics reflect synthetic rule learning rather than genuine hydrology."
        ]
    }

    for meta_path in [ml_rainfall_dir / "model_metadata.json", models_rainfall_dir / "model_metadata.json"]:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    # 4. Generate Comprehensive Evaluation Report
    _write_evaluation_report(metadata, eval_results, ml_rainfall_dir, reports_dir)

    return {
        "best_model_name": best_name,
        "eval_results": eval_results,
        "metadata": metadata
    }


def _write_evaluation_report(metadata, eval_results, ml_rainfall_dir, reports_dir):
    """Writes detailed markdown evaluation report."""
    md = [
        "# WaterWatch AI — Rainfall-to-Waterlogging Model Evaluation Report",
        "",
        f"**Best Model**: `{metadata['model_name']}` (`{metadata['model_type']}`)  ",
        f"**Model Version**: `{metadata['model_version']}`  ",
        f"**Data Provenance**: `{metadata['training_data']['provenance']}`  ",
        f"**Split Strategy**: `{metadata['training_data']['split_type']}`  ",
        "",
        "---",
        "",
        "## 1. Scientific Integrity & Model Limitations",
        "",
        "> [!WARNING]",
        "> **Notice of Synthetic Data Limitation**: This model was trained on `waterwatch_ai_nagpur_localities.csv`. "
        "While locality identifiers correspond to genuine Nagpur neighborhoods (Dharampeth, Sadar, Sitabuldi, etc.), "
        "the rainfall measurements, drainage proxies, and binary waterlogging labels were synthetically generated. "
        "Consequently, the model learns the **synthetic labeling rules**, not real-world urban runoff dynamics. "
        "This model is **NOT calibrated for operational civic alerting** and must be labeled strictly as an **experimental synthetic-data baseline**.",
        "",
        "---",
        "",
        "## 2. Test Set Evaluation Benchmark (Chronological Holdout)",
        "",
        f"- **Train Samples**: `{metadata['training_data']['train_samples']}`  ",
        f"- **Validation Samples**: `{metadata['training_data']['val_samples']}`  ",
        f"- **Held-Out Test Samples**: `{metadata['training_data']['test_samples']}`  ",
        f"- **Test Class Balance**: Positive={metadata['training_data']['positive_class_ratio_test'] * 100:.1f}%, Negative={(1 - metadata['training_data']['positive_class_ratio_test']) * 100:.1f}%",
        "",
        "| Model Algorithm | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Brier Score |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for name, m in eval_results.items():
        roc = f"{m['roc_auc']:.4f}" if m['roc_auc'] is not None else "N/A"
        pr = f"{m['pr_auc']:.4f}" if m['pr_auc'] is not None else "N/A"
        brier = f"{m['brier_score']:.4f}" if m['brier_score'] is not None else "N/A"
        md.append(f"| **{name}** | `{m['accuracy']:.4f}` | `{m['precision']:.4f}` | `{m['recall']:.4f}` | `{m['f1_score']:.4f}` | `{roc}` | `{pr}` | `{brier}` |")

    best_m = eval_results[metadata["model_name"]]
    cm = best_m["confusion_matrix"]

    md.extend([
        "",
        "---",
        "",
        f"## 3. Confusion Matrix for Best Model (`{metadata['model_name']}`)",
        "",
        "| | Predicted Non-Waterlogged (0) | Predicted Waterlogged (1) |",
        "| :--- | :--- | :--- |",
        f"| **Actual Non-Waterlogged (0)** | `{cm[0][0]}` (TN) | `{cm[0][1]}` (FP) |",
        f"| **Actual Waterlogged (1)** | `{cm[1][0]}` (FN) | `{cm[1][1]}` (TP) |",
        "",
        "---",
        "",
        "## 4. Feature Importance & Coefficients",
        "",
        "| Feature | Role / Importance | Hydrological Meaning |",
        "| :--- | :--- | :--- |",
    ])

    for feat, imp in metadata.get("feature_importance_or_coefficients", {}).items():
        md.append(f"| `{feat}` | `{imp}` | {metadata['feature_schema']['feature_descriptions'].get(feat, '')} |")

    md.extend([
        "",
        "---",
        "",
        "## 5. Prevented Target Leakage",
        "",
        "- **`severity` completely omitted**: `severity` is assigned only when an event occurs, encoding direct post-hoc labels.",
        "- **`location_id` / `location_name` omitted**: Models trained on locality dummy codes memorize locality frequency rather than physical rainfall-runoff mechanics.",
        "- **Chronological Temporal Split**: Prevents overlapping rolling rainfall windows (3h, 6h, 24h, 72h) from leaking into future test intervals."
    ])

    report_text = "\n".join(md)
    for d in [ml_rainfall_dir, reports_dir]:
        out_path = d / "evaluation_report.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Saved evaluation report to {out_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Train WaterWatch AI Rainfall Model")
    parser.add_argument("--csv", type=str, default="waterwatch_ai_nagpur_localities.csv", help="Path to input CSV")
    args = parser.parse_args()

    train_and_evaluate(csv_path=args.csv)


if __name__ == "__main__":
    main()
