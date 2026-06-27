import json

from app.genai.client import nim_chat


def generate_report(scan_result: dict) -> str:
    prompt = f"Generate a professional privacy risk report in markdown format. Include: Summary, Risk Level, Detected Entities table, Analysis, Recommendations. Scan data: {json.dumps(scan_result, default=str)}"
    result = nim_chat(prompt, max_tokens=1000, temperature=0.3)
    if result:
        return result.strip()
    entities = scan_result.get("entities", [])
    rows = "\n".join(f"| {e.get('entity_type')} | {e.get('severity')} | {e.get('redacted_value')} |" for e in entities) or "| None | none | - |"
    return f"""# Privacy Risk Report

## Summary
Risk level: **{scan_result.get('risk_level', 'Unknown')}** with score **{scan_result.get('risk_score', 0)}/100**.

## Detected Entities
| Type | Severity | Redacted Value |
| --- | --- | --- |
{rows}

## Analysis
The scan found {len(entities)} sensitive item(s). Prompt injection detected: {scan_result.get('injection_detected', False)}.

## Recommendations
Redact sensitive values, avoid pasting secrets into third-party AI tools, and use the safe rewritten prompt where available.
"""
