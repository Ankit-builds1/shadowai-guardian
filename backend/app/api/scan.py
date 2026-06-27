from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import DetectedEntity, PromptScan, get_db
from app.detectors.injection_detector import detect_injection
from app.detectors.regex_detector import detect_all, get_risk_level
from app.genai.explanation import explain_risk
from app.ml.predict import predict_risk
from app.schemas.scan_schema import PromptScanRequest

router = APIRouter(prefix="/scan", tags=["scan"])


async def persist_prompt_scan(db: AsyncSession, text: str, source_type: str, result: dict) -> int:
    scan = PromptScan(original_text=text, safe_text=result.get("safe_text"), source_type=source_type, category=result["category"], risk_score=result["risk_score"], risk_level=result["risk_level"], explanation=result.get("explanation"), injection_detected=result.get("injection_detected", False), ml_confidence=result.get("ml_confidence"))
    db.add(scan)
    await db.flush()
    for entity in result["entities"]:
        db.add(DetectedEntity(scan_id=scan.id, **entity))
    await db.commit()
    return scan.id


def build_scan_result(text: str, source_type: str = "prompt") -> dict:
    detection = detect_all(text)
    injection = detect_injection(text)
    score = min(100, max(detection["risk_score"], injection.get("injection_risk_score", 0)))
    ml = predict_risk(text)
    score = max(score, ml["score_hint"] if ml["confidence"] > 0.55 else 0)
    result = {**detection, "risk_score": score, "risk_level": get_risk_level(score), "source_type": source_type, "injection_detected": injection["is_injection_attack"], "injection": injection, "ml_confidence": ml["confidence"]}
    result["explanation"] = explain_risk(result)
    return result


@router.post("/prompt")
async def scan_prompt(payload: PromptScanRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = build_scan_result(payload.text, payload.source_type)
        result["scan_id"] = await persist_prompt_scan(db, payload.text, payload.source_type, result)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prompt scan failed: {exc}") from exc

