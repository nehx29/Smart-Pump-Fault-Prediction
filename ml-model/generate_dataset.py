import numpy as np
import pandas as pd
import os

def generate_pump_dataset(output_path="ml-model/dataset/pump_sensor_dataset.csv", num_samples_per_class=700, seed=42):
    np.random.seed(seed)
    
    data = []
    
    # 1. Normal State
    p_norm = np.random.normal(loc=3.8, scale=0.35, size=num_samples_per_class)
    c_norm = np.random.normal(loc=5.0, scale=0.4, size=num_samples_per_class)
    v_norm = np.random.normal(loc=1.2, scale=0.25, size=num_samples_per_class)
    for p, c, v in zip(p_norm, c_norm, v_norm):
        data.append({
            'pressure': round(float(np.clip(p, 2.5, 4.8)), 2),
            'current': round(float(np.clip(c, 3.5, 6.2)), 2),
            'vibration': round(float(np.clip(v, 0.4, 2.2)), 2),
            'label': 'Normal'
        })
        
    # 2. High Pressure Fault (Discharge Blockage / Restriction)
    p_hp = np.random.normal(loc=6.4, scale=0.45, size=num_samples_per_class)
    c_hp = np.random.normal(loc=6.8, scale=0.5, size=num_samples_per_class)
    v_hp = np.random.normal(loc=2.8, scale=0.35, size=num_samples_per_class)
    for p, c, v in zip(p_hp, c_hp, v_hp):
        data.append({
            'pressure': round(float(np.clip(p, 5.2, 8.0)), 2),
            'current': round(float(np.clip(c, 5.5, 8.5)), 2),
            'vibration': round(float(np.clip(v, 1.8, 4.0)), 2),
            'label': 'High Pressure Fault'
        })

    # 3. Overcurrent Fault (Motor Overload / Stalled Rotor)
    p_oc = np.random.normal(loc=3.3, scale=0.4, size=num_samples_per_class)
    c_oc = np.random.normal(loc=9.6, scale=0.6, size=num_samples_per_class)
    v_oc = np.random.normal(loc=3.4, scale=0.4, size=num_samples_per_class)
    for p, c, v in zip(p_oc, c_oc, v_oc):
        data.append({
            'pressure': round(float(np.clip(p, 2.0, 4.5)), 2),
            'current': round(float(np.clip(c, 8.0, 12.0)), 2),
            'vibration': round(float(np.clip(v, 2.0, 5.0)), 2),
            'label': 'Overcurrent Fault'
        })

    # 4. Excessive Vibration Fault (Bearing Wear / Mechanical Unbalance)
    p_vib = np.random.normal(loc=3.6, scale=0.4, size=num_samples_per_class)
    c_vib = np.random.normal(loc=5.4, scale=0.45, size=num_samples_per_class)
    v_vib = np.random.normal(loc=6.8, scale=0.7, size=num_samples_per_class)
    for p, c, v in zip(p_vib, c_vib, v_vib):
        data.append({
            'pressure': round(float(np.clip(p, 2.4, 4.8)), 2),
            'current': round(float(np.clip(c, 4.0, 7.0)), 2),
            'vibration': round(float(np.clip(v, 4.8, 9.5)), 2),
            'label': 'Excessive Vibration Fault'
        })

    # 5. Combined Fault (Cavitation + Heavy Mechanical Strain)
    p_comb = np.random.normal(loc=1.4, scale=0.3, size=num_samples_per_class)
    c_comb = np.random.normal(loc=8.4, scale=0.55, size=num_samples_per_class)
    v_comb = np.random.normal(loc=7.5, scale=0.8, size=num_samples_per_class)
    for p, c, v in zip(p_comb, c_comb, v_comb):
        data.append({
            'pressure': round(float(np.clip(p, 0.5, 2.4)), 2),
            'current': round(float(np.clip(c, 7.0, 10.5)), 2),
            'vibration': round(float(np.clip(v, 5.5, 10.0)), 2),
            'label': 'Combined Fault'
        })

    df = pd.DataFrame(data)
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} pump sensor samples at {output_path}")
    print("Class distribution:")
    print(df['label'].value_counts())

if __name__ == '__main__':
    generate_pump_dataset()
