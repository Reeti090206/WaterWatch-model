"""
WaterWatch AI - Dataset Merging and Split Engine (Phase 4)
Integrates verified IndiaScene365 negative road scenes with the existing waterlogging dataset.
Maintains strict 70/15/15 splits, empty YOLO label files for negatives,
preserves valid positive bounding boxes, and generates split manifests.
"""

import os
import sys
import shutil
import json
import random
from pathlib import Path
import yaml
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
YOLO_DIR = PROCESSED_DIR / "yolo_water_logging"
CLS_DIR = PROCESSED_DIR / "classification_water_logging"
NEG_MANIFEST_PATH = PROCESSED_DIR / "verified_negatives" / "verified_negatives_manifest.json"
MANIFESTS_DIR = DATA_DIR / "manifests"
REPORTS_DIR = PROJECT_ROOT / "reports"

MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def merge_datasets(seed=42):
    print("=" * 65)
    print("PHASE 4: MERGING WATERLOGGED AND VERIFIED NEGATIVE DATASETS")
    print("=" * 65)

    random.seed(seed)

    # 1. Collect all original positive images and their labels
    # Source from backup directory or extracted roboflow_raw
    positive_candidates = []
    backup_dir = PROCESSED_DIR / "yolo_water_logging_pre_merge_backup"
    source_dir = backup_dir if backup_dir.exists() else YOLO_DIR
    
    for split in ["train", "val", "test"]:
        split_img_dir = source_dir / "images" / split
        split_lbl_dir = source_dir / "labels" / split
        if not split_img_dir.exists():
            continue
        for img_file in split_img_dir.iterdir():
            if img_file.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            lbl_file = split_lbl_dir / (img_file.stem + ".txt")
            if lbl_file.exists():
                with open(lbl_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    # Positive image with bounding boxes
                    positive_candidates.append({
                        "image_path": img_file,
                        "label_path": lbl_file,
                        "label_content": content,
                        "filename": img_file.name,
                        "category": "waterlogged"
                    })

    # If count is 0, fallback to raw extracted
    if len(positive_candidates) == 0:
        raw_roboflow = DATA_DIR / "extracted" / "roboflow_raw"
        for img_file in raw_roboflow.rglob("*.*"):
            if img_file.suffix.lower() in (".jpg", ".jpeg", ".png"):
                lbl_file = img_file.parent.parent / "labels" / (img_file.stem + ".txt")
                if lbl_file.exists():
                    content = lbl_file.read_text().strip()
                    if content:
                        positive_candidates.append({
                            "image_path": img_file,
                            "label_path": lbl_file,
                            "label_content": content,
                            "filename": img_file.name,
                            "category": "waterlogged"
                        })

    # Deduplicate positive candidates by filename
    pos_dict = {p["filename"]: p for p in positive_candidates}
    pos_list = sorted(list(pos_dict.values()), key=lambda x: x["filename"])
    print(f"Total verified positive waterlogging images found: {len(pos_list)}")

    # 2. Collect verified negative images
    if not NEG_MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Verified negatives manifest not found at {NEG_MANIFEST_PATH}. Run prepare_indiascene365_negatives.py first!")

    with open(NEG_MANIFEST_PATH, "r", encoding="utf-8") as f:
        neg_meta = json.load(f)

    neg_list = []
    for item in neg_meta:
        img_p = PROJECT_ROOT / item["local_processed_path"]
        if img_p.exists():
            neg_list.append({
                "image_path": img_p,
                "label_path": None,
                "label_content": "",  # Empty label for background / negative in YOLO
                "filename": item["curated_filename"],
                "category": "not_waterlogged",
                "source_meta": item
            })

    print(f"Total verified negative road images loaded: {len(neg_list)}")

    # 3. Deterministic 70 / 15 / 15 Split for both classes
    def split_class(items, train_ratio=0.70, val_ratio=0.15):
        shuffled = list(items)
        random.shuffle(shuffled)
        n = len(shuffled)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        train_items = shuffled[:n_train]
        val_items = shuffled[n_train:n_train + n_val]
        test_items = shuffled[n_train + n_val:]
        return train_items, val_items, test_items

    pos_train, pos_val, pos_test = split_class(pos_list, 0.70, 0.15)
    neg_train, neg_val, neg_test = split_class(neg_list, 0.70, 0.15)

    print("\nDataset Partitioning (70 / 15 / 15):")
    print(f"  Positives (waterlogged)     : Train={len(pos_train)}, Val={len(pos_val)}, Test={len(pos_test)} (Total: {len(pos_list)})")
    print(f"  Negatives (not_waterlogged) : Train={len(neg_train)}, Val={len(neg_val)}, Test={len(neg_test)} (Total: {len(neg_list)})")
    print(f"  Combined Totals             : Train={len(pos_train)+len(neg_train)}, Val={len(pos_val)+len(neg_val)}, Test={len(pos_test)+len(neg_test)} (Grand Total: {len(pos_list)+len(neg_list)})")

    # 4. Prepare target YOLO directories (clean rebuild)
    splits = {
        "train": pos_train + neg_train,
        "val": pos_val + neg_val,
        "test": pos_test + neg_test
    }

    # Backup existing yolo directory to yolo_water_logging_backup if not already backed up
    backup_dir = PROCESSED_DIR / "yolo_water_logging_pre_merge_backup"
    if not backup_dir.exists() and YOLO_DIR.exists():
        shutil.copytree(YOLO_DIR, backup_dir)
        print(f"Created safety backup of pre-merge dataset at {backup_dir}")

    # Recreate clean directories for YOLO
    for s in ["train", "val", "test"]:
        img_s = YOLO_DIR / "images" / s
        lbl_s = YOLO_DIR / "labels" / s
        img_s.mkdir(parents=True, exist_ok=True)
        lbl_s.mkdir(parents=True, exist_ok=True)

        # Clear existing to prevent stale cross-split files
        for f in img_s.glob("*.*"):
            try: f.unlink()
            except: pass
        for f in lbl_s.glob("*.*"):
            try: f.unlink()
            except: pass

    # Also build Classification format directory
    for s in ["train", "val", "test"]:
        for cat in ["waterlogged", "not_waterlogged"]:
            (CLS_DIR / s / cat).mkdir(parents=True, exist_ok=True)

    manifest_records = []
    total_boxes = {"train": 0, "val": 0, "test": 0}

    for s, items in splits.items():
        # Shuffle order within split
        random.shuffle(items)
        for item in items:
            src_img = item["image_path"]
            fname = item["filename"]
            stem = Path(fname).stem
            ext = Path(fname).suffix

            # Destination YOLO paths
            dst_img = YOLO_DIR / "images" / s / fname
            dst_lbl = YOLO_DIR / "labels" / s / f"{stem}.txt"

            # Copy image
            shutil.copy2(src_img, dst_img)

            # Write label
            with open(dst_lbl, "w", encoding="utf-8") as f:
                f.write(item["label_content"].strip() + ("\n" if item["label_content"].strip() else ""))

            # Count bounding boxes
            if item["label_content"].strip():
                boxes = [l for l in item["label_content"].strip().split("\n") if l.strip()]
                total_boxes[s] += len(boxes)
                box_count = len(boxes)
            else:
                box_count = 0

            # Destination Classification path
            dst_cls = CLS_DIR / s / item["category"] / fname
            shutil.copy2(src_img, dst_cls)

            manifest_records.append({
                "filename": fname,
                "split": s,
                "category": item["category"],
                "box_count": box_count,
                "source_path": str(src_img.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "yolo_image_path": str(dst_img.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "yolo_label_path": str(dst_lbl.relative_to(PROJECT_ROOT)).replace("\\", "/")
            })

    # 5. Write data.yaml for YOLOv11
    yaml_config = {
        "path": str(YOLO_DIR.resolve()).replace("\\", "/"),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": 1,
        "names": {
            0: "water_logging"
        }
    }

    yaml_dest = YOLO_DIR / "data.yaml"
    with open(yaml_dest, "w", encoding="utf-8") as f:
        yaml.dump(yaml_config, f, default_flow_style=False, sort_keys=False)
    print(f"\nGenerated unified YOLO data.yaml at {yaml_dest}")

    # Copy to dataset/water_logging/data.yaml for compatibility
    dataset_alias = PROJECT_ROOT / "dataset" / "water_logging"
    dataset_alias.mkdir(parents=True, exist_ok=True)
    with open(dataset_alias / "data.yaml", "w", encoding="utf-8") as f:
        yaml.dump(yaml_config, f, default_flow_style=False, sort_keys=False)

    # 6. Save split manifest
    split_manifest_path = MANIFESTS_DIR / "waterwatch_split_manifest.json"
    with open(split_manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "seed": seed,
            "summary": {
                "total_samples": len(manifest_records),
                "total_waterlogged": len(pos_list),
                "total_not_waterlogged": len(neg_list),
                "splits": {
                    "train": {
                        "total": len(splits["train"]),
                        "waterlogged": len(pos_train),
                        "not_waterlogged": len(neg_train),
                        "bounding_boxes": total_boxes["train"]
                    },
                    "val": {
                        "total": len(splits["val"]),
                        "waterlogged": len(pos_val),
                        "not_waterlogged": len(neg_val),
                        "bounding_boxes": total_boxes["val"]
                    },
                    "test": {
                        "total": len(splits["test"]),
                        "waterlogged": len(pos_test),
                        "not_waterlogged": len(neg_test),
                        "bounding_boxes": total_boxes["test"]
                    }
                }
            },
            "records": manifest_records
        }, f, indent=2)
    print(f"Saved reproducible split manifest at {split_manifest_path}")

    # 7. Write Markdown Report
    rep_path = REPORTS_DIR / "dataset_merge_and_split_report.md"
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write("# WaterWatch AI — Unified Dataset Merge & Split Report (Phase 4)\n\n")
        f.write("## 1. Overview\n")
        f.write("Integrates verified positive waterlogging scenes with verified negative road scenes from IndiaScene365.\n")
        f.write(f"- **Total Dataset Size**: {len(manifest_records)} images\n")
        f.write(f"- **Positive (Waterlogged)**: {len(pos_list)} images (with explicit YOLO bounding boxes)\n")
        f.write(f"- **Negative (Not Waterlogged)**: {len(neg_list)} images (with standard empty YOLO label files)\n")
        f.write(f"- **Partitioning Seed**: {seed}\n\n")

        f.write("## 2. Partitioning Breakdown\n\n")
        f.write("| Split | Waterlogged (Pos) | Not Waterlogged (Neg) | Total Images | Positive Boxes | Class Ratio (Pos:Neg) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        f.write(f"| **Train** | {len(pos_train)} | {len(neg_train)} | {len(splits['train'])} | {total_boxes['train']} | 1 : {len(neg_train)/max(1, len(pos_train)):.2f} |\n")
        f.write(f"| **Validation** | {len(pos_val)} | {len(neg_val)} | {len(splits['val'])} | {total_boxes['val']} | 1 : {len(neg_val)/max(1, len(pos_val)):.2f} |\n")
        f.write(f"| **Held-Out Test** | {len(pos_test)} | {len(neg_test)} | {len(splits['test'])} | {total_boxes['test']} | 1 : {len(neg_test)/max(1, len(pos_test)):.2f} |\n")
        f.write(f"| **Total** | **{len(pos_list)}** | **{len(neg_list)}** | **{len(manifest_records)}** | **{sum(total_boxes.values())}** | **1 : {len(neg_list)/len(pos_list):.2f}** |\n\n")

        f.write("## 3. Storage Formats Generated\n")
        f.write("1. **YOLOv11 Detection Format**: `data/processed/yolo_water_logging/`\n")
        f.write("   - `images/{train,val,test}` and `labels/{train,val,test}`\n")
        f.write("   - Negatives contain clean empty text files to prevent false alarms on dry pavement.\n")
        f.write("2. **Image Classification Format**: `data/processed/classification_water_logging/`\n")
        f.write("   - `{train,val,test}/{waterlogged,not_waterlogged}/` for standard computer vision loaders.\n")

    print(f"Generated merge and split report at {rep_path}")


if __name__ == "__main__":
    merge_datasets()
