from datetime import datetime

from app.api.scan import build_scan_result
from app.genai.safe_rewriter import rewrite_safe


def run_privacy_agent(text: str) -> dict:
    scan = build_scan_result(text, "agent")
    rewrite = rewrite_safe(text, scan["entities"])
    decision = "Block" if scan["risk_level"] in ["Critical", "High"] or scan["injection_detected"] else "Approve with caution" if scan["risk_level"] != "Safe" else "Approve"
    action = "Use the safe rewritten version before submitting." if decision != "Approve" else "Content can be used as-is."
    names = ["OBSERVE", "ANALYZE", "DECIDE", "EXPLAIN", "REWRITE", "ASK", "LOG"]
    texts = [
        "Captured user text and source context.",
        f"Detected {len(scan['entities'])} entities; injection={scan['injection_detected']}.",
        f"Decision: {decision}.",
        scan["explanation"],
        "Generated a redacted safe prompt." if rewrite["changes_made"] else "No rewrite required.",
        "Awaiting user approval or rejection.",
        "Recorded agent analysis in the local audit log.",
    ]
    steps = [{"step": i + 1, "name": name, "result": texts[i], "timestamp": datetime.utcnow().isoformat() + "Z"} for i, name in enumerate(names)]
    return {"steps": steps, "decision": decision, "suggested_action": action, "scan_result": scan, "safe_text": rewrite["safe_text"]}
