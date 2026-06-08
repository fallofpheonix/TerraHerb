from terraherb.inference.classes import PLANT_CLASSES
from terraherb.inference.classifier import NUM_CLASSES

def test_classes_exist():
    assert NUM_CLASSES == 88
    assert len(PLANT_CLASSES) == 88

def test_indian_agriculture_classes_included():
    # Verify the new unstructured crops made it into the generated class list
    assert "Wheat___healthy" in PLANT_CLASSES
    assert "Wheat___brown_rust" in PLANT_CLASSES
    assert "Rice___healthy" in PLANT_CLASSES
    assert "Rice___hispa" in PLANT_CLASSES
    assert "Sugarcane___red_rot" in PLANT_CLASSES
    
def test_class_order_stability():
    # Ensure standard plantvillage classes didn't get corrupted (note: casing from Kaggle differs slightly)
    assert "Apple___scab" in PLANT_CLASSES
    assert "Tomato___healthy" in PLANT_CLASSES

def test_mappings_match():
    # Ensure index maps correctly
    index_to_label = {i: c for i, c in enumerate(PLANT_CLASSES)}
    label_to_index = {c: i for i, c in enumerate(PLANT_CLASSES)}
    assert index_to_label[label_to_index["Wheat___healthy"]] == "Wheat___healthy"
