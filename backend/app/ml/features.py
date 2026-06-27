def text_features(text: str) -> dict:
    lowered = text.lower()
    return {
        "length": len(text),
        "has_secret_words": int(any(w in lowered for w in ["key", "token", "secret", "password", "private"])),
        "has_url": int("://" in text),
        "has_injection_words": int(any(w in lowered for w in ["ignore previous", "jailbreak", "system prompt"])),
    }
