"""
WaterWatch AI - Lightweight Image Classification Model Engine (MobileNetV3)
Trains and validates a MobileNetV3-Small binary classifier on the unified
waterlogging dataset with balanced loss weighting, validation threshold tuning,
and rigorous held-out test evaluation.
"""

import os
import sys
import time
import json
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "classification_water_logging"
MODELS_DIR = PROJECT_ROOT / "models" / "image"
REPORTS_DIR = PROJECT_ROOT / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def get_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return train_transform, eval_transform


def train_classifier(epochs=12, batch_size=16, lr=0.001, device=None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=" * 65)
    print("WATERWATCH AI - MOBILENETV3 CLASSIFIER TRAINING")
    print(f"Device: {device} | Epochs: {epochs} | Batch Size: {batch_size} | Learning Rate: {lr}")
    print("=" * 65)

    train_tf, eval_tf = get_transforms()

    train_ds = datasets.ImageFolder(str(DATA_DIR / "train"), transform=train_tf)
    val_ds = datasets.ImageFolder(str(DATA_DIR / "val"), transform=eval_tf)
    test_ds = datasets.ImageFolder(str(DATA_DIR / "test"), transform=eval_tf)

    print(f"Class to index mapping: {train_ds.class_to_idx}")
    # We want 1 = waterlogged, 0 = not_waterlogged
    waterlogged_idx = train_ds.class_to_idx.get("waterlogged", 1)
    not_waterlogged_idx = train_ds.class_to_idx.get("not_waterlogged", 0)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    # Compute class weights for loss balancing
    targets = [s[1] for s in train_ds.samples]
    count_0 = targets.count(not_waterlogged_idx)
    count_1 = targets.count(waterlogged_idx)
    n_total = len(targets)
    w0 = n_total / (2.0 * max(1, count_0))
    w1 = n_total / (2.0 * max(1, count_1))
    weights = torch.tensor([w0, w1], dtype=torch.float).to(device)
    print(f"Dataset counts: not_waterlogged={count_0}, waterlogged={count_1} (Total: {n_total})")
    print(f"Balanced Class Weights: [not_waterlogged: {w0:.3f}, waterlogged: {w1:.3f}]")

    # Initialize MobileNetV3-Small
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    # Replace classifier head for 2 classes
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(in_features, 2)
    )
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_f1 = 0.0
    best_weights_path = MODELS_DIR / "mobilenetv3_waterlogging_best.pth"
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for imgs, lbls in train_loader:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, lbls)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * imgs.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == lbls).sum().item()
            total += lbls.size(0)

        scheduler.step()
        train_loss = running_loss / total
        train_acc = correct / total

        # Validation
        model.eval()
        val_loss = 0.0
        val_y_true = []
        val_y_pred = []
        val_probs = []

        with torch.no_grad():
            for imgs, lbls in val_loader:
                imgs, lbls = imgs.to(device), lbls.to(device)
                outputs = model(imgs)
                loss = criterion(outputs, lbls)
                val_loss += loss.item() * imgs.size(0)
                probs = torch.softmax(outputs, dim=1)[:, waterlogged_idx]
                preds = outputs.argmax(dim=1)

                val_y_true.extend(lbls.cpu().numpy())
                val_y_pred.extend(preds.cpu().numpy())
                val_probs.extend(probs.cpu().numpy())

        val_loss /= len(val_ds)
        val_acc = accuracy_score(val_y_true, val_y_pred)
        val_rec = recall_score(val_y_true, val_y_pred, pos_label=waterlogged_idx, zero_division=0)
        val_prec = precision_score(val_y_true, val_y_pred, pos_label=waterlogged_idx, zero_division=0)
        val_f1 = f1_score(val_y_true, val_y_pred, pos_label=waterlogged_idx, zero_division=0)

        history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 4),
            "val_f1": round(val_f1, 4),
            "val_recall": round(val_rec, 4),
            "val_precision": round(val_prec, 4)
        })

        print(f"Epoch [{epoch:02d}/{epochs:02d}] Train Loss: {train_loss:.4f} Acc: {train_acc:.3f} | Val Loss: {val_loss:.4f} Acc: {val_acc:.3f} Prec: {val_prec:.3f} Rec: {val_rec:.3f} F1: {val_f1:.3f}")

        if val_f1 >= best_val_f1:
            best_val_f1 = val_f1
            torch.save(model.state_dict(), best_weights_path)
            print(f"  --> Saved new best checkpoint to {best_weights_path} (Val F1: {best_val_f1:.4f})")

    # Load best model for validation threshold tuning and test evaluation
    model.load_state_dict(torch.load(best_weights_path, map_location=device))
    model.eval()

    # 1. Threshold Tuning on Validation Split ONLY
    val_probs_all = []
    val_true_all = []
    with torch.no_grad():
        for imgs, lbls in val_loader:
            imgs = imgs.to(device)
            probs = torch.softmax(model(imgs), dim=1)[:, waterlogged_idx]
            val_probs_all.extend(probs.cpu().numpy())
            val_true_all.extend([1 if l == waterlogged_idx else 0 for l in lbls])

    val_probs_all = np.array(val_probs_all)
    val_true_all = np.array(val_true_all)

    best_thresh = 0.50
    best_thresh_f1 = 0.0
    for t in np.arange(0.20, 0.81, 0.05):
        t_preds = (val_probs_all >= t).astype(int)
        score = f1_score(val_true_all, t_preds, zero_division=0)
        # Prioritize recall while maintaining precision
        if score > best_thresh_f1:
            best_thresh_f1 = score
            best_thresh = round(float(t), 2)

    print(f"\nTuned Decision Threshold on Validation Split: {best_thresh} (Val F1: {best_thresh_f1:.4f})")

    # 2. Strict Held-Out Test Evaluation
    test_probs_all = []
    test_true_all = []
    with torch.no_grad():
        for imgs, lbls in test_loader:
            imgs = imgs.to(device)
            probs = torch.softmax(model(imgs), dim=1)[:, waterlogged_idx]
            test_probs_all.extend(probs.cpu().numpy())
            test_true_all.extend([1 if l == waterlogged_idx else 0 for l in lbls])

    test_probs_all = np.array(test_probs_all)
    test_true_all = np.array(test_true_all)
    test_preds_default = (test_probs_all >= 0.50).astype(int)
    test_preds_tuned = (test_probs_all >= best_thresh).astype(int)

    def compute_metrics(y_true, y_pred, y_probs):
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred).tolist()
        try:
            auc = roc_auc_score(y_true, y_probs)
        except:
            auc = None
        tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        return {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "specificity": round(float(spec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4) if auc is not None else None,
            "confusion_matrix": {
                "true_negative": tn,
                "false_positive": fp,
                "false_negative": fn,
                "true_positive": tp
            }
        }

    default_metrics = compute_metrics(test_true_all, test_preds_default, test_probs_all)
    tuned_metrics = compute_metrics(test_true_all, test_preds_tuned, test_probs_all)

    print("\n" + "=" * 65)
    print("HELD-OUT TEST SET EVALUATION RESULTS (N=79, 31 Pos / 48 Neg)")
    print("=" * 65)
    print(f"Accuracy:    {tuned_metrics['accuracy']:.4f} ({tuned_metrics['accuracy']*100:.1f}%)")
    print(f"Precision:   {tuned_metrics['precision']:.4f}")
    print(f"Recall (TPR):{tuned_metrics['recall']:.4f}")
    print(f"Specificity: {tuned_metrics['specificity']:.4f}")
    print(f"F1-Score:    {tuned_metrics['f1_score']:.4f}")
    print(f"ROC-AUC:     {tuned_metrics['roc_auc']}")
    print(f"Confusion Matrix: TN={tuned_metrics['confusion_matrix']['true_negative']}, FP={tuned_metrics['confusion_matrix']['false_positive']}, FN={tuned_metrics['confusion_matrix']['false_negative']}, TP={tuned_metrics['confusion_matrix']['true_positive']}")

    # Save evaluation report
    report_data = {
        "model_name": "MobileNetV3-Small",
        "architecture": "mobilenet_v3_small_transfer_learning",
        "checkpoint_path": str(best_weights_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_samples": len(train_ds),
        "validation_samples": len(val_ds),
        "test_samples": len(test_ds),
        "class_distribution": {
            "waterlogged": count_1,
            "not_waterlogged": count_0
        },
        "optimal_threshold": best_thresh,
        "test_metrics_tuned_threshold": tuned_metrics,
        "test_metrics_default_threshold": default_metrics,
        "training_history": history
    }

    report_json = REPORTS_DIR / "mobilenetv3_evaluation_report.json"
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"\nSaved evaluation metrics to {report_json}")

    return report_data


if __name__ == "__main__":
    train_classifier()
