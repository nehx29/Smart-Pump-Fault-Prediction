import os
import json
import random
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from model import build_model

# --- CONFIGURATION VARIABLES ---
EPOCHS = 75
BATCH_SIZE = 32
LEARNING_RATE = 0.001
RANDOM_SEED = 42

# --- REPRODUCIBILITY SEEDS ---
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, 'dataset', 'processed')
SAVED_MODEL_DIR = os.path.join(BASE_DIR, 'saved_model')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
MODEL_SAVE_PATH = os.path.join(SAVED_MODEL_DIR, 'pump_fault_model.keras')

FEATURE_COLS = ['pressure', 'current', 'vibration']
TARGET_COL = 'label'

def train_dnn():
    print("==============================================================")
    print("      SMART PUMP DNN MODEL TRAINING PIPELINE (PHASE 3)        ")
    print("==============================================================")
    print(f" Random Seed   : {RANDOM_SEED}")
    print(f" Epochs        : {EPOCHS}")
    print(f" Batch Size    : {BATCH_SIZE}")
    print(f" Learning Rate : {LEARNING_RATE}")
    print("--------------------------------------------------------------")

    # 1. Load Processed Datasets
    train_path = os.path.join(PROCESSED_DIR, 'train.csv')
    val_path = os.path.join(PROCESSED_DIR, 'val.csv')

    if not os.path.exists(train_path) or not os.path.exists(val_path):
        raise FileNotFoundError("Processed train/val dataset files missing. Run preprocessing.py first.")

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    X_train = train_df[FEATURE_COLS].values
    y_train = train_df[TARGET_COL].values

    X_val = val_df[FEATURE_COLS].values
    y_val = val_df[TARGET_COL].values

    print(f"[OK] Loaded Training Data   : {X_train.shape[0]} samples")
    print(f"[OK] Loaded Validation Data : {X_val.shape[0]} samples")

    # Load class mapping metadata
    classes_file = os.path.join(SAVED_MODEL_DIR, 'classes.json')
    with open(classes_file, 'r') as f:
        classes_map = json.load(f)

    num_classes = len(classes_map)
    print(f"[OK] Number of Target Classes: {num_classes} ({list(classes_map.values())})\n")

    # 2. Build DNN Model
    model = build_model(input_shape=(3,), num_classes=num_classes, learning_rate=LEARNING_RATE)
    model.summary()

    # 3. Configure Callbacks
    os.makedirs(SAVED_MODEL_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=MODEL_SAVE_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]

    # 4. Train Model
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1
    )

    # Save final model
    model.save(MODEL_SAVE_PATH)
    print(f"\n[OK] Saved trained Keras model to: {MODEL_SAVE_PATH}")

    # 5. Extract and Save Training History
    history_dict = {
        'loss': [float(x) for x in history.history['loss']],
        'val_loss': [float(x) for x in history.history['val_loss']],
        'accuracy': [float(x) for x in history.history['accuracy']],
        'val_accuracy': [float(x) for x in history.history['val_accuracy']]
    }
    
    history_path = os.path.join(RESULTS_DIR, 'training_history.json')
    with open(history_path, 'w') as f:
        json.dump(history_dict, f, indent=2)
    print(f"[OK] Saved training history log to: {history_path}")

    # 6. Plot & Save Curves
    epochs_range = range(1, len(history_dict['accuracy']) + 1)

    # Accuracy Curve
    plt.figure(figsize=(8, 5))
    plt.plot(epochs_range, history_dict['accuracy'], 'b-o', label='Training Accuracy', linewidth=2, markersize=4)
    plt.plot(epochs_range, history_dict['val_accuracy'], 'g-s', label='Validation Accuracy', linewidth=2, markersize=4)
    plt.title('Smart Pump DNN — Training vs Validation Accuracy', fontsize=12, fontweight='bold')
    plt.xlabel('Epochs', fontsize=10)
    plt.ylabel('Accuracy', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='lower right')
    plt.tight_layout()
    acc_curve_path = os.path.join(RESULTS_DIR, 'accuracy_curve.png')
    plt.savefig(acc_curve_path, dpi=300)
    plt.close()
    print(f"[OK] Generated accuracy curve graph: {acc_curve_path}")

    # Loss Curve
    plt.figure(figsize=(8, 5))
    plt.plot(epochs_range, history_dict['loss'], 'r-o', label='Training Loss', linewidth=2, markersize=4)
    plt.plot(epochs_range, history_dict['val_loss'], 'm-s', label='Validation Loss', linewidth=2, markersize=4)
    plt.title('Smart Pump DNN — Training vs Validation Loss', fontsize=12, fontweight='bold')
    plt.xlabel('Epochs', fontsize=10)
    plt.ylabel('Loss', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper right')
    plt.tight_layout()
    loss_curve_path = os.path.join(RESULTS_DIR, 'loss_curve.png')
    plt.savefig(loss_curve_path, dpi=300)
    plt.close()
    print(f"[OK] Generated loss curve graph: {loss_curve_path}")

    # 7. Save Model Info Metadata
    summary_str = []
    model.summary(print_fn=lambda x: summary_str.append(x))
    
    model_info = {
        "model_type": "Deep Neural Network (Sequential DNN)",
        "input_features": FEATURE_COLS,
        "number_of_classes": num_classes,
        "class_names": list(classes_map.values()),
        "training_samples": len(X_train),
        "validation_samples": len(X_val),
        "test_samples": 525,
        "architecture_summary": "\n".join(summary_str),
        "training_configuration": {
            "epochs_total": EPOCHS,
            "epochs_completed": len(history_dict['accuracy']),
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "random_seed": RANDOM_SEED,
            "optimizer": "Adam",
            "loss_function": "sparse_categorical_crossentropy"
        }
    }

    model_info_path = os.path.join(RESULTS_DIR, 'model_info.json')
    with open(model_info_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    print(f"[OK] Saved model info metadata to: {model_info_path}")

    print("==============================================================")
    print("            TRAINING COMPLETED SUCCESSFULLY                   ")
    print("==============================================================\n")

if __name__ == '__main__':
    train_dnn()
