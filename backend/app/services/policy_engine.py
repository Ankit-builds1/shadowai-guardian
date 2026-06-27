POLICIES = {
    "student": {
        "label": "Student",
        "block_at": 90,
        "warn_at": 45,
        "block_secret_severities": ["Critical"],
    },
    "developer": {
        "label": "Developer",
        "block_at": 85,
        "warn_at": 40,
        "block_secret_severities": ["Critical"],
    },
    "company": {
        "label": "Company",
        "block_at": 75,
        "warn_at": 35,
        "block_secret_severities": ["Critical", "High"],
    },
    "strict": {
        "label": "Strict Compliance",
        "block_at": 60,
        "warn_at": 25,
        "block_secret_severities": ["Critical", "High"],
    },
}


def normalize_policy_mode(mode: str | None) -> str:
    key = (mode or "developer").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "strict_compliance": "strict",
        "compliance": "strict",
        "enterprise": "company",
        "default": "developer",
    }
    return aliases.get(key, key if key in POLICIES else "developer")


def apply_policy(scan_result: dict, mode: str | None = "developer") -> dict:
    policy_key = normalize_policy_mode(mode)
    policy = POLICIES[policy_key]
    risk_score = int(scan_result.get("risk_score", 0))
    entities = scan_result.get("entities", [])
    injection_detected = bool(scan_result.get("injection_detected", False))
    blocked_severities = {severity.lower() for severity in policy["block_secret_severities"]}
    blocking_entities = [
        entity for entity in entities
        if str(entity.get("severity", "")).lower() in blocked_severities
    ]

    reasons: list[str] = []
    if blocking_entities:
        entity_types = ", ".join(sorted({entity.get("entity_type", "secret") for entity in blocking_entities}))
        reasons.append(f"{entity_types} matched protected data rules")
    if injection_detected:
        reasons.append("Prompt injection behavior was detected")
    if risk_score >= policy["block_at"]:
        reasons.append(f"Risk score {risk_score} meets the block threshold {policy['block_at']}")

    if reasons:
        action = "block"
    elif risk_score >= policy["warn_at"] or scan_result.get("risk_level") in {"Medium", "High", "Critical"}:
        action = "warn"
        reasons.append(f"Risk score {risk_score} meets the warning threshold {policy['warn_at']}")
    else:
        action = "allow"
        reasons.append("No protected data or high-risk behavior matched this policy")

    return {
        "policy_mode": policy["label"],
        "policy_key": policy_key,
        "action": action,
        "requires_rewrite": action == "block" or bool(blocking_entities),
        "reasons": reasons,
        "block_threshold": policy["block_at"],
        "warn_threshold": policy["warn_at"],
    }
