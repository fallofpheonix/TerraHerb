import argparse
import os
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Embedded fix for OpenMP issue on macOS
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from terraherb.datasets.plantvillage_loader import get_dataloader
from terraherb.models.mobilenet_classifier import MobileNetClassifier
from terraherb.inference.classes import PLANT_CLASSES

def generate_matrix(fast_dev_run: bool = False):
    print("Loading test dataset...")
    # Get the test split (10%)
    test_loader = get_dataloader(
        root_dir="datasets_substrate/raw/plant_disease_merged",
        split="test",
        batch_size=64,
        num_workers=4
    )
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print("Loading model...")
    model = MobileNetClassifier(num_classes=88, pretrained=False)
    # Note: In a real scenario, we load the trained weights here.
    # If the file doesn't exist, this will evaluate the random initialization.
    weight_path = "models/saved/mobilenet_v2.pth"
    if Path(weight_path).exists():
        model.load_state_dict(torch.load(weight_path, map_location=device))
        print(f"Loaded weights from {weight_path}")
    else:
        print(f"WARNING: Weights not found at {weight_path}. Evaluating random initialization!")
        
    model = model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []
    
    print(f"Evaluating... (fast_dev_run={fast_dev_run})")
    n_batches = 0
    with torch.no_grad():
        for images, labels in test_loader:
            if fast_dev_run and n_batches >= 2:
                break
            images = images.to(device)
            outputs = model(images)
            preds = outputs.argmax(dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())
            n_batches += 1
            
    print("\n--- CLASSIFICATION REPORT ---")
    # For brevity in terminal, just print overall metrics
    report = classification_report(all_labels, all_preds, labels=range(len(PLANT_CLASSES)), target_names=PLANT_CLASSES, output_dict=True, zero_division=0)
    print(f"Macro Avg Precision: {report['macro avg']['precision']:.4f}")
    print(f"Macro Avg Recall:    {report['macro avg']['recall']:.4f}")
    print(f"Macro Avg F1-Score:  {report['macro avg']['f1-score']:.4f}")
    print(f"Overall Accuracy:    {report['accuracy']:.4f}")
    
    # Save the matrix to disk
    cm = confusion_matrix(all_labels, all_preds, labels=range(len(PLANT_CLASSES)))
    np.save("docs/confusion_matrix.npy", cm)
    print("\nSaved full confusion matrix array to docs/confusion_matrix.npy")

if __name__ == "__main__":
    # Ensure working dir is project root
    import os
    os.chdir(Path(__file__).resolve().parents[1])
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast-dev-run", action="store_true", help="Run with just 2 batches to test the pipeline")
    args = parser.parse_args()
    generate_matrix(fast_dev_run=args.fast_dev_run)
