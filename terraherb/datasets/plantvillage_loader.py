import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import os

class PlantVillageDataset(Dataset):
    """
    Experimental PyTorch Dataset for PlantVillage crop health analysis.
    Maps to the 3.5GB datasets_substrate.
    """
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        # Only include directories (filter out .DS_Store etc.)
        self.classes = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))])
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        self.images = self._load_images()

    def _load_images(self):
        image_paths = []
        for class_name in self.classes:
            class_dir = os.path.join(self.root_dir, class_name)
            for img_name in os.listdir(class_dir):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_paths.append((os.path.join(class_dir, img_name), self.class_to_idx[class_name]))
        return image_paths

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path, label = self.images[idx]
        image = Image.open(img_path).convert("RGB")
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

def get_dataloader(batch_size=32, substrate_path="datasets_substrate/raw/images/color"):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    if not os.path.exists(substrate_path):
        return None
        
    dataset = PlantVillageDataset(substrate_path, transform=transform)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=2)
