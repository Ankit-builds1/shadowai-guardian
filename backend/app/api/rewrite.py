from fastapi import APIRouter, HTTPException

from app.detectors.regex_detector import detect_all
from app.genai.safe_rewriter import rewrite_safe
from app.schemas.scan_schema import RewriteRequest

router = APIRouter(prefix="/rewrite", tags=["rewrite"])


@router.post("")
async def rewrite(payload: RewriteRequest):
    try:
        entities = payload.entities if payload.entities is not None else detect_all(payload.text)["entities"]
        return rewrite_safe(payload.text, entities)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {exc}") from exc
