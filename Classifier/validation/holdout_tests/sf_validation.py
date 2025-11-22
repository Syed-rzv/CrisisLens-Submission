import pandas as pd
import joblib
import os
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

model_bundle = joblib.load('models/XGBoost_A_word1-3.pkl')
model = model_bundle['model']
vect = model_bundle['vect']
le = model_bundle.get('label_encoder')

sf = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'Data', 'sf_clean_mapped.csv'))
print(f"Loaded {len(sf)} SF samples")

sf_sample = sf.sample(n=50000, random_state=42)
print(f"Testing on {len(sf_sample)} samples")

X_sf = sf_sample['CallType'].astype(str)
y_sf = sf_sample['emergency_type']

X_sf_vec = vect.transform(X_sf)

y_pred_numeric = model.predict(X_sf_vec)

label_map = {0: 'EMS', 1: 'Fire', 2: 'Traffic'}
y_pred = [label_map.get(p, 'Unknown') for p in y_pred_numeric]

print("\nXGBoost on SF Data")
print(classification_report(y_sf, y_pred, digits=4))

# Confusion matrix
cm = confusion_matrix(y_sf, y_pred, labels=['EMS', 'Fire', 'Traffic'])
print("\nConfusion Matrix:")
print("Predicted -> ['EMS', 'Fire', 'Traffic']")
labels_order = ['EMS', 'Fire', 'Traffic']
for i, true_label in enumerate(labels_order):
    print(f"{true_label:>8} | {cm[i]}")