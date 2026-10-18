"""
Unit and Integration Tests for WaterWatch AI Image Pipeline
Tests dataset paths, class mappings, split independence, annotation formats, and inference.
"""

import os
import sys
from pathlib import Path
import yaml
import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_IMG_DIR = PROJECT_ROOT / "data" / "processed" / "yolo_water_logging"
DATA_YAML = PROCESSED_IMG_DIR / "data.yaml"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from predict_image import predict


def test_data_yaml_exists_and_valid():
    """Verify data.yaml exists and contains required YOLO keys and class mappings."""
    assert DATA_YAML.exists(), f"data.yaml not found at {DATA_YAML}"
    with open(DATA_YAML, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert "train" in cfg, "Missing 'train' in data.yaml"
    assert "val" in cfg, "Missing 'val' in data.yaml"
    assert "test" in cfg, "Missing 'test' in data.yaml"
    assert cfg.get("nc") == 1, f"Expected 1 class, got {cfg.get('nc')}"
    
    names = cfg.get("names")
    if isinstance(names, dict):
        assert names.get(0) == "water_logging" or names.get("0") == "water_logging"
    elif isinstance(names, list):
        assert names[0] == "water_logging"
    else:
        pytest.fail(f"Invalid names structure in data.yaml: {names}")


def test_splits_non_empty_and_valid():
    """Verify train, val, and test image directories contain images and labels."""
    for split in ["train", "val", "test"]:
        img_dir = PROCESSED_IMG_DIR / "images" / split
        lbl_dir = PROCESSED_IMG_DIR / "labels" / split

        assert img_dir.exists(), f"Image dir {img_dir} does not exist"
        assert lbl_dir.exists(), f"Label dir {lbl_dir} does not exist"

        imgs = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png"))
        lbls = list(lbl_dir.glob("*.txt"))

        assert len(imgs) > 0, f"Split {split} has 0 images"
        assert len(lbls) > 0, f"Split {split} has 0 labels"


def test_no_data_leakage_between_splits():
    """Strictly assert zero image filename overlap between train, val, and test splits."""
    train_imgs = {f.name for f in (PROCESSED_IMG_DIR / "images" / "train").glob("*.*")}
    val_imgs = {f.name for f in (PROCESSED_IMG_DIR / "images" / "val").glob("*.*")}
    test_imgs = {f.name for f in (PROCESSED_IMG_DIR / "images" / "test").glob("*.*")}

    train_val_overlap = train_imgs.intersection(val_imgs)
    train_test_overlap = train_imgs.intersection(test_imgs)
    val_test_overlap = val_imgs.intersection(test_imgs)

    assert len(train_val_overlap) == 0, f"Leakage detected between train and val: {train_val_overlap}"
    assert len(train_test_overlap) == 0, f"Leakage detected between train and test: {train_test_overlap}"
    assert len(val_test_overlap) == 0, f"Leakage detected between val and test: {val_test_overlap}"


def test_yolo_bounding_box_format():
    """Verify bounding box coordinates are normalized in [0, 1] and class ID is 0."""
    lbl_files = list((PROCESSED_IMG_DIR / "labels" / "train").glob("*.txt"))
    assert len(lbl_files) > 0

    checked_boxes = 0
    for lf in lbl_files[:20]:
        with open(lf, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            for line in lines:
                parts = line.split()
                assert len(parts) == 5, f"Invalid YOLO bbox format in {lf.name}: {line}"
                cls_id = int(parts[0])
                xc, yc, w, h = map(float, parts[1:])
                assert cls_id == 0, f"Expected class 0 (water_logging), got {cls_id}"
                assert 0.0 <= xc <= 1.0, f"x_center out of bounds in {lf.name}: {xc}"
                assert 0.0 <= yc <= 1.0, f"y_center out of bounds in {lf.name}: {yc}"
                assert 0.0 < w <= 1.0, f"width out of bounds in {lf.name}: {w}"
                assert 0.0 < h <= 1.0, f"height out of bounds in {lf.name}: {h}"
                checked_boxes += 1

    assert checked_boxes > 0, "No bounding boxes were checked"


def test_predict_image_inference():
    """Verify predict_image runs on a sample image and returns expected dictionary keys."""
    test_img = next((PROCESSED_IMG_DIR / "images" / "test").glob("*.jpg"))
    results = predict(source_path=test_img, conf_thresh=0.25)

    assert isinstance(results, list)
    assert len(results) == 1
    res = results[0]
    assert "image_path" in res
    assert "waterlogging_detected" in res
    assert "detection_count" in res
    assert "detections" in res
    assert "scientific_disclaimer" in res
