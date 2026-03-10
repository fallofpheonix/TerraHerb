#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="$ROOT_DIR/datasets_substrate/raw/plant_disease_merged"
UCI_TARGET_DIR="$ROOT_DIR/datasets_substrate/external/uci_plants"

SOURCE_DIR="${1:-$HOME/Downloads/TerraHerb DataSet/plantvillage dataset}"
UCI_SOURCE_DIR="${2:-$HOME/Downloads/TerraHerb DataSet/plants}"

mkdir -p "$ROOT_DIR/datasets_substrate/raw" "$UCI_TARGET_DIR"

if [ -d "$SOURCE_DIR" ]; then
  echo "[relocate] Copying PlantVillage dataset from: $SOURCE_DIR"
  if [ -d "$TARGET_DIR" ]; then
    echo "[relocate] Target exists. Syncing updates..."
    rsync -a --delete "$SOURCE_DIR/" "$TARGET_DIR/"
  else
    rsync -a "$SOURCE_DIR/" "$TARGET_DIR/"
  fi
  echo "[relocate] PlantVillage synced to: $TARGET_DIR"
else
  echo "[relocate] Source not found: $SOURCE_DIR"
fi

if [ -d "$UCI_SOURCE_DIR" ]; then
  echo "[relocate] Copying UCI Plants data from: $UCI_SOURCE_DIR"
  rsync -a "$UCI_SOURCE_DIR/" "$UCI_TARGET_DIR/"
  echo "[relocate] UCI dataset synced to: $UCI_TARGET_DIR"
else
  echo "[relocate] UCI source not found: $UCI_SOURCE_DIR"
fi
