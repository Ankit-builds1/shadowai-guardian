from app.genai.client import nim_chat


def rewrite_safe(original_text: str, entities: list[dict]) -> dict:
    safe_text = original_text
    changes_made = []
    for entity in sorted(entities, key=lambda e: e["start_index"], reverse=True):
        placeholder = f"[{entity['entity_type']}_REDACTED]"
        start, end = entity["start_index"], entity["end_index"]
        safe_text = safe_text[:start] + placeholder + safe_text[end:]
        changes_made.append({"original": entity["redacted_value"], "replaced_with": placeholder, "entity_type": entity["entity_type"]})
    prompt = f"""You are a privacy expert.
This text has already been redacted. Keep all [TYPE_REDACTED] placeholders exactly as they are.
Improve the text to be clearer and more professional while preserving the technical intent.
Return ONLY the improved text. No explanation. No preamble.
Text: {safe_text}"""
    improved = nim_chat(prompt, max_tokens=500, temperature=0.2)
    if improved and "[" in improved and "_REDACTED]" in improved:
        safe_text = improved.strip()
    return {"original_text": original_text, "safe_text": safe_text, "changes_made": list(reversed(changes_made))}
