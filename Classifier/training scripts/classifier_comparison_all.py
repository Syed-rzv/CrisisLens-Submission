import joblib
from sklearn.metrics import precision_score, recall_score, f1_score

def load_models():
    return {
        "Naive Bayes": joblib.load("models/classifier_nb.pkl"),
        "Logistic Regression": joblib.load("models/classifier_lr.pkl"),
        "SVM": joblib.load("models/classifier_svm.pkl"),
        "Decision Tree": joblib.load("models/classifier_dt.pkl")
    }

def compare_models():
    models = load_models()

    test_cases = [
        ("Car flipped over on highway, fuel leaking everywhere", "Traffic"),
        ("Elderly person fainted while shopping at the mall", "EMS"),
        ("Kitchen fire spreading quickly through the house", "Fire"),
        ("Motorcycle crash with rider unconscious", "Traffic"),
        ("Explosion reported in apartment basement", "Fire"),
        ("Person trapped in elevator, difficulty breathing", "EMS"),
        ("Gas leak smell reported in residential building", "Fire"),
        ("Massive pileup on the freeway with injuries", "Traffic"),
        ("Man having severe chest pain at the park", "EMS"),
        ("Smoke seen coming from warehouse roof", "Fire")
    ]

    print("MODEL COMPARISON RESULTS WITH CONFIDENCE & METRICS")
    print(f"{'Test Case':<50} | {'Model':<20} | {'Prediction':<10} | {'Confidence':<10} | {'Precision':<8} | {'Recall':<6} | {'F1':<6}")

    for case_text, true_label in test_cases:
        for name, model in models.items():
            pred = model.predict([case_text])[0]
            try:
                proba = max(model.predict_proba([case_text])[0])
            except AttributeError:
                proba = "N/A"
            
            precision = 1.0 if pred == true_label else 0.0
            recall = 1.0 if pred == true_label else 0.0
            f1 = 1.0 if pred == true_label else 0.0

            print(f"{case_text[:49]:<50} | {name:<20} | {pred:<10} | {str(proba):<10} | {precision:<8.2f} | {recall:<6.2f} | {f1:<6.2f}")

if __name__ == "__main__":
    compare_models()
