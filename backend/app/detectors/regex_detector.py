import re

PATTERNS = {
    "API_KEY": [
        r"sk-[a-zA-Z0-9]{20,}",
        r"AIza[0-9A-Za-z\-_]{35}",
        r"AKIA[0-9A-Z]{16}",
        r"ghp_[a-zA-Z0-9]{36}",
        r"github_pat_[a-zA-Z0-9_]{82}",
        r"xox[baprs]-[0-9a-zA-Z]{10,48}",
        r"nvapi-[a-zA-Z0-9\-_]{30,}",
    ],
    "PASSWORD": [r"(?i)password\s*[=:]\s*\S+", r"(?i)passwd\s*[=:]\s*\S+", r"(?i)pwd\s*[=:]\s*\S+", r"(?i)secret\s*[=:]\s*\S+"],
    "DATABASE_URL": [r"mongodb(\+srv)?://[^\s]+", r"postgresql://[^\s]+", r"postgres://[^\s]+", r"mysql://[^\s]+", r"redis://[^\s]+", r"sqlite:///[^\s]+"],
    "PRIVATE_KEY": [r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"],
    "JWT_TOKEN": [r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"],
    "EMAIL": [r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"],
    "PHONE": [r"\b[6-9]\d{9}\b", r"\+?[0-9]{1,3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"],
    "CREDIT_CARD": [r"\b(?:\d[ -]?){13,16}\b"],
    "AADHAR": [r"\b[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}\b"],
    "PAN": [r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"],
    "UNSAFE_COMMAND": [r"rm\s+-rf\s+/", r"(?i)DROP\s+TABLE", r"curl\s+[^\s]+\s*\|\s*bash", r"wget\s+[^\s]+\s*\|\s*sh"],
}

SEVERITY_MAP = {"API_KEY": "critical", "PRIVATE_KEY": "critical", "DATABASE_URL": "critical", "CREDIT_CARD": "critical", "JWT_TOKEN": "high", "PASSWORD": "high", "AADHAR": "high", "PAN": "high", "UNSAFE_COMMAND": "medium", "EMAIL": "low", "PHONE": "low"}
SCORE_MAP = {"critical": 90, "high": 45, "medium": 25, "low": 10}


def detect_all(text: str, tool_risk_score: int = 0) -> dict:
    entities = []
    total_score = 0
    for entity_type, patterns in PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                severity = SEVERITY_MAP[entity_type]
                entities.append({"entity_type": entity_type, "redacted_value": redact_value(match.group(), entity_type), "severity": severity, "confidence": 0.95, "start_index": match.start(), "end_index": match.end()})
                total_score += SCORE_MAP[severity]
    total_score = min(100, total_score + tool_risk_score // 10)
    return {"entities": dedupe_entities(entities), "risk_score": total_score, "risk_level": get_risk_level(total_score), "category": get_category(entities)}


def dedupe_entities(entities: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for entity in entities:
        key = (entity["entity_type"], entity["start_index"], entity["end_index"])
        if key not in seen:
            seen.add(key)
            result.append(entity)
    return result


def redact_value(value: str, entity_type: str) -> str:
    if len(value) <= 8:
        return f"[{entity_type}_REDACTED]"
    return value[:4] + "*" * (len(value) - 8) + value[-4:] + f" [{entity_type}_REDACTED]"


def get_risk_level(score: int) -> str:
    if score == 0:
        return "Safe"
    if score <= 20:
        return "Low"
    if score <= 40:
        return "Medium"
    if score <= 80:
        return "High"
    return "Critical"


def get_category(entities: list) -> str:
    types = [e["entity_type"] for e in entities]
    if any(t in types for t in ["API_KEY", "DATABASE_URL", "PRIVATE_KEY", "JWT_TOKEN", "PASSWORD"]):
        return "Credential Leakage"
    if any(t in types for t in ["EMAIL", "PHONE", "AADHAR", "PAN", "CREDIT_CARD"]):
        return "Personal Information"
    if "UNSAFE_COMMAND" in types:
        return "Unsafe Command"
    return "Safe Content"
