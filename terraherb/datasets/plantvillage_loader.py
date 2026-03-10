"""
PlantVillage PyTorch Dataset and DataLoader factory.

Supports:
  - Train / validation / test splits (stratified by class)
  - Standard data augmentation for training
  - Deterministic transforms for validation/testing
  - Optional class weighting for imbalanced datasets
"""

from __future__ import annotations

import logging
import os
import random
from pathlib import Path
from typing import Optional, Tuple

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import transforms

logger = logging.getLogger(__name__)

# ImageNet statistics used to normalise inputs (matches backbone pre-training)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def _get_train_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.1),
        transforms.RandomRotation(degrees=20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        transforms.RandomErasing(p=0.1, scale=(0.02, 0.1)),
    ])


def _get_eval_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


class PlantVillageDataset(Dataset):
    """
    PyTorch Dataset for the PlantVillage (or merged plant disease) dataset.

    Expected directory structure::

        root_dir/
            Apple___Apple_scab/
                image001.jpg
                image002.jpg
            Apple___healthy/
                ...

    Args:
        root_dir: Path to the dataset root directory.
        transform: Torchvision transform pipeline. If None, the eval transform is used.
        image_extensions: Accepted file extensions (case-insensitive).
    """

    EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}

    def __init__(
        self,
        root_dir: str,
        transform: Optional[transforms.Compose] = None,
        image_extensions: Optional[set[str]] = None,
    ) -> None:
        self.root_dir = Path(root_dir)
        if not self.root_dir.exists():
            raise FileNotFoundError(
                f"Dataset root not found: '{self.root_dir}'. "
                "Run scripts/ingest_data.py to download the dataset."
            )

        self.transform = transform or _get_eval_transform()
        self.extensions = image_extensions or self.EXTENSIONS

        # Discover classes (subdirectory names, sorted for reproducibility)
        self.classes = sorted(
            d.name for d in self.root_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )
        if not self.classes:
            raise RuntimeError(f"No class subdirectories found in '{self.root_dir}'.")

        self.class_to_idx: dict[str, int] = {
            cls: idx for idx, cls in enumerate(self.classes)
        }
        self.samples: list[tuple[str, int]] = self._discover_samples()

        logger.info(
            "PlantVillageDataset: %d classes, %d samples (root='%s')",
            len(self.classes),
            len(self.samples),
            self.root_dir,
        )

    def _discover_samples(self) -> list[tuple[str, int]]:
        """Walk class directories and collect (image_path, class_idx) pairs."""
        samples = []
        for cls_name in self.classes:
            cls_dir = self.root_dir / cls_name
            for img_path in cls_dir.iterdir():
                if img_path.suffix.lower() in self.extensions:
                    samples.append((str(img_path), self.class_to_idx[cls_name]))
        if not samples:
            raise RuntimeError(
                f"No images found in '{self.root_dir}'. "
                "Check that the dataset has been downloaded correctly."
            )
        return samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception as exc:
            logger.warning("Skipping unreadable image '%s': %s", img_path, exc)
            # Return a black image as fallback so the batch doesn't crash
            image = Image.new("RGB", (224, 224), (0, 0, 0))
        return self.transform(image), label

    def class_weights(self) -> torch.Tensor:
        """
        Compute per-class inverse-frequency weights for use with
        WeightedRandomSampler to handle class imbalance.
        """
        counts = [0] * len(self.classes)
        for _, label in self.samples:
            counts[label] += 1
        weights = [1.0 / max(c, 1) for c in counts]
        return torch.tensor(weights, dtype=torch.float32)


def split_dataset(
    dataset: PlantVillageDataset,
    val_fraction: float = 0.15,
    test_fraction: float = 0.10,
    seed: int = 42,
) -> tuple[Dataset, Dataset, Dataset]:
    """
    Perform a stratified split of the dataset into train / val / test subsets.

    Returns:
        (train_dataset, val_dataset, test_dataset)
    """
    from torch.utils.data import Subset

    # Group indices by class for stratified splitting
    class_indices: dict[int, list[int]] = {}
    for idx, (_, label) in enumerate(dataset.samples):
        class_indices.setdefault(label, []).append(idx)

    rng = random.Random(seed)
    train_idx, val_idx, test_idx = [], [], []

    for cls_idxs in class_indices.values():
        rng.shuffle(cls_idxs)
        n = len(cls_idxs)
        n_test = max(1, int(n * test_fraction))
        n_val = max(1, int(n * val_fraction))
        test_idx.extend(cls_idxs[:n_test])
        val_idx.extend(cls_idxs[n_test: n_test + n_val])
        train_idx.extend(cls_idxs[n_test + n_val:])

    logger.info(
        "Split: train=%d, val=%d, test=%d",
        len(train_idx), len(val_idx), len(test_idx),
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx), Subset(dataset, test_idx)


def get_dataloader(
    root_dir: str = "datasets_substrate/raw/plant_disease_merged",
    split: str = "train",
    batch_size: int = 32,
    num_workers: int = 2,
    val_fraction: float = 0.15,
    test_fraction: float = 0.10,
    seed: int = 42,
    use_weighted_sampler: bool = True,
    pin_memory: bool = True,
) -> Optional[DataLoader]:
    """
    Build and return a DataLoader for the requested split.

    Args:
        root_dir: Path to the dataset root.
        split: One of 'train', 'val', 'test'.
        batch_size: Number of samples per batch.
        num_workers: DataLoader worker processes.
        val_fraction: Fraction of data for validation.
        test_fraction: Fraction of data for testing.
        seed: Random seed for reproducibility.
        use_weighted_sampler: Balance class frequencies during training.
        pin_memory: Pin tensors in CPU memory (speeds up GPU transfer).

    Returns:
        A configured DataLoader, or None if root_dir does not exist.
    """
    if not Path(root_dir).exists():
        logger.warning(
            "Dataset root '%s' not found. Run `python -m terraherb.scripts.ingest_data`.",
            root_dir,
        )
        return None

    # Use augmented transforms only for training
    train_transform = _get_train_transform()
    eval_transform = _get_eval_transform()

    full_dataset = PlantVillageDataset(root_dir, transform=eval_transform)
    train_ds, val_ds, test_ds = split_dataset(full_dataset, val_fraction, test_fraction, seed)

    # Apply training transforms to the training subset
    if split == "train":
        full_dataset_aug = PlantVillageDataset(root_dir, transform=train_transform)
        train_ds_aug, _, _ = split_dataset(full_dataset_aug, val_fraction, test_fraction, seed)
        target_ds = train_ds_aug
    elif split == "val":
        target_ds = val_ds
    elif split == "test":
        target_ds = test_ds
    else:
        raise ValueError(f"Invalid split '{split}'. Choose from 'train', 'val', 'test'.")

    sampler = None
    shuffle = split == "train"

    if split == "train" and use_weighted_sampler:
        weights = full_dataset.class_weights()
        sample_weights = torch.tensor(
            [weights[full_dataset.samples[i][1]] for i in train_ds.indices]
        )
        sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)
        shuffle = False  # sampler handles ordering

    return DataLoader(
        target_ds,
        batch_size=batch_size,
        shuffle=shuffle,
        sampler=sampler,
        num_workers=num_workers,
        pin_memory=pin_memory and torch.cuda.is_available(),
        persistent_workers=num_workers > 0,
        drop_last=split == "train",
    )
