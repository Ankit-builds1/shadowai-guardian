from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import PromptScan, get_db
from app.genai.report_generator import generate_report
from app.services.report_pdf_service import build_scan_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
async def reports(db: AsyncSession = Depends(get_db)):
    try:
        scans = (await db.execute(select(PromptScan).options(selectinload(PromptScan.entities)).order_by(desc(PromptScan.created_at)).limit(100))).scalars().all()
        return [{
            "id": s.id,
            "created_at": s.created_at,
            "source_type": s.source_type,
            "risk_level": s.risk_level,
            "category": s.category,
            "risk_score": s.risk_score,
            "explanation": s.explanation,
            "entities": [{"entity_type": e.entity_type, "severity": e.severity, "redacted_value": e.redacted_value} for e in s.entities],
            "markdown_report": generate_report({"risk_level": s.risk_level, "risk_score": s.risk_score, "entities": [{"entity_type": e.entity_type, "severity": e.severity, "redacted_value": e.redacted_value} for e in s.entities]}),
        } for s in scans]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reports failed: {exc}") from exc


@router.get("/{scan_id}/pdf")
async def report_pdf(scan_id: int, db: AsyncSession = Depends(get_db)):
    try:
        scan = (await db.execute(
            select(PromptScan)
            .options(selectinload(PromptScan.entities))
            .where(PromptScan.id == scan_id)
        )).scalars().first()
        if scan is None:
            raise HTTPException(status_code=404, detail="Report not found")
        pdf_bytes = build_scan_pdf(scan)
        filename = f"shadowai-report-{scan.id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF report generation failed: {exc}") from exc
