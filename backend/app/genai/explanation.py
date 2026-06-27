from app.genai.client import nim_chat


def explain_risk(scan_result: dict) -> str:
    prompt = f"Explain this AI privacy scan result in concise professional language and recommend next actions: {scan_result}"
    result = nim_chat(prompt, max_tokens=500, temperature=0.3)
    if result:
        return result.strip()
    entities = scan_result.get("entities", [])
    if not entities and not scan_result.get("injection_detected"):
        return "No sensitive entities or prompt injection patterns were detected. The content appears safe to share with an AI tool."
    types = ", ".join(sorted({e.get("entity_type", "UNKNOWN") for e in entities})) or "prompt injection"
    return f"This content is rated {scan_result.get('risk_level', 'Unknown')} because it contains {types}. Remove or redact these values before using any external AI tool."
