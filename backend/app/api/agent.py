from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.privacy_agent import run_privacy_agent
from app.core.database import AuditLog, get_db
from app.schemas.scan_schema import AgentRequest

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/analyze")
async def analyze(payload: AgentRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = run_privacy_agent(payload.text)
        db.add(AuditLog(action="agent_analyze", description=f"{result['decision']}: {result['suggested_action']}"))
        await db.commit()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {exc}") from exc


@router.get("/audit")
async def audit(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(10))).scalars().all()
    return [{"id": r.id, "action": r.action, "description": r.description, "created_at": r.created_at} for r in rows]
