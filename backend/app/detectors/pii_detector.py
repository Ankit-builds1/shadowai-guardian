from app.detectors.regex_detector import detect_all


def detect_pii(text: str) -> dict:
    return detect_all(text)
