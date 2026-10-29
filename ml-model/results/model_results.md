# Smart Pump Fault Prediction — Model Results

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
* **Hold-out Test Samples:** 525 (15%)

---

## 3. Empirical Test Evaluation Results

| Metric | Score |
| :--- | :--- |
| **Test Accuracy** | **100.00%** |
| **Weighted Precision** | **1.0000** |
| **Weighted Recall** | **1.0000** |
| **Weighted F1 Score** | **1.0000** |
| **Test Loss** | **0.000001** |

---

## 4. Per-Class Detailed Performance

```text
                           precision    recall  f1-score   support

           Combined Fault     1.0000    1.0000    1.0000       105
Excessive Vibration Fault     1.0000    1.0000    1.0000       105
      High Pressure Fault     1.0000    1.0000    1.0000       105
                   Normal     1.0000    1.0000    1.0000       105
        Overcurrent Fault     1.0000    1.0000    1.0000       105

                 accuracy                         1.0000       525
                macro avg     1.0000    1.0000    1.0000       525
             weighted avg     1.0000    1.0000    1.0000       525

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
