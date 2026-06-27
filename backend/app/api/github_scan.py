from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import RepoFileFinding, RepoScan, get_db
from app.schemas.scan_schema import RepoScanRequest
from app.services.github_service import scan_repository

router = APIRouter(prefix="/scan/github", tags=["github"])


@router.post("")
async def scan_github(payload: RepoScanRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = scan_repository(payload.repo_url)
        repo = RepoScan(repo_name=result["repo_name"], repo_url=result["repo_url"], files_scanned=result["files_scanned"], secrets_found=result["secrets_found"], risk_score=result["risk_score"], risk_level=result["risk_level"])
        db.add(repo)
        await db.flush()
        for finding in result["findings"]:
            db.add(RepoFileFinding(repo_scan_id=repo.id, file_path=finding["file_path"], entity_type=finding["entity_type"], severity=finding["severity"], line_number=finding["line_number"], redacted_value=finding["redacted_value"]))
        await db.commit()
        result["repo_scan_id"] = repo.id
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"GitHub scan failed: {exc}") from exc
