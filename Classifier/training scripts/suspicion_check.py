import os
import joblib
import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "XGBoost_B_word1-3_char3-5.pkl")
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data', 'cleaned_data.csv')

df = pd.read_csv(DATA_PATH)

titles = df["emergency_title"].astype(str)  
labels = df["emergency_type"].astype(str)   

le = LabelEncoder()
labels_encoded = le.fit_transform(labels)

bundle = joblib.load(MODEL_PATH)
vectorizer = bundle["vect"]

X = vectorizer.transform(titles)

y_shuffled = shuffle(labels_encoded, random_state=42)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_shuffled, test_size=0.2, random_state=42, stratify=y_shuffled
)

xgb = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    n_jobs=-1,
    random_state=42,
    use_label_encoder=False,
    eval_metric="mlogloss")
    
xgb.fit(X_train, y_train)

y_pred = xgb.predict(X_test)
y_pred_labels = le.inverse_transform(y_pred)
y_test_labels = le.inverse_transform(y_test)

print("Suspicion Check")
print(classification_report(y_test_labels, y_pred_labels))
