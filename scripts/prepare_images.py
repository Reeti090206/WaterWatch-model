"""
WaterWatch AI - Image Dataset Preparation Pipeline
Extracts raw image datasets, fixes train/val/test splits for YOLOv11 object detection,
updates data.yaml with valid paths, and prepares image manifests.
"""

import os
import sys
import shutil
import zipfile
import random
from pathlib import Path
import yaml
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXTRACTED_DIR = DATA_DIR / "extracted"
PROCESSED_IMG_DIR = DATA_DIR / "processed" / "yolo_water_logging"
DATASET_ALIAS_DIR = PROJECT_ROOT / "dataset" / "water_logging"

def find_file(patterns):
    search_dirs = [PROJECT_ROOT, DATA_DIR / "raw", PROJECT_ROOT / "dataset"]
    for pattern in patterns:
        for d in search_dirs:
            matches = list(d.glob(pattern))
            if matches:
                return matches[0]
    return None

def prepare_roboflow_yolo(seed=42):
    print("=" * 60)
    print("PREPARING ROBOFLOW YOLOV11 DATASET")
    print("=" * 60)

    zip_path = find_file(["*water*logging*yolov11*.zip", "*water*logging*.zip"])
    if not zip_path:
        raise FileNotFoundError("Could not find water logging YOLOv11 ZIP archive!")

    print(f"Found archive: {zip_path.name}")
    temp_extract = EXTRACTED_DIR / "roboflow_raw"
    temp_extract.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(temp_extract)
    print(f"Extracted to {temp_extract}")

    # Inspect extracted content
    valid_img_dir = temp_extract / "valid" / "images"
    valid_lbl_dir = temp_extract / "valid" / "labels"

    if not valid_img_dir.exists():
        # Look for images anywhere inside temp_extract
        found_imgs = list(temp_extract.rglob("*.jpg")) + list(temp_extract.rglob("*.png"))
        if not found_imgs:
            raise FileNotFoundError("No images found in extracted Roboflow archive!")
        valid_img_dir = found_imgs[0].parent
        valid_lbl_dir = valid_img_dir.parent / "labels"

    img_files = sorted([f for f in valid_img_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])
    print(f"Found {len(img_files)} source images in {valid_img_dir}")

    # Create target directories
    for split in ['train', 'val', 'test']:
        (PROCESSED_IMG_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (PROCESSED_IMG_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)

    # Shuffle deterministically
    random.seed(seed)
    indices = list(range(len(img_files)))
    random.shuffle(indices)

    n_total = len(img_files)
    n_train = int(n_total * 0.70)
    n_val = int(n_total * 0.20)
    # remaining to test

    train_idx = set(indices[:n_train])
    val_idx = set(indices[n_train:n_train + n_val])
    test_idx = set(indices[n_train + n_val:])

    split_counts = {"train": 0, "val": 0, "test": 0}
    corrupted_count = 0
    box_counts = {"train": 0, "val": 0, "test": 0}

    for i, img_path in enumerate(img_files):
        if i in train_idx:
            split = "train"
        elif i in val_idx:
            split = "val"
        else:
            split = "test"

        # Verify image integrity
        try:
            with Image.open(img_path) as im:
                im.verify()
        except Exception as e:
            print(f"Corrupted image skipped: {img_path.name} ({e})")
            corrupted_count += 1
            continue

        # Destination paths
        dst_img = PROCESSED_IMG_DIR / "images" / split / img_path.name
        shutil.copy2(img_path, dst_img)

        # Corresponding label
        lbl_name = img_path.stem + ".txt"
        src_lbl = valid_lbl_dir / lbl_name
        dst_lbl = PROCESSED_IMG_DIR / "labels" / split / lbl_name

        if src_lbl.exists():
            shutil.copy2(src_lbl, dst_lbl)
            # Count boxes
            with open(src_lbl, "r", encoding="utf-8") as lf:
                boxes = [line for line in lf.read().strip().split("\n") if line.strip()]
                box_counts[split] += len(boxes)
        else:
            # Create empty label file for negative example if label missing
            dst_lbl.touch()

        split_counts[split] += 1

    print("\nDataset split complete:")
    for split in ['train', 'val', 'test']:
        print(f"  {split.upper()}: {split_counts[split]} images, {box_counts[split]} bounding boxes")

    # Generate validated data.yaml
    # We provide forward-slash relative paths from dataset directory
    yaml_config = {
        "path": str(PROCESSED_IMG_DIR.resolve()).replace("\\", "/"),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": 1,
        "names": {0: "water_logging"}
    }

    yaml_dest = PROCESSED_IMG_DIR / "data.yaml"
    with open(yaml_dest, "w", encoding="utf-8") as yf:
        yaml.dump(yaml_config, yf, default_flow_style=False, sort_keys=False)
    print(f"Generated data.yaml at {yaml_dest}")

    # Also write a copy to dataset/ folder for backward-compatibility with user prompts
    DATASET_ALIAS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATASET_ALIAS_DIR / "data.yaml", "w", encoding="utf-8") as yf:
        yaml.dump(yaml_config, yf, default_flow_style=False, sort_keys=False)

    return split_counts, box_counts


def prepare_kaggle_roadway():
    print("\n" + "=" * 60)
    print("PREPARING KAGGLE ROADWAY FLOODING DATASET")
    print("=" * 60)

    zip_path = find_file(["archive.zip", "*kaggle*.zip", "*roadway*.zip"])
    if not zip_path:
        print("Kaggle archive not found, skipping.")
        return

    dest = EXTRACTED_DIR / "kaggle_roadway_flooding"
    dest.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest)

    images = list(dest.rglob("*.jpg"))
    masks = list(dest.rglob("*.png"))
    print(f"Extracted {len(images)} images and {len(masks)} segmentation masks to {dest}")


def main():
    prepare_roboflow_yolo()
    prepare_kaggle_roadway()
    print("\nImage preparation pipeline complete!")


if __name__ == "__main__":
    main()
