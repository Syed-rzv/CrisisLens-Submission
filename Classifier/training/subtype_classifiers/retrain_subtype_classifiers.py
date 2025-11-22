import pandas as pd
import joblib
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import shutil

print("RETRAINING SUBTYPE CLASSIFIERS WITH NATURAL LANGUAGE")

print("\nLoading combined dataset...")
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'Data', 'montgomery_with_natural_language.csv'))
df = df.dropna(subset=['emergency_title', 'emergency_type', 'emergency_subtype'])
print(f"Total records: {len(df):,}")

print("TRAINING THREE SUBTYPE CLASSIFIERS")

print("1. EMS SUBTYPE CLASSIFIER")

ems_df = df[df['emergency_type'] == 'EMS'].copy()
print(f"\nTotal EMS calls: {len(ems_df):,}")

subtype_counts = ems_df['emergency_subtype'].value_counts()
valid_subtypes = subtype_counts[subtype_counts >= 100].index
ems_df = ems_df[ems_df['emergency_subtype'].isin(valid_subtypes)]

print(f"After filtering (≥100 samples): {len(ems_df):,} calls")
print(f"Number of classes: {ems_df['emergency_subtype'].nunique()}")

X_train_ems, X_test_ems, y_train_ems, y_test_ems = train_test_split(
    ems_df['emergency_title'], 
    ems_df['emergency_subtype'],
    test_size=0.2,
    random_state=42,
    stratify=ems_df['emergency_subtype']
)

print("\nVectorizing...")
vectorizer_ems = TfidfVectorizer(
    min_df=5,
    max_features=15000,
    ngram_range=(1, 3),
    strip_accents='unicode',
    lowercase=True
)

X_train_ems_vec = vectorizer_ems.fit_transform(X_train_ems)
X_test_ems_vec = vectorizer_ems.transform(X_test_ems)

print(f"Vocabulary size: {len(vectorizer_ems.vocabulary_):,}")

le_ems = LabelEncoder()
y_train_ems_enc = le_ems.fit_transform(y_train_ems)
y_test_ems_enc = le_ems.transform(y_test_ems)

print("\nTraining XGBoost...")
model_ems = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)

model_ems.fit(X_train_ems_vec, y_train_ems_enc)

y_pred_ems_enc = model_ems.predict(X_test_ems_vec)
y_pred_ems = le_ems.inverse_transform(y_pred_ems_enc)

accuracy = accuracy_score(y_test_ems, y_pred_ems)
print(f"\ EMS Subtype Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

try:
    shutil.copy('models/XGBoost_EMS_Subtype.pkl', 'models/XGBoost_EMS_Subtype_OLD.pkl')
except:
    pass

ems_bundle = {
    'model': model_ems,
    'vect': vectorizer_ems,
    'label_encoder': le_ems
}
joblib.dump(ems_bundle, 'models/XGBoost_EMS_Subtype.pkl')
print(" Saved: models/XGBoost_EMS_Subtype.pkl")


print("2. FIRE SUBTYPE CLASSIFIER")

fire_df = df[df['emergency_type'] == 'Fire'].copy()
print(f"\nTotal Fire calls: {len(fire_df):,}")

subtype_counts = fire_df['emergency_subtype'].value_counts()
valid_subtypes = subtype_counts[subtype_counts >= 100].index
fire_df = fire_df[fire_df['emergency_subtype'].isin(valid_subtypes)]

print(f"After filtering (≥100 samples): {len(fire_df):,} calls")
print(f"Number of classes: {fire_df['emergency_subtype'].nunique()}")

X_train_fire, X_test_fire, y_train_fire, y_test_fire = train_test_split(
    fire_df['emergency_title'], 
    fire_df['emergency_subtype'],
    test_size=0.2,
    random_state=42,
    stratify=fire_df['emergency_subtype']
)

print("\nVectorizing...")
vectorizer_fire = TfidfVectorizer(
    min_df=5,
    max_features=15000,
    ngram_range=(1, 3),
    strip_accents='unicode',
    lowercase=True
)

X_train_fire_vec = vectorizer_fire.fit_transform(X_train_fire)
X_test_fire_vec = vectorizer_fire.transform(X_test_fire)

print(f"Vocabulary size: {len(vectorizer_fire.vocabulary_):,}")

le_fire = LabelEncoder()
y_train_fire_enc = le_fire.fit_transform(y_train_fire)
y_test_fire_enc = le_fire.transform(y_test_fire)

print("\nTraining XGBoost...")
model_fire = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)

model_fire.fit(X_train_fire_vec, y_train_fire_enc)

y_pred_fire_enc = model_fire.predict(X_test_fire_vec)
y_pred_fire = le_fire.inverse_transform(y_pred_fire_enc)

accuracy = accuracy_score(y_test_fire, y_pred_fire)
print(f"\ Fire Subtype Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

try:
    shutil.copy('models/XGBoost_Fire_Subtype.pkl', 'models/XGBoost_Fire_Subtype_OLD.pkl')
except:
    pass

fire_bundle = {
    'model': model_fire,
    'vect': vectorizer_fire,
    'label_encoder': le_fire
}
joblib.dump(fire_bundle, 'models/XGBoost_Fire_Subtype.pkl')
print(" Saved: models/XGBoost_Fire_Subtype.pkl")


print("3. TRAFFIC SUBTYPE CLASSIFIER")

traffic_df = df[df['emergency_type'] == 'Traffic'].copy()
print(f"\nTotal Traffic calls: {len(traffic_df):,}")

subtype_counts = traffic_df['emergency_subtype'].value_counts()
valid_subtypes = subtype_counts[subtype_counts >= 100].index
traffic_df = traffic_df[traffic_df['emergency_subtype'].isin(valid_subtypes)]

print(f"After filtering (≥100 samples): {len(traffic_df):,} calls")
print(f"Number of classes: {traffic_df['emergency_subtype'].nunique()}")

X_train_traffic, X_test_traffic, y_train_traffic, y_test_traffic = train_test_split(
    traffic_df['emergency_title'], 
    traffic_df['emergency_subtype'],
    test_size=0.2,
    random_state=42,
    stratify=traffic_df['emergency_subtype']
)

print("\nVectorizing...")
vectorizer_traffic = TfidfVectorizer(
    min_df=5,
    max_features=15000,
    ngram_range=(1, 3),
    strip_accents='unicode',
    lowercase=True
)

X_train_traffic_vec = vectorizer_traffic.fit_transform(X_train_traffic)
X_test_traffic_vec = vectorizer_traffic.transform(X_test_traffic)

print(f"Vocabulary size: {len(vectorizer_traffic.vocabulary_):,}")

le_traffic = LabelEncoder()
y_train_traffic_enc = le_traffic.fit_transform(y_train_traffic)
y_test_traffic_enc = le_traffic.transform(y_test_traffic)

print("\nTraining XGBoost...")
model_traffic = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)

model_traffic.fit(X_train_traffic_vec, y_train_traffic_enc)

y_pred_traffic_enc = model_traffic.predict(X_test_traffic_vec)
y_pred_traffic = le_traffic.inverse_transform(y_pred_traffic_enc)

accuracy = accuracy_score(y_test_traffic, y_pred_traffic)
print(f"\ Traffic Subtype Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

try:
    shutil.copy('models/XGBoost_Traffic_Subtype.pkl', 'models/XGBoost_Traffic_Subtype_OLD.pkl')
except:
    pass

traffic_bundle = {
    'model': model_traffic,
    'vect': vectorizer_traffic,
    'label_encoder': le_traffic
}
joblib.dump(traffic_bundle, 'models/XGBoost_Traffic_Subtype.pkl')
print(" Saved: models/XGBoost_Traffic_Subtype.pkl")

print("RETRAINING COMPLETE")
