import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score, 
    precision_recall_fscore_support, 
    confusion_matrix, 
    classification_report
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, 'dataset', 'processed')
SAVED_MODEL_DIR = os.path.join(BASE_DIR, 'saved_model')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
MODEL_PATH = os.path.join(SAVED_MODEL_DIR, 'pump_fault_model.keras')

FEATURE_COLS = ['pressure', 'current', 'vibration']
TARGET_COL = 'label'

def evaluate_dnn():
    print("==============================================================")
    print("      SMART PUMP DNN MODEL EVALUATION PIPELINE (PHASE 3)      ")
    print("==============================================================")

    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Trained model missing at {MODEL_PATH}. Run train.py first.")
        
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"[OK] Loaded Keras model from: {MODEL_PATH}")

    # 2. Load Class Map
    classes_file = os.path.join(SAVED_MODEL_DIR, 'classes.json')
    with open(classes_file, 'r') as f:
        classes_map = json.load(f)
    
    # Ordered list of class names according to index 0..4
    class_names = [classes_map[str(i)] for i in range(len(classes_map))]
    print(f"[OK] Class labels ({len(class_names)}): {class_names}")

    # 3. Load Hold-out Test Dataset
    test_path = os.path.join(PROCESSED_DIR, 'test.csv')
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Processed test dataset missing at {test_path}")

    test_df = pd.read_csv(test_path)
    X_test = test_df[FEATURE_COLS].values
    y_test = test_df[TARGET_COL].values
    print(f"[OK] Loaded Hold-out Test Set : {X_test.shape[0]} samples")

    # 4. Perform Inference on Test Set
    eval_loss, eval_acc = model.evaluate(X_test, y_test, verbose=0)
    
    y_pred_probs = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)

    # 5. Compute Empirical Metrics
    accuracy = float(accuracy_score(y_test, y_pred))
    p_w, r_w, f1_w, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    p_m, r_m, f1_m, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')
    
    cm = confusion_matrix(y_test, y_pred).tolist()
    clf_report_str = classification_report(y_test, y_pred, target_names=class_names, digits=4)

    # Per-class metrics
    p_per, r_per, f1_per, support_per = precision_recall_fscore_support(y_test, y_pred, average=None)
    per_class_dict = {}
    for i, name in enumerate(class_names):
        per_class_dict[name] = {
            "precision": round(float(p_per[i]), 4),
            "recall": round(float(r_per[i]), 4),
            "f1_score": round(float(f1_per[i]), 4),
            "support": int(support_per[i])
        }

    # 6. Save Classification Report Text
    os.makedirs(RESULTS_DIR, exist_ok=True)
    report_path = os.path.join(RESULTS_DIR, 'classification_report.txt')
    with open(report_path, 'w') as f:
        f.write("SMART PUMP FAULT PREDICTION — DNN CLASSIFICATION REPORT\n")
        f.write("========================================================\n\n")
        f.write(clf_report_str)
    print(f"[OK] Saved Classification Report: {report_path}")

    # 7. Plot & Save Confusion Matrix
    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm, 
        annot=True, 
        fmt='d', 
        cmap='Blues', 
        xticklabels=class_names, 
        yticklabels=class_names,
        cbar=True,
        linewidths=1,
        linecolor='white'
    )
    plt.title('Smart Pump DNN Classifier — Test Set Confusion Matrix', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Predicted Label', fontsize=10, labelpad=10)
    plt.ylabel('Actual (True) Label', fontsize=10, labelpad=10)
    plt.xticks(rotation=25, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    
    cm_path = os.path.join(RESULTS_DIR, 'confusion_matrix.png')
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[OK] Saved Confusion Matrix Graph: {cm_path}")

    # 8. Save Evaluation Results JSON
    eval_json = {
        "test_loss": round(float(eval_loss), 6),
        "test_accuracy": round(accuracy, 4),
        "weighted_precision": round(float(p_w), 4),
        "weighted_recall": round(float(r_w), 4),
        "weighted_f1_score": round(float(f1_w), 4),
        "macro_precision": round(float(p_m), 4),
        "macro_recall": round(float(r_m), 4),
        "macro_f1_score": round(float(f1_m), 4),
        "total_test_samples": len(y_test),
        "confusion_matrix": cm,
        "class_labels": class_names,
        "per_class_metrics": per_class_dict
    }

    eval_json_path = os.path.join(RESULTS_DIR, 'evaluation_results.json')
    with open(eval_json_path, 'w') as f:
        json.dump(eval_json, f, indent=2)
    print(f"[OK] Saved Evaluation Metrics JSON: {eval_json_path}")

    # 9. Save Summary Markdown Document (model_results.md)
    md_content = f"""# Smart Pump Fault Prediction — Model Results

**Project:** Smart Pump Fault Prediction — Industrial Pump Condition Monitoring  
**Domain:** Predictive Maintenance — Sensor-Driven Fault Classification  

---

## 1. Model Configuration

* **Model Type:** Deep Neural Network (Sequential DNN)
* **Input Features:** Pressure (bar), Current (A), Vibration (mm/s)
* **Output Classes (5):**
  1. Normal
  2. High Pressure Fault
  3. Overcurrent Fault
  4. Excessive Vibration Fault
  5. Combined Fault

---

## 2. Sample Distribution

* **Training Samples:** 2,450 (70%)
* **Validation Samples:** 525 (15%)
* **Hold-out Test Samples:** {len(y_test)} (15%)

---

## 3. Empirical Test Evaluation Results

| Metric | Score |
| :--- | :--- |
| **Test Accuracy** | **{accuracy * 100:.2f}%** |
| **Weighted Precision** | **{p_w:.4f}** |
| **Weighted Recall** | **{r_w:.4f}** |
| **Weighted F1 Score** | **{f1_w:.4f}** |
| **Test Loss** | **{eval_loss:.6f}** |

---

## 4. Per-Class Detailed Performance

```text
{clf_report_str}
```

---

## 5. Artifacts Generated

* Saved Model: `ml-model/saved_model/pump_fault_model.keras`
* Accuracy Curve: `ml-model/results/accuracy_curve.png`
* Loss Curve: `ml-model/results/loss_curve.png`
* Confusion Matrix: `ml-model/results/confusion_matrix.png`
* Evaluation Metrics: `ml-model/results/evaluation_results.json`
* Classification Report: `ml-model/results/classification_report.txt`
* Model Info: `ml-model/results/model_info.json`
"""

    md_path = os.path.join(RESULTS_DIR, 'model_results.md')
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"[OK] Saved Model Results Summary Markdown: {md_path}")

    print("\n==============================================================")
    print(f" EMPIRICAL TEST ACCURACY: {accuracy * 100:.2f}% | F1-SCORE: {f1_w:.4f} ")
    print("==============================================================\n")

    return eval_json

if __name__ == '__main__':
    evaluate_dnn()
