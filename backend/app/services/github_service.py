import shutil
import tempfile
import os
from pathlib import Path

from git import Repo

from app.detectors.regex_detector import detect_all
from app.services.repository_url import normalize_github_repo_url

ALLOWED_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".env", ".json", ".yaml", ".yml", ".md", ".txt", ".ini", ".toml"}
IGNORED_DIRECTORIES = {".git", ".venv", "venv", "node_modules", ".next", "dist", "build", "__pycache__"}


def should_scan_path(path: Path, root: Path, max_file_bytes: int = 1_000_000) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    if any(part in IGNORED_DIRECTORIES for part in relative.parts[:-1]):
        return False
    if path.name != ".env" and path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False
    try:
        return path.is_file() and path.stat().st_size <= max_file_bytes
    except OSError:
        return False


def scan_repository(repo_url: str, *, max_files: int = 5000, max_file_bytes: int = 1_000_000) -> dict:
    repo_url = normalize_github_repo_url(repo_url)
    tmp = Path(tempfile.mkdtemp(prefix="shadowai_repo_"))
    try:
        clone_environment = {
            **os.environ,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_HTTP_LOW_SPEED_LIMIT": "1000",
            "GIT_HTTP_LOW_SPEED_TIME": "30",
        }
        Repo.clone_from(repo_url, tmp, depth=1, env=clone_environment)
        findings = []
        files_scanned = 0
        for path in tmp.rglob("*"):
            if not should_scan_path(path, tmp, max_file_bytes):
                continue
            if files_scanned >= max_files:
                break
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
        repo_name = repo_url.rsplit("/", 1)[-1]
        return {"repo_name": repo_name, "repo_url": repo_url, "files_scanned": files_scanned, "secrets_found": len(findings), "findings": findings, "risk_score": score, "risk_level": level}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
