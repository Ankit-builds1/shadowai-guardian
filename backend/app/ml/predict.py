from pathlib import Path

import joblib

from app.ml.train_model import MODEL_PATH, train_model

model = None


def load_model():
    global model
    if model is None:
        if not Path(MODEL_PATH).exists():
            model = train_model()
        else:
            model = joblib.load(MODEL_PATH)
        print("ML model loaded successfully")
    return model


def predict_risk(text: str) -> dict:
    clf = load_model()
    label = str(clf.predict([text])[0])
    confidence = max(clf.predict_proba([text])[0]) if hasattr(clf, "predict_proba") else 0.7
    score_hint = {"Safe": 0, "Low": 20, "Medium": 50, "High": 75, "Critical": 95}.get(label, 0)
    return {"label": label, "confidence": float(confidence), "score_hint": score_hint}
