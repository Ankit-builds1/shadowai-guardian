from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import ToolRiskScore, get_db
from app.detectors.regex_detector import get_risk_level
from app.schemas.scan_schema import ToolRiskRequest

router = APIRouter(prefix="/tool-risk", tags=["tool-risk"])

KNOWN_TOOLS = {"chat.openai.com": "ChatGPT", "claude.ai": "Claude", "gemini.google.com": "Gemini", "copilot.microsoft.com": "Copilot", "perplexity.ai": "Perplexity", "build.nvidia.com": "NVIDIA NIM"}
SUSPICIOUS_WORDS = ["free-ai-key", "token-grabber", "jailbreak", "prompt-leak", "shadow-login"]


@router.post("")
async def check_tool_risk(payload: ToolRiskRequest, db: AsyncSession = Depends(get_db)):
    try:
        raw = payload.domain.strip()
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
        domain = parsed.netloc.lower() or parsed.path.lower()
        is_https = parsed.scheme == "https"
        known_name = KNOWN_TOOLS.get(domain)
        suspicious = any(word in domain for word in SUSPICIOUS_WORDS)
        score = 5 if known_name else 35
        if not is_https:
            score += 30
        if suspicious:
            score += 45
        score = min(100, score)
        status = "Trusted" if known_name and is_https else "Suspicious" if suspicious or not is_https else "Unknown"
        result = {"domain": domain, "tool_name": known_name, "is_known_tool": bool(known_name), "is_https": is_https, "user_trust_status": status, "risk_score": score, "risk_level": get_risk_level(score), "recommendation": "Use this tool with standard redaction." if status == "Trusted" else "Avoid sharing secrets or personal data until this tool is verified."}
        db.add(ToolRiskScore(**{k: result[k] for k in ["domain", "tool_name", "is_known_tool", "is_https", "user_trust_status", "risk_score", "risk_level"]}))
        await db.commit()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Tool risk check failed: {exc}") from exc
