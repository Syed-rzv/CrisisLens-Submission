import pandas as pd
import joblib
import os
from sklearn.metrics import classification_report, accuracy_score

print("Testing model accuracy with and without type prefixes\n")

model_bundle = joblib.load('../models/XGBoost_Combined_MultiJurisdiction.pkl')
model = model_bundle['model']
vect = model_bundle['vect']
le = model_bundle['label_encoder']

print("Model loaded\n")

data_path = os.path.join('..', '..', 'Data', 'cleaned_data.csv')
df = pd.read_csv(data_path)

df = df.sample(n=10000, random_state=42)
df = df[['emergency_title', 'emergency_type']].dropna()
df = df[df['emergency_type'].isin(['EMS', 'Fire', 'Traffic'])]

print(f"Loaded {len(df)} test records\n")

df['original'] = df['emergency_title']
df['stripped'] = df['emergency_title'].str.replace(r'^(EMS|Fire|Traffic):\s*', '', regex=True)

print("Testing with original format (prefixes included)")
X_with = vect.transform(df['original'])
y_pred_with = le.inverse_transform(model.predict(X_with))
y_true = df['emergency_type']

acc_with = accuracy_score(y_true, y_pred_with)
print(f"Accuracy: {acc_with:.4f} ({acc_with*100:.2f}%)\n")

print("Testing without prefixes (stripped format)")
X_without = vect.transform(df['stripped'])
y_pred_without = le.inverse_transform(model.predict(X_without))

acc_without = accuracy_score(y_true, y_pred_without)
print(f"Accuracy: {acc_without:.4f} ({acc_without*100:.2f}%)\n")

print("Results")
print(f"With prefixes:    {acc_with*100:.2f}%")
print(f"Without prefixes: {acc_without*100:.2f}%")
print(f"Difference:       {(acc_with - acc_without)*100:.2f} percentage points\n")

print("Classification report (without prefixes)")
print(classification_report(y_true, y_pred_without, digits=4))

print("\nSample predictions")
print(f"{'Stripped Text':<45} {'True':<8} {'With':<10} {'Without':<12}")

for i in range(min(10, len(df))):
    stripped = df.iloc[i]['stripped'][:43]
    true_label = y_true.iloc[i]
    with_prefix = y_pred_with[i]
    without_prefix = y_pred_without[i]
    
    print(f"{stripped:<45} {true_label:<8} {with_prefix:<10} {without_prefix:<12}")

print("\nTest complete")