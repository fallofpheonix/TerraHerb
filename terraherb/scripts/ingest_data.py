import kagglehub
import shutil
import os
from pathlib import Path

def ingest_dataset():
    """
    Automated ingestion script to fetch and localize the plant disease dataset.
    Downloads to a temp location and moves to data/raw/plant_disease_merged.
    """
    print("🌿 Initiating kagglehub dataset download...")
    
    # 1. Download latest version
    download_path = kagglehub.dataset_download("alinedobrovsky/plant-disease-classification-merged-dataset")
    print(f"✅ Downloaded to temporary cache: {download_path}")
    
    # 2. Define project target
    project_root = Path(__file__).parent.parent.parent
    target_dir = project_root / "data" / "raw" / "plant_disease_merged"
    
    # 3. Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 4. Move/Copy files to project substrate
    print(f"📦 Localizing dataset to: {target_dir}")
    # Note: We use copytree if moving across filesystems or for persistence 
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(download_path, target_dir)
    
    print("🌿 Dataset localized successfully. Ready for training.")

if __name__ == "__main__":
    ingest_dataset()
