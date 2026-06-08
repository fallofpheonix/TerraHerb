import os
from pathlib import Path

TARGET_DIR = Path("/Users/fallofpheonix/Project/TerraHerb/datasets_substrate/raw/plant_disease_merged")

def generate():
    classes = []
    for class_dir in sorted(TARGET_DIR.iterdir()):
        if class_dir.is_dir() and "___" in class_dir.name:
            classes.append(class_dir.name)
            
    with open("TerraHerb/terraherb/inference/classes.py", "w") as f:
        f.write('PLANT_CLASSES = [\n')
        for c in classes:
            f.write(f'    "{c}",\n')
        f.write(']\n')
    print(f"Generated {len(classes)} classes.")

if __name__ == "__main__":
    generate()
