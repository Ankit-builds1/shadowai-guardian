import json


def exit_code_for_action(action: str) -> int:
    return {"allow": 0, "warn": 1, "block": 2}.get((action or "").lower(), 3)


def render_prompt_result(result: dict, *, as_json: bool = False) -> str:
    if as_json:
        return json.dumps(result, indent=2, default=str, sort_keys=True)
    decision = result.get("policy_decision", {})
    lines = [
        "ShadowAI Guardian",
        "=================",
        f"Action: {str(decision.get('action', 'unknown')).upper()}",
        f"Risk:   {result.get('risk_level', 'Unknown')} ({result.get('risk_score', 0)}/100)",
        f"Policy: {decision.get('policy_mode', 'Developer')}",
    ]
    reasons = decision.get("reasons") or []
    if reasons:
        lines.append("Reasons:")
        lines.extend(f"  - {reason}" for reason in reasons)
    entities = result.get("entities") or []
    if entities:
        lines.append("Findings:")
        for entity in entities:
            lines.append(
                "  - {entity_type} | {severity} | {redacted_value}".format(**entity)
            )
    if result.get("safe_text"):
        lines.extend(["Safe version:", result["safe_text"]])
    return "\n".join(lines)


def render_repository_result(result: dict, *, as_json: bool = False) -> str:
    if as_json:
        return json.dumps(result, indent=2, default=str, sort_keys=True)
    lines = [
        "ShadowAI Repository Scan",
        "========================",
        f"Repository: {result.get('repo_url', '')}",
        f"Files:      {result.get('files_scanned', 0)}",
        f"Findings:   {result.get('secrets_found', 0)}",
        f"Risk:       {result.get('risk_level', 'Unknown')} ({result.get('risk_score', 0)}/100)",
    ]
    for finding in result.get("findings", []):
        lines.append(
            "  - {file_path}:{line_number} | {entity_type} | {severity} | {redacted_value}".format(
                **finding
            )
        )
    return "\n".join(lines)
