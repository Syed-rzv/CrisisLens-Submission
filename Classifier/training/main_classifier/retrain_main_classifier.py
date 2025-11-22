import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score


print("RETRAINING MAIN CLASSIFIER WITH NATURAL LANGUAGE")

# Load combined dataset
print("\nLoading combined dataset...")
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'Data', 'montgomery_with_natural_language.csv'))
print(f"Total records: {len(df):,}")

df = df.dropna(subset=['emergency_title', 'emergency_type'])
df = df[df['emergency_type'].isin(['EMS', 'Fire', 'Traffic'])]

print(f"\nAfter cleaning: {len(df):,} records")
print("\nDistribution:")
print(df['emergency_type'].value_counts())

# Train/test split
print("TRAIN/TEST SPLIT")

X = df['emergency_title']
y = df['emergency_type']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {len(X_train):,} records")
print(f"Test: {len(X_test):,} records")

print("TF-IDF VECTORIZATION")

vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    min_df=5,
    max_features=15000,
    strip_accents='unicode',
    lowercase=True
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"Vocabulary size: {len(vectorizer.vocabulary_):,}")

le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

print(f"Classes: {le.classes_}")

# Train XGBoost
print("TRAINING XGBOOST")

model = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)

print("Training model...")
model.fit(X_train_vec, y_train_enc)
print(" Training complete")

# Evaluate
print("EVALUATION")

y_pred_enc = model.predict(X_test_vec)
y_pred = le.inverse_transform(y_pred_enc)
y_test_arr = le.inverse_transform(y_test_enc)

accuracy = accuracy_score(y_test_arr, y_pred)
print(f"\nTest Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

print("\nClassification Report:")
print(classification_report(y_test_arr, y_pred, digits=4))

print("SAVING MODEL")

model_bundle = {
    'model': model,
    'vect': vectorizer,
    'label_encoder': le
}

import shutil
old_model = 'models/XGBoost_Combined_MultiJurisdiction.pkl'
backup_model = 'models/XGBoost_Combined_MultiJurisdiction_OLD.pkl'

try:
    shutil.copy(old_model, backup_model)
    print(f" Backed up old model to: {backup_model}")
except:
    pass

joblib.dump(model_bundle, old_model)
print(f" Saved new model to: {old_model}")

print("MAIN CLASSIFIER RETRAINING COMPLETE")