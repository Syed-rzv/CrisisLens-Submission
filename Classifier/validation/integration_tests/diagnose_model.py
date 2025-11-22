import joblib
import numpy as np

print("MODEL DIAGNOSTICS")

model_path = 'models/XGBoost_Combined_MultiJurisdiction.pkl'
print(f"\nLoading: {model_path}")

bundle = joblib.load(model_path)


if isinstance(bundle, dict):
    print("\nKeys in bundle:")
    for key in bundle.keys():
        print(f"  - {key}")
    
    if 'vect' in bundle:
        vectorizer = bundle['vect']
        print(f"\n Vectorizer Vocabulary Size: {len(vectorizer.vocabulary_)}")
        print(f"   Sample vocabulary (first 20 words):")
        vocab_items = list(vectorizer.vocabulary_.items())[:20]
        for word, idx in vocab_items:
            print(f"     '{word}': {idx}")
    
    if 'label_encoder' in bundle:
        le = bundle['label_encoder']
        print(f"\n Label Encoder Classes: {le.classes_}")
        print(f"   Class mapping:")
        for i, label in enumerate(le.classes_):
            print(f"     {i} → {label}")
    
    # Check model
    if 'model' in bundle:
        model = bundle['model']
        print(f"\n Model Type: {type(model).__name__}")
        if hasattr(model, 'n_estimators'):
            print(f"   n_estimators: {model.n_estimators}")
        if hasattr(model, 'max_depth'):
            print(f"   max_depth: {model.max_depth}")

print("TEST PREDICTIONS")

test_titles = [
    "EMS - CARDIAC EMERGENCY",
    "FIRE - BUILDING FIRE",
    "TRAFFIC - VEHICLE ACCIDENT",
    "cardiac arrest patient",
    "structure fire reported",
    "car crash on highway"
]

vectorizer = bundle['vect']
model = bundle['model']
le = bundle['label_encoder']

print("\nTesting predictions on sample titles:")
for title in test_titles:
    vec = vectorizer.transform([title])
    pred_enc = model.predict(vec)[0]
    pred = le.inverse_transform([pred_enc])[0]
    print(f"  '{title}' → {pred}")

print("DIAGNOSIS COMPLETE")