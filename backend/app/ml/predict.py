from pathlib import Path

import joblib

from app.ml.train_model import get_model_path, train_model

model = None


def load_model():
    global model
    if model is None:
        model_path = get_model_path()
        if not Path(model_path).exists():
            model = train_model(model_path)
        else:
            model = joblib.load(model_path)
    return model


def predict_risk(text: str) -> dict:
    clf = load_model()
    label = str(clf.predict([text])[0])
    confidence = max(clf.predict_proba([text])[0]) if hasattr(clf, "predict_proba") else 0.7
    score_hint = {"Safe": 0, "Low": 20, "Medium": 50, "High": 75, "Critical": 95}.get(label, 0)
    return {"label": label, "confidence": float(confidence), "score_hint": score_hint}
