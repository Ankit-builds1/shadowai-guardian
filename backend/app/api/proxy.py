from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.scan import build_scan_result, persist_prompt_scan
from app.genai.safe_rewriter import rewrite_safe
from app.schemas.scan_schema import ProxyInspectRequest
from app.services.policy_engine import apply_policy
from app.core.database import get_db

router = APIRouter(prefix="/proxy", tags=["proxy"])


@router.post("/inspect")
async def inspect_prompt(payload: ProxyInspectRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = build_scan_result(payload.text, "browser_proxy")
        decision = apply_policy(result, payload.policy_mode)
        safe_text = rewrite_safe(payload.text, result["entities"])["safe_text"] if decision["requires_rewrite"] else ""
        result["safe_text"] = safe_text
        result["policy_decision"] = decision
        result["scan_id"] = await persist_prompt_scan(db, payload.text, "browser_proxy", result)
        return {
            "scan_id": result["scan_id"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "entities": result["entities"],
            "injection_detected": result["injection_detected"],
            "explanation": result["explanation"],
            "safe_text": safe_text,
            "policy_decision": decision,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Proxy inspection failed: {exc}") from exc
