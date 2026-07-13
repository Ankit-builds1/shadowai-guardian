from app.api.scan import build_scan_result


def test_ml_only_prediction_cannot_block_clean_text(monkeypatch):
    monkeypatch.setattr(
        "app.api.scan.predict_risk",
        lambda _text: {"label": "Critical", "confidence": 0.99, "score_hint": 95},
    )

    result = build_scan_result("Explain local API rate limiting.")

    assert result["entities"] == []
    assert result["injection_detected"] is False
    assert result["risk_score"] <= 20
