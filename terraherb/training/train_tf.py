import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
import os

def train_tf_strategy_98():
    """
    High-accuracy 'Strategy 98' training using EfficientNetB0 and Fine-Tuning.
    Targets 97-98% accuracy on the PlantVillage dataset.
    """
    print("🚀 Initializing 'Strategy 98' Pipeline (EfficientNetB0 + Fine-Tuning)...")
    
    # 1. Advanced Data Augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        zoom_range=0.2,
        horizontal_flip=True,
        shear_range=0.2,
        brightness_range=[0.8, 1.2],
        validation_split=0.2
    )

    train_dir = "datasets_substrate/raw/images/color" 
    
    if not os.path.exists(train_dir):
        print(f"⚠️ Training directory {train_dir} not found. Ensure datasets are moved correctly.")
        return

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode="categorical",
        subset='training'
    )

    val_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode="categorical",
        subset='validation'
    )

    # 2. Build Model with Transfer Learning (Stage 1)
    print("🏗️ Building Stage 1: Initial Training of Head Layers...")
    base_model = EfficientNetB0(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False # Freeze backbone

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.3)(x)
    predictions = Dense(train_generator.num_classes, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    # 3. Callbacks
    lr_scheduler = ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=3)
    early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

    # 4. Phase 1 Training
    print("🌿 Phase 1: Training top layers...")
    model.fit(train_generator, 
              validation_data=val_generator, 
              epochs=5, 
              callbacks=[lr_scheduler, early_stop])

    # 5. Phase 2: Fine-Tuning (The 98% Accuracy Trick)
    print("🔥 Phase 2: Initiating Fine-Tuning (Unfreezing last 20 layers)...")
    base_model.trainable = True
    for layer in base_model.layers[:-20]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001), # Very low LR
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.fit(train_generator, 
              validation_data=val_generator, 
              epochs=15, 
              callbacks=[lr_scheduler, early_stop])
    
    os.makedirs("models/saved", exist_ok=True)
    model.save("models/saved/plant_disease_model_strat98.h5")
    print("✅ Strategy 98 model saved to models/saved/plant_disease_model_strat98.h5")

if __name__ == "__main__":
    train_tf_strategy_98()
