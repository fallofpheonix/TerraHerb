import os
import shutil
from pathlib import Path
from collections import defaultdict

CACHE_DIR = Path("/Users/fallofpheonix/.cache/kagglehub/datasets/alinedobrovsky/plant-disease-classification-merged-dataset/versions/1")
TARGET_DIR = Path("/Users/fallofpheonix/Project/TerraHerb/datasets_substrate/raw/plant_disease_merged")

def standardize_and_copy():
    print(f"Scanning {CACHE_DIR} for double-underscore formats...")
    
    # 1. Find all Crop__Disease folders
    for d in CACHE_DIR.iterdir():
        if d.is_dir() and "__" in d.name and "___" not in d.name:
            crop, disease = d.name.split("__", 1)
            # Standardize to Crop___Disease
            new_name = f"{crop}___{disease}"
            target_path = TARGET_DIR / new_name
            
            print(f"Migrating: {d.name} -> {new_name}")
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(d, target_path)

def audit_dataset():
    print("\n--- DATASET AUDIT ---")
    stats = defaultdict(int)
    total_images = 0
    
    for class_dir in sorted(TARGET_DIR.iterdir()):
        if class_dir.is_dir() and "___" in class_dir.name:
            count = len(list(class_dir.glob("*.*")))
            stats[class_dir.name] = count
            total_images += count
            
    print(f"{'Class Name':<50} | {'Image Count':<10}")
    print("-" * 65)
    for class_name, count in stats.items():
        print(f"{class_name:<50} | {count:<10}")
        
    print("-" * 65)
    print(f"Total Classes: {len(stats)}")
    print(f"Total Images: {total_images}")

if __name__ == "__main__":
    standardize_and_copy()
    audit_dataset()
