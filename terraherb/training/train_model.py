"""
Terraherb MobileNetV2 training pipeline.

Features:
  - Two-phase training (head-only → partial fine-tuning)
  - AdamW optimiser with cosine LR schedule
  - Early stopping on validation accuracy
  - Checkpoint saving (best model + latest)
  - Config-driven via YAML (configs/default_training.yaml)
  - Full metrics logging (accuracy, loss per epoch)
"""

from __future__ import annotations

import argparse
import logging
import os
import time
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.optim as optim
import yaml
from torch.optim.lr_scheduler import CosineAnnealingLR

from terraherb.datasets.plantvillage_loader import get_dataloader
from terraherb.models.mobilenet_classifier import MobileNetClassifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH = "configs/default_training.yaml"


def load_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    with open(path, "r") as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def accuracy(outputs: torch.Tensor, labels: torch.Tensor) -> float:
    """Top-1 accuracy as a fraction (0–1)."""
    preds = outputs.argmax(dim=1)
    return (preds == labels).float().mean().item()


def top_k_accuracy(outputs: torch.Tensor, labels: torch.Tensor, k: int = 5) -> float:
    """Top-k accuracy as a fraction (0–1)."""
    _, top_k_preds = outputs.topk(k, dim=1)
    expanded = labels.unsqueeze(1).expand_as(top_k_preds)
    return (top_k_preds == expanded).any(dim=1).float().mean().item()


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

def run_epoch(
    model: nn.Module,
    loader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: Optional[optim.Optimizer] = None,
    phase: str = "train",
) -> dict[str, float]:
    """
    Run a single epoch of training or evaluation.

    Args:
        optimizer: If provided, backprop is performed (training mode).
        phase: 'train' or 'val' — controls model.train() / model.eval().

    Returns:
        dict with keys: loss, top1_acc, top5_acc
    """
    is_train = phase == "train" and optimizer is not None
    model.train(is_train)

    total_loss = 0.0
    total_top1 = 0.0
    total_top5 = 0.0
    n_batches = 0

    with torch.set_grad_enabled(is_train):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)                        # log-softmax
            loss = criterion(outputs, labels)              # NLLLoss

            if is_train:
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

            # For accuracy, convert log-probs → probs
            probs = outputs.exp()
            total_loss += loss.item()
            total_top1 += accuracy(probs, labels)
            total_top5 += top_k_accuracy(probs, labels, k=5)
            n_batches += 1

    return {
        "loss": total_loss / max(n_batches, 1),
        "top1_acc": total_top1 / max(n_batches, 1),
        "top5_acc": total_top5 / max(n_batches, 1),
    }


# ---------------------------------------------------------------------------
# Main training function
# ---------------------------------------------------------------------------

def train(config_path: str = DEFAULT_CONFIG_PATH) -> None:
    """
    Run the full two-phase training pipeline.

    Phase 1: Train the classification head only (backbone frozen).
    Phase 2: Unfreeze the top N backbone layers for deeper fine-tuning.
    """
    cfg = load_config(config_path)
    logger.info("Config loaded from '%s'.", config_path)

    device = torch.device(
        "cuda" if (cfg["training"]["device"] == "cuda" and torch.cuda.is_available()) else "cpu"
    )
    logger.info("🌿 Training on device: %s", device)

    # --- Data ---
    dataset_cfg = cfg["dataset"]
    train_loader = get_dataloader(
        root_dir=dataset_cfg["path"],
        split="train",
        batch_size=dataset_cfg["batch_size"],
        val_fraction=dataset_cfg["val_split"],
        test_fraction=dataset_cfg["test_split"],
    )
    val_loader = get_dataloader(
        root_dir=dataset_cfg["path"],
        split="val",
        batch_size=dataset_cfg["batch_size"],
        val_fraction=dataset_cfg["val_split"],
        test_fraction=dataset_cfg["test_split"],
    )

    if train_loader is None:
        logger.error(
            "Training data not found. Run `python -m terraherb.scripts.ingest_data` first."
        )
        return

    # --- Model ---
    model_cfg = cfg["model"]
    model = MobileNetClassifier(
        num_classes=model_cfg["num_classes"],
        freeze_backbone=True,
        dropout=model_cfg["dropout"],
        pretrained=model_cfg["pretrained"],
    ).to(device)

    param_info = model.count_parameters()
    logger.info("Model params — total: %d | trainable: %d | frozen: %d",
                param_info["total"], param_info["trainable"], param_info["frozen"])

    # --- Loss / Optimiser ---
    criterion = nn.NLLLoss()
    opt_cfg = cfg["optimizer"]
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=opt_cfg["lr"],
        weight_decay=opt_cfg["weight_decay"],
    )

    train_cfg = cfg["training"]
    save_dir = Path(train_cfg["save_dir"])
    save_dir.mkdir(parents=True, exist_ok=True)

    best_val_acc = 0.0
    epochs_no_improve = 0
    history = []

    # ---------------------
    # Phase 1: Head only
    # ---------------------
    logger.info("=== Phase 1: Head-only training ===")
    scheduler = CosineAnnealingLR(optimizer, T_max=train_cfg["epochs"])

    for epoch in range(1, train_cfg["epochs"] + 1):
        t0 = time.perf_counter()
        train_metrics = run_epoch(model, train_loader, criterion, device, optimizer, "train")
        val_metrics = run_epoch(model, val_loader, criterion, device, phase="val")
        scheduler.step()
        epoch_time = time.perf_counter() - t0

        logger.info(
            "Epoch %02d/%02d | "
            "train loss=%.4f acc=%.3f | "
            "val loss=%.4f acc=%.3f top5=%.3f | "
            "%.1fs",
            epoch, train_cfg["epochs"],
            train_metrics["loss"], train_metrics["top1_acc"],
            val_metrics["loss"], val_metrics["top1_acc"], val_metrics["top5_acc"],
            epoch_time,
        )

        row = {"epoch": epoch, "phase": "head", **train_metrics,
               "val_loss": val_metrics["loss"], "val_top1": val_metrics["top1_acc"]}
        history.append(row)

        # Save best model
        if val_metrics["top1_acc"] > best_val_acc:
            best_val_acc = val_metrics["top1_acc"]
            model.save(str(save_dir / "mobilenet_v2_best.pth"))
            logger.info("  ✅ New best val acc: %.4f — checkpoint saved.", best_val_acc)
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= train_cfg["early_stopping"]:
                logger.info("Early stopping at epoch %d.", epoch)
                break

    # ---------------------
    # Phase 2: Fine-tuning
    # ---------------------
    logger.info("=== Phase 2: Fine-tuning last 5 backbone layers ===")
    model.unfreeze_top_layers(n_layers=5)

    # Rebuild optimiser to include newly unfrozen params at a lower LR
    ft_lr = opt_cfg["lr"] / 10
    optimizer_ft = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=ft_lr,
        weight_decay=opt_cfg["weight_decay"],
    )
    scheduler_ft = CosineAnnealingLR(optimizer_ft, T_max=10)
    epochs_no_improve = 0

    for epoch in range(1, 11):  # 10 fine-tuning epochs
        t0 = time.perf_counter()
        train_metrics = run_epoch(model, train_loader, criterion, device, optimizer_ft, "train")
        val_metrics = run_epoch(model, val_loader, criterion, device, phase="val")
        scheduler_ft.step()

        logger.info(
            "FT Epoch %02d/10 | "
            "train loss=%.4f acc=%.3f | "
            "val loss=%.4f acc=%.3f top5=%.3f | %.1fs",
            epoch, train_metrics["loss"], train_metrics["top1_acc"],
            val_metrics["loss"], val_metrics["top1_acc"], val_metrics["top5_acc"],
            time.perf_counter() - t0,
        )

        if val_metrics["top1_acc"] > best_val_acc:
            best_val_acc = val_metrics["top1_acc"]
            model.save(str(save_dir / "mobilenet_v2_best.pth"))
            logger.info("  ✅ New best (fine-tune) val acc: %.4f", best_val_acc)
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= 3:
                logger.info("Fine-tuning early stop at FT epoch %d.", epoch)
                break

    # Save final weights
    model.save(str(save_dir / "mobilenet_v2.pth"))
    logger.info(
        "✅ Training complete. Best val accuracy: %.4f. Weights → '%s'",
        best_val_acc, save_dir,
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Terraherb MobileNetV2 classifier")
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Path to YAML training config (default: configs/default_training.yaml)",
    )
    args = parser.parse_args()
    train(config_path=args.config)
