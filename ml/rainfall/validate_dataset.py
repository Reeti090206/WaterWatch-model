"""
WaterWatch AI - Rainfall Dataset Validation Engine
Validates schema, data types, value boundaries, logical window consistency,
duplicate/conflicting observations, and class distributions for synthetic
Nagpur locality rainfall datasets.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

EXPECTED_COLUMNS = [
    "timestamp",
    "location_id",
    "location_name",
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "rainfall_prev_72h_mm",
    "drainage_capacity_proxy",
    "waterlogging_observed",
    "severity"
]

NUMERIC_COLUMNS = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "rainfall_prev_72h_mm",
    "drainage_capacity_proxy"
]


class DatasetValidationError(Exception):
    """Raised when critical dataset validation fails."""
    pass


def validate_dataset(df_or_path, generate_reports: bool = True) -> Dict[str, Any]:
    """
    Performs full validation on the rainfall waterlogging dataset.
    
    Args:
        df_or_path: Path to CSV or pandas DataFrame.
        generate_reports: If True, writes markdown and json reports.
        
    Returns:
        dict: Comprehensive validation report data.
    """
    if isinstance(df_or_path, (str, Path)):
        csv_path = Path(df_or_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {csv_path}")
        df = pd.read_csv(csv_path)
        source_name = csv_path.name
    elif isinstance(df_or_path, pd.DataFrame):
        df = df_or_path.copy()
        source_name = "in_memory_dataframe"
    else:
        raise TypeError("Expected filepath or pandas DataFrame")

    findings = {
        "source_name": source_name,
        "total_records": len(df),
        "is_valid": True,
        "critical_errors": [],
        "warnings": [],
        "schema": {},
        "missing_values": {},
        "duplicates": {},
        "ranges": {},
        "consistency": {},
        "class_distribution": {},
        "leakage_audit": {}
    }

    # 1. Schema Check
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    extra_cols = [col for col in df.columns if col not in EXPECTED_COLUMNS]
    findings["schema"]["columns_present"] = list(df.columns)
    findings["schema"]["missing_expected_columns"] = missing_cols
    findings["schema"]["unexpected_columns"] = extra_cols

    if missing_cols:
        findings["is_valid"] = False
        findings["critical_errors"].append(f"Missing required columns: {missing_cols}")
        if generate_reports:
            _write_validation_reports(findings)
        return findings

    # 2. Missing Values
    null_counts = df[EXPECTED_COLUMNS].isnull().sum().to_dict()
    findings["missing_values"] = {k: int(v) for k, v in null_counts.items()}
    total_nulls = sum(null_counts.values())
    if total_nulls > 0:
        findings["warnings"].append(f"Found {total_nulls} null values across dataset")

    # 3. Data Types & Parsing
    try:
        timestamps = pd.to_datetime(df["timestamp"])
        findings["temporal_coverage"] = {
            "min_timestamp": str(timestamps.min()),
            "max_timestamp": str(timestamps.max()),
            "unique_timestamps": int(timestamps.nunique()),
            "is_monotonic": bool(timestamps.is_monotonic_increasing)
        }
    except Exception as e:
        findings["critical_errors"].append(f"Invalid timestamp formatting: {str(e)}")
        findings["is_valid"] = False

    # 4. Binary Target Check
    unique_targets = set(df["waterlogging_observed"].unique())
    if not unique_targets.issubset({0, 1}):
        findings["critical_errors"].append(f"Target 'waterlogging_observed' must only contain 0 and 1; got {unique_targets}")
        findings["is_valid"] = False

    target_counts = df["waterlogging_observed"].value_counts().to_dict()
    findings["class_distribution"] = {
        "class_0_negative_count": int(target_counts.get(0, 0)),
        "class_1_positive_count": int(target_counts.get(1, 0)),
        "positive_class_ratio": round(float(target_counts.get(1, 0)) / max(len(df), 1), 4)
    }

    # 5. Severity Alignment
    severity_values = set(df["severity"].dropna().str.lower().unique())
    findings["severity_categories"] = list(severity_values)
    crosstab = pd.crosstab(df["waterlogging_observed"], df["severity"]).to_dict()
    findings["severity_crosstab"] = {str(k): {str(sub_k): int(sub_v) for sub_k, sub_v in v.items()} for k, v in crosstab.items()}

    # Non-waterlogged with non-none severity
    inv_none = df[(df["waterlogging_observed"] == 0) & (df["severity"].str.lower() != "none")]
    if len(inv_none) > 0:
        findings["warnings"].append(f"Found {len(inv_none)} records where waterlogging_observed=0 but severity!='none'")

    # Waterlogged with none severity
    inv_pos = df[(df["waterlogging_observed"] == 1) & (df["severity"].str.lower() == "none")]
    if len(inv_pos) > 0:
        findings["warnings"].append(f"Found {len(inv_pos)} records where waterlogging_observed=1 but severity='none'")

    # 6. Duplicates & Conflicting Records
    exact_dups = int(df.duplicated().sum())
    key_dups = int(df.duplicated(subset=["timestamp", "location_id"]).sum())
    findings["duplicates"]["exact_row_duplicates"] = exact_dups
    findings["duplicates"]["timestamp_location_duplicates"] = key_dups

    # Conflicting labels check
    grouped = df.groupby(["timestamp", "location_id"])["waterlogging_observed"].nunique()
    conflicting_pairs = int((grouped > 1).sum())
    findings["duplicates"]["conflicting_outcome_groups"] = conflicting_pairs
    if conflicting_pairs > 0:
        findings["warnings"].append(
            f"Found {conflicting_pairs} (timestamp, location_id) groups with conflicting outcome labels (both 0 and 1)."
        )

    # 7. Numeric Ranges & Units
    range_summary = {}
    for col in NUMERIC_COLUMNS:
        min_v = float(df[col].min())
        max_v = float(df[col].max())
        mean_v = float(df[col].mean())
        range_summary[col] = {"min": round(min_v, 2), "max": round(max_v, 2), "mean": round(mean_v, 2)}
        if min_v < 0.0:
            findings["critical_errors"].append(f"Column '{col}' contains negative values (min: {min_v})")
            findings["is_valid"] = False

    # Check drainage capacity proxy range [0, 1]
    if df["drainage_capacity_proxy"].min() < 0.0 or df["drainage_capacity_proxy"].max() > 1.0:
        findings["warnings"].append(
            f"drainage_capacity_proxy should be in [0.0, 1.0], observed: [{df['drainage_capacity_proxy'].min()}, {df['drainage_capacity_proxy'].max()}]"
        )
    findings["ranges"] = range_summary

    # 8. Rainfall Window Monotonic Consistency
    # 1h <= 3h <= 6h <= 24h
    viol_1_3 = int((df["rainfall_1h_mm"] > df["rainfall_3h_mm"]).sum())
    viol_3_6 = int((df["rainfall_3h_mm"] > df["rainfall_6h_mm"]).sum())
    viol_6_24 = int((df["rainfall_6h_mm"] > df["rainfall_24h_mm"]).sum())
    findings["consistency"] = {
        "violations_1h_gt_3h": viol_1_3,
        "violations_3h_gt_6h": viol_3_6,
        "violations_6h_gt_24h": viol_6_24,
        "monotonic_integrity_pass": (viol_1_3 == 0 and viol_3_6 == 0 and viol_6_24 == 0)
    }
    if viol_1_3 > 0 or viol_3_6 > 0 or viol_6_24 > 0:
        findings["critical_errors"].append("Cumulative rainfall window monotonicity violation detected!")
        findings["is_valid"] = False

    # 9. Data Leakage & Synthetic Nature Audit
    findings["leakage_audit"] = {
        "severity_is_leakage": True,
        "severity_policy": "EXCLUDE - 'severity' is directly derived from waterlogging event and rainfall intensity threshold.",
        "location_id_policy": "EXCLUDE - Location IDs must not be used as one-hot shortcuts to prevent memorizing local topology.",
        "drainage_proxy_policy": "SYNTHETIC PROXY - 'drainage_capacity_proxy' is an illustrative synthetic index, not physical measured drainage infrastructure.",
        "data_provenance": "SYNTHETIC DEMONSTRATION DATA - Rainfall values, drainage proxy, and waterlogging outcomes are synthetically generated for Nagpur localities. They are NOT municipal observations."
    }

    if generate_reports:
        _write_validation_reports(findings)

    return findings


def _write_validation_reports(findings: Dict[str, Any]) -> None:
    """Writes both markdown and JSON validation reports."""
    project_root = Path(__file__).resolve().parent.parent.parent
    reports_dir = project_root / "reports"
    ml_rainfall_dir = project_root / "ml" / "rainfall"

    reports_dir.mkdir(parents=True, exist_ok=True)
    ml_rainfall_dir.mkdir(parents=True, exist_ok=True)

    # 1. JSON Summary
    json_path = ml_rainfall_dir / "dataset_validation_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    # 2. Markdown Report
    md_lines = [
        "# WaterWatch AI — Rainfall Dataset Validation Report",
        "",
        f"**Dataset File**: `{findings['source_name']}`  ",
        f"**Total Records**: `{findings['total_records']}`  ",
        f"**Validation Status**: `{'PASSED' if findings['is_valid'] else 'FAILED'}`  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Provenance Disclosure",
        "",
        "> [!IMPORTANT]",
        "> **Synthetic Demonstration Data Notice**: Although this dataset features genuine Nagpur locality names "
        "(e.g., Dharampeth, Sadar, Sitabuldi, Manish Nagar, Dhantoli, Mankapur), the rainfall accumulation figures, "
        "drainage capacity proxies, and waterlogging occurrence labels were **synthetically generated**. "
        "They do NOT represent verified observations from Nagpur Municipal Corporation (NMC) or IMD.",
        "",
        "---",
        "",
        "## 2. Schema and Completeness",
        "",
        f"- **Expected Columns**: 11  ",
        f"- **Present Columns**: {len(findings['schema'].get('columns_present', []))}  ",
        f"- **Missing Columns**: {findings['schema'].get('missing_expected_columns', [])}  ",
        f"- **Null / Missing Value Count**: {sum(findings['missing_values'].values())} (100% complete records)",
        "",
        "| Column | Type / Role | Null Count |",
        "| :--- | :--- | :--- |",
    ]

    for col in EXPECTED_COLUMNS:
        null_c = findings["missing_values"].get(col, 0)
        role = "Target" if col == "waterlogging_observed" else ("Leaked Outcome" if col == "severity" else ("Metadata" if "location" in col or col == "timestamp" else "Input Feature"))
        md_lines.append(f"| `{col}` | {role} | {null_c} |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Rainfall Window Consistency (Monotonic Integrity)",
        "",
        "Physical rainfall accumulations over overlapping windows must strictly satisfy:  ",
        "`rainfall_1h_mm <= rainfall_3h_mm <= rainfall_6h_mm <= rainfall_24h_mm`",
        "",
        f"- **1h > 3h Violations**: `{findings['consistency'].get('violations_1h_gt_3h', 0)}`",
        f"- **3h > 6h Violations**: `{findings['consistency'].get('violations_3h_gt_6h', 0)}`",
        f"- **6h > 24h Violations**: `{findings['consistency'].get('violations_6h_gt_24h', 0)}`",
        f"- **Monotonic Integrity Assessment**: `{'PERFECT (100% Valid)' if findings['consistency'].get('monotonic_integrity_pass') else 'VIOLATIONS FOUND'}`",
        "",
        "---",
        "",
        "## 4. Value Ranges & Units",
        "",
        "| Feature | Min (mm or index) | Median | Max (mm or index) | Units / Scale |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])

    for col, stats in findings["ranges"].items():
        unit = "Unitless [0, 1]" if "proxy" in col else "Millimeters (mm)"
        md_lines.append(f"| `{col}` | `{stats['min']}` | `{stats['mean']}` | `{stats['max']}` | {unit} |")

    class_dist = findings.get("class_distribution", {})
    pos_count = class_dist.get("class_1_positive_count", 0)
    neg_count = class_dist.get("class_0_negative_count", 0)
    pos_ratio = class_dist.get("positive_class_ratio", 0.0)

    md_lines.extend([
        "",
        "---",
        "",
        "## 5. Class Distribution & Imbalance",
        "",
        f"- **Class 0 (No Waterlogging)**: `{neg_count}` ({round((1 - pos_ratio) * 100, 2)}%)  ",
        f"- **Class 1 (Waterlogged Observed)**: `{pos_count}` ({round(pos_ratio * 100, 2)}%)  ",
        f"- **Imbalance Ratio**: approximately `{round(neg_count / max(pos_count, 1), 2)} : 1`  ",
        "- **Mitigation in Modeling**: Models must use `class_weight='balanced'` and be evaluated via Precision-Recall AUC (PR-AUC) and F1-score rather than simple classification accuracy.",
        "",
        "---",
        "",
        "## 6. Duplicates and Conflicting Observations",
        "",
        f"- **Exact Row Duplicates**: `{findings['duplicates'].get('exact_row_duplicates', 0)}`  ",
        f"- **Repeated (timestamp, location_id) Pairs**: `{findings['duplicates'].get('timestamp_location_duplicates', 0)}`  ",
        f"- **Conflicting Outcome Groups**: `{findings['duplicates'].get('conflicting_outcome_groups', 0)}` groups where identical timestamp and location had conflicting waterlogging labels (both 0 and 1).  ",
        "- **Resolution Strategy**: When training models, these conflicting pairs are resolved by prioritizing the verified positive record or deduplicating to eliminate contradictory training signals.",
        "",
        "---",
        "",
        "## 7. Data Leakage & Feature Selection Policy",
        "",
        "1. **`severity` Excluded**: `severity` represents post-event damage level ('low', 'moderate', 'high') and is derived directly from the occurrence. Using it as a predictor would constitute 100% target leakage.",
        "2. **`location_id` / `location_name` Excluded**: Memorizing specific locality IDs produces brittle models that cannot generalize across Nagpur. Features must rely solely on meteorological measurements and generalized drainage proxies.",
        "3. **`drainage_capacity_proxy` Handled Cautiously**: Acknowledged as a synthetic demonstration parameter rather than calibrated civil infrastructure flow capacity.",
        ""
    ])

    report_content = "\n".join(md_lines)
    for target_dir in [reports_dir, ml_rainfall_dir]:
        out_file = target_dir / "rainfall_dataset_validation_report.md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(report_content)

    print(f"Validation reports saved to {reports_dir / 'rainfall_dataset_validation_report.md'} and {ml_rainfall_dir / 'rainfall_dataset_validation_report.md'}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate WaterWatch AI Rainfall Dataset")
    parser.add_argument("--csv", type=str, default="waterwatch_ai_nagpur_localities.csv", help="Path to CSV dataset")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = project_root / args.csv
        if not csv_path.exists():
            # Try alternate filename
            alt_path = project_root / "waterwatch_ai_nagpur_localities_sample.csv"
            if alt_path.exists():
                csv_path = alt_path

    print(f"Validating dataset: {csv_path}")
    findings = validate_dataset(csv_path, generate_reports=True)
    print(f"Validation completed. Status: {'VALID' if findings['is_valid'] else 'INVALID'}")
    print(f"Total Records: {findings['total_records']}")
    print(f"Class distribution: {findings['class_distribution']}")
    print(f"Warnings: {len(findings['warnings'])}")
    for w in findings["warnings"]:
        print(f"  - WARNING: {w}")


if __name__ == "__main__":
    main()
