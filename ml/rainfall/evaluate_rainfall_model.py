"""
WaterWatch AI - Rainfall Model Evaluation Script
Evaluates serialized rainfall-to-waterlogging classification models against
held-out test data, computing classification metrics, calibration scores,
and generating transparent evaluation artifacts.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import joblib

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    brier_score_loss, classification_report
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml.rainfall.predict_rainfall import FEATURE_COLUMNS
TARGET_COL = "waterlogging_observed"


def evaluate_model(
    model_path: Optional[str] = None,
    csv_path: Optional[str] = None,
    test_ratio: float = 0.15
) -> Dict[str, Any]:
    """
    Evaluates a saved model pipeline against the held-out test portion of the dataset.
    """
    project_root = Path(__file__).resolve().parent.parent.parent

    # Locate model
    if model_path is None:
        model_path = project_root / "ml" / "rainfall" / "rainfall_model.joblib"
        if not model_path.exists():
            model_path = project_root / "models" / "rainfall" / "best_rainfall_model.joblib"
    else:
        model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    # Locate CSV
    if csv_path is None:
        csv_path = project_root / "waterwatch_ai_nagpur_localities.csv"
        if not csv_path.exists():
            csv_path = project_root / "waterwatch_ai_nagpur_localities_sample.csv"
    else:
        csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")

    print(f"Loading model from: {model_path}")
    pipeline = joblib.load(model_path)

    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)

    # Sort chronologically for temporal test partition
    df["dt"] = pd.to_datetime(df["timestamp"])
    df_sorted = df.sort_values("dt").reset_index(drop=True)

    n_samples = len(df_sorted)
    test_start = int(n_samples * (1.0 - test_ratio))

    test_df = df_sorted.iloc[test_start:].copy()
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COL].astype(int)

    preds = pipeline.predict(X_test)
    if hasattr(pipeline, "predict_proba"):
        probs = pipeline.predict_proba(X_test)[:, 1]
    else:
        probs = np.zeros(len(X_test))

    acc = float(accuracy_score(y_test, preds))
    prec = float(precision_score(y_test, preds, zero_division=0))
    rec = float(recall_score(y_test, preds, zero_division=0))
    f1 = float(f1_score(y_test, preds, zero_division=0))
    brier = float(brier_score_loss(y_test, probs)) if hasattr(pipeline, "predict_proba") else None

    try:
        roc_auc = float(roc_auc_score(y_test, probs))
    except Exception:
        roc_auc = None

    try:
        pr_auc = float(average_precision_score(y_test, probs))
    except Exception:
        pr_auc = None

    cm = confusion_matrix(y_test, preds).tolist()

    report = {
        "model_path": str(model_path),
        "dataset_path": str(csv_path),
        "total_test_samples": len(test_df),
        "positive_test_samples": int(y_test.sum()),
        "negative_test_samples": int((1 - y_test).sum()),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
            "pr_auc": round(pr_auc, 4) if pr_auc is not None else None,
            "brier_score": round(brier, 4) if brier is not None else None,
            "confusion_matrix": cm
        },
        "classification_summary": classification_report(y_test, preds, output_dict=True, zero_division=0),
        "scientific_integrity_note": (
            "Metrics reflect performance on synthetic test labels. "
            "High or moderate scores indicate fidelity to synthetic generation heuristics, "
            "not verified empirical forecasting accuracy for Nagpur city."
        )
    }

    print("\n" + "=" * 50)
    print("WATERWATCH AI — RAINFALL MODEL EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Test Samples: {report['total_test_samples']} (Pos: {report['positive_test_samples']}, Neg: {report['negative_test_samples']})")
    print(f"Accuracy:     {report['metrics']['accuracy']:.4f}")
    print(f"Precision:    {report['metrics']['precision']:.4f}")
    print(f"Recall:       {report['metrics']['recall']:.4f}")
    print(f"F1-Score:     {report['metrics']['f1_score']:.4f}")
    print(f"ROC-AUC:      {report['metrics']['roc_auc'] if report['metrics']['roc_auc'] is not None else 'N/A'}")
    print(f"PR-AUC:       {report['metrics']['pr_auc'] if report['metrics']['pr_auc'] is not None else 'N/A'}")
    print(f"Brier Score:  {report['metrics']['brier_score'] if report['metrics']['brier_score'] is not None else 'N/A'}")
    print(f"\nConfusion Matrix (TN, FP / FN, TP):")
    print(f"  [{cm[0][0]}, {cm[0][1]}]")
    print(f"  [{cm[1][0]}, {cm[1][1]}]")
    print(f"\n[NOTE]: {report['scientific_integrity_note']}")

    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate WaterWatch AI Rainfall Model")
    parser.add_argument("--model", type=str, default=None, help="Path to model .joblib file")
    parser.add_argument("--csv", type=str, default=None, help="Path to evaluation CSV")
    args = parser.parse_args()

    evaluate_model(model_path=args.model, csv_path=args.csv)


if __name__ == "__main__":
    main()
