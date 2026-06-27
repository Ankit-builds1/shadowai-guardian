from datetime import datetime, timedelta
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import DetectedEntity, PromptScan, get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_last_month_score() -> int:
    return 82


def calculate_monthly_privacy_score(scans: list) -> dict:
    now = datetime.now()
    this_month_scans = [s for s in scans if s.created_at.month == now.month and s.created_at.year == now.year]
    counts = {
        "critical": sum(1 for s in this_month_scans if s.risk_level == "Critical"),
        "high": sum(1 for s in this_month_scans if s.risk_level == "High"),
        "medium": sum(1 for s in this_month_scans if s.risk_level == "Medium"),
        "low": sum(1 for s in this_month_scans if s.risk_level == "Low"),
        "safe": sum(1 for s in this_month_scans if s.risk_level == "Safe"),
    }
    score = max(0, min(100, 100 - counts["critical"] * 20 - counts["high"] * 10 - counts["medium"] * 5 - counts["low"] * 2))
    grade_map = [(90, "A", "Excellent privacy habits", "#22c55e"), (75, "B", "Good, room to improve", "#14b8a6"), (50, "C", "Moderate risk behavior", "#eab308"), (25, "D", "High risk habits", "#f97316"), (0, "F", "Critical - leaking secrets regularly", "#ef4444")]
    grade, label, color = "F", "Critical", "#ef4444"
    for threshold, g, l, c in grade_map:
        if score >= threshold:
            grade, label, color = g, l, c
            break
    last_month_score = get_last_month_score()
    improvement = score - last_month_score
    return {"score": score, "grade": grade, "label": label, "color": color, "total_scans_this_month": len(this_month_scans), "counts": counts, "improvement_percent": round(improvement, 1), "trend": "up" if improvement > 0 else "down" if improvement < 0 else "same", "last_month_score": last_month_score}


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    try:
        scans = (await db.execute(select(PromptScan).order_by(desc(PromptScan.created_at)))).scalars().all()
        entities = (await db.execute(select(DetectedEntity))).scalars().all()
        week_ago = datetime.utcnow() - timedelta(days=7)
        distribution = Counter(s.risk_level for s in scans)
        entity_types = Counter(e.entity_type for e in entities)
        total = len(scans)
        return {
            "total_scans": total,
            "critical_alerts": sum(1 for s in scans if s.risk_level == "Critical"),
            "injection_attacks_total": sum(1 for s in scans if s.injection_detected),
            "injection_attacks_this_week": sum(1 for s in scans if s.injection_detected and s.created_at >= week_ago),
            "average_risk_score": round(sum(s.risk_score for s in scans) / total, 1) if total else 0,
            "privacy_amnesia_score": calculate_monthly_privacy_score(scans),
            "risk_distribution": [{"name": name, "value": distribution.get(name, 0)} for name in ["Safe", "Low", "Medium", "High", "Critical"]],
            "entity_breakdown": [{"name": k, "value": v} for k, v in entity_types.items()],
            "recent_scans": [{"id": s.id, "created_at": s.created_at, "source_type": s.source_type, "risk_level": s.risk_level, "category": s.category, "risk_score": s.risk_score} for s in scans[:10]],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Dashboard stats failed: {exc}") from exc
