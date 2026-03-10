"""Dataset ingestion for TerraHerb.

Downloads PlantVillage merged dataset via KaggleHub and syncs it into:
  datasets_substrate/raw/plant_disease_merged
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import kagglehub

KAGGLE_DATASET = "alinedobrovsky/plant-disease-classification-merged-dataset"


def _copytree(src: Path, dst: Path, force: bool = False) -> None:
    if dst.exists() and force:
        shutil.rmtree(dst)
    if dst.exists() and not force:
        raise FileExistsError(f"Target already exists: {dst}. Use --force to overwrite.")
    shutil.copytree(src, dst)


def ingest_dataset(force: bool = False) -> Path:
    project_root = Path(__file__).resolve().parents[2]
    target_dir = project_root / "datasets_substrate" / "raw" / "plant_disease_merged"
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    print("[ingest] Downloading dataset from KaggleHub...")
    download_path = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    print(f"[ingest] Downloaded to cache: {download_path}")

    print(f"[ingest] Syncing to: {target_dir}")
    _copytree(download_path, target_dir, force=force)
    print("[ingest] Done.")
    return target_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and localize PlantVillage dataset")
    parser.add_argument("--force", action="store_true", help="Overwrite existing target directory")
    args = parser.parse_args()
    ingest_dataset(force=args.force)


if __name__ == "__main__":
    main()
