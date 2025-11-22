import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import sys 
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_split import train_test_split_by_title

# Unified training script for all baseline classifiers
# Usage: python classifier_train_unified.py --model [lr|nb|dt|svm]
# Examples:
#   python classifier_train_unified.py --model lr    (Logistic Regression)
#   python classifier_train_unified.py --model nb    (Naive Bayes)
#   python classifier_train_unified.py --model dt    (Decision Tree)
#   python classifier_train_unified.py --model svm   (SVM)

MODEL_CONFIGS = {
    'lr': {
        'name': 'Logistic Regression',
        'estimator': LogisticRegression(class_weight='balanced', max_iter=1000),
        'output': 'models/classifier_lr.pkl' },
    'nb': {
        'name': 'Naive Bayes',
        'estimator': MultinomialNB(),
        'output': 'models/classifier_nb.pkl' },
    'dt': {
        'name': 'Decision Tree',
        'estimator': DecisionTreeClassifier(class_weight='balanced', random_state=42, max_depth=None),
        'output': 'models/classifier_dt.pkl' },
    'svm': {
        'name': 'Support Vector Machine',
        'estimator': LinearSVC(class_weight='balanced', max_iter=5000),
        'output': 'models/classifier_svm.pkl' }
}

def train_classifier(model_type='lr', data_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'cleaned_data.csv')):
    if model_type not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model type: {model_type}. Choose from {list(MODEL_CONFIGS.keys())}")
    
    config = MODEL_CONFIGS[model_type]
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["emergency_title", "emergency_type"])

    print(" DATA CHECK")
    print("Total rows:", len(df))
    print("Unique emergency_titles:", df["emergency_title"].nunique())
    print("Label counts:\n", df["emergency_type"].value_counts())

    X_train, X_test, y_train, y_test = train_test_split_by_title(
        df, text_col="emergency_title", label_col="emergency_type", test_size=0.2, random_state=42)
    
    overlap = set(X_train) & set(X_test)
    print("Train/test overlap:", len(overlap))


    clf = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 3),
            max_features=15000,
            min_df=5 )),
        ("classifier", config['estimator'])
    ])

    print(f"Training {config['name']} model")
    clf.fit(X_train, y_train)

    acc = clf.score(X_test, y_test)
    y_pred = clf.predict(X_test)

    print(f"\n{config['name']} Results:")
    print(f"Validation Accuracy: {acc:.3f}")
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    print("\nConfusion Matrix:")
    print("Predicted ->", clf.classes_)
    for i, true_class in enumerate(clf.classes_):
        print(f"{true_class:>8} | {cm[i]}")

    model_path = config['output']
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(clf, model_path)
    print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Train emergency classification model')
    parser.add_argument('--model', type=str, default='lr', choices=['lr', 'nb', 'dt', 'svm'],
                       help='Model type: lr (Logistic Regression), nb (Naive Bayes), dt (Decision Tree), svm (SVM)')
    parser.add_argument('--data', type=str, default=os.path.join(os.path.dirname(__file__), '..', 'Data', 'cleaned_data.csv'), help='Path to training data')
    
    args = parser.parse_args()
    train_classifier(model_type=args.model, data_path=args.data)