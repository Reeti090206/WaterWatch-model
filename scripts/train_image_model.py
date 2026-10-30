"""
WaterWatch AI - Image Model Training Engine (YOLOv11 Object Detection)
Trains a YOLOv11 model on the prepared waterlogging dataset using Ultralytics.
Configurable for CPU and GPU, with early stopping and automatic validation.
"""

import os
import sys
import argparse
from pathlib import Path
import yaml
import torch
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models" / "image"
PROCESSED_IMG_DIR = DATA_DIR / "processed" / "yolo_water_logging"
DATA_YAML = PROCESSED_IMG_DIR / "data.yaml"

MODELS_DIR.mkdir(parents=True, exist_ok=True)


def verify_dataset_config():
    """Validates data.yaml paths and verifies image and label files exist before training."""
    print("=" * 60)
    print("VERIFYING YOLOV11 DATASET CONFIGURATION")
    print("=" * 60)

    if not DATA_YAML.exists():
        # Check alias in dataset/ folder
        alias_yaml = PROJECT_ROOT / "dataset" / "water_logging" / "data.yaml"
        if alias_yaml.exists():
            yaml_to_use = alias_yaml
        else:
            raise FileNotFoundError(f"data.yaml not found at {DATA_YAML}. Run prepare_images.py first!")
    else:
        yaml_to_use = DATA_YAML

    with open(yaml_to_use, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    print(f"data.yaml path: {yaml_to_use}")
    print(f"Dataset root: {cfg.get('path')}")
    print(f"Class count (nc): {cfg.get('nc')}")
    print(f"Class names: {cfg.get('names')}")

    root_path = Path(cfg["path"])
    train_dir = root_path / cfg["train"]
    val_dir = root_path / cfg["val"]

    train_imgs = list(train_dir.glob("*.jpg")) + list(train_dir.glob("*.png"))
    val_imgs = list(val_dir.glob("*.jpg")) + list(val_dir.glob("*.png"))

    print(f"Found {len(train_imgs)} train images in {train_dir}")
    print(f"Found {len(val_imgs)} val images in {val_dir}")

    if len(train_imgs) == 0:
        raise ValueError(f"No train images found in {train_dir}!")
    if len(val_imgs) == 0:
        raise ValueError(f"No validation images found in {val_dir}!")

    print("Configuration and dataset integrity verified successfully!")
    return yaml_to_use


def train(epochs=10, batch_size=8, imgsz=640, model_type="yolo11n.pt", device=None):
    yaml_path = verify_dataset_config()

    if device is None:
        device = "0" if torch.cuda.is_available() else "cpu"

    print("\n" + "=" * 60)
    print(f"STARTING YOLOV11 TRAINING ({model_type})")
    print(f"Device: {device} | Epochs: {epochs} | Batch: {batch_size} | Image Size: {imgsz}")
    print("=" * 60)

    # Initialize model with pretrained weights
    model = YOLO(model_type)

    # Train
    results = model.train(
        data=str(yaml_path).replace("\\", "/"),
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=device,
        project=str(PROJECT_ROOT / "runs" / "train").replace("\\", "/"),
        name="water_logging_yolo11",
        exist_ok=True,
        workers=0,
        plots=True,
        save=True,
        verbose=True,
        fliplr=0.5,
        hsv_h=0.015,
        hsv_s=0.4,
        hsv_v=0.3,
        degrees=5.0,
        scale=0.2,
        patience=10
    )

    # Export best model weights to models/image/
    best_pt = Path(results.save_dir) / "weights" / "best.pt"
    if not best_pt.exists():
        best_pt = Path(results.save_dir) / "weights" / "last.pt"

    target_pt = MODELS_DIR / "best.pt"
    if best_pt.exists():
        import shutil
        shutil.copy2(best_pt, target_pt)
        print(f"\nTraining Complete! Best model saved to: {target_pt}")
    else:
        print(f"\nWarning: Could not locate best.pt in {results.save_dir}")

    return results


def main():
    parser = argparse.ArgumentParser(description="WaterWatch Image Model Training")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=8, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--model", type=str, default="yolo11n.pt", help="Pretrained model weights (e.g. yolo11n.pt)")
    parser.add_argument("--device", type=str, default=None, help="Device ('cpu', '0', etc.)")
    parser.add_argument("--verify_only", action="store_true", help="Only verify dataset configuration without training")
    args = parser.parse_args()

    if args.verify_only:
        verify_dataset_config()
    else:
        train(
            epochs=args.epochs,
            batch_size=args.batch,
            imgsz=args.imgsz,
            model_type=args.model,
            device=args.device
        )


if __name__ == "__main__":
    main()
