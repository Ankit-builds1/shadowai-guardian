import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from git import Repo

from app.detectors.regex_detector import detect_all

ALLOWED_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".env", ".json", ".yaml", ".yml", ".md", ".txt", ".ini", ".toml"}


def scan_repository(repo_url: str) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="shadowai_repo_"))
    try:
        Repo.clone_from(repo_url, tmp, depth=1)
        findings = []
        files_scanned = 0
        for path in tmp.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS or ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            files_scanned += 1
            for entity in detect_all(text)["entities"]:
                line_number = text[: entity["start_index"]].count("\n") + 1
                findings.append({"file_path": str(path.relative_to(tmp)), "line_number": line_number, **entity})
        score = min(100, sum(40 if f["severity"] == "critical" else 25 if f["severity"] == "high" else 10 for f in findings))
        level = "Critical" if score > 80 else "High" if score > 60 else "Medium" if score > 40 else "Low" if score > 0 else "Safe"
        repo_name = Path(urlparse(repo_url).path).stem or "repository"
        return {"repo_name": repo_name, "repo_url": repo_url, "files_scanned": files_scanned, "secrets_found": len(findings), "findings": findings, "risk_score": score, "risk_level": level}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
