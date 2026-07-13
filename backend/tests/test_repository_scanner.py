from pathlib import Path
import asyncio

import pytest
from fastapi import HTTPException

from app.services.repository_url import normalize_github_repo_url


def test_accepts_canonical_github_https_url():
    assert (
        normalize_github_repo_url("https://github.com/openai/openai-python/")
        == "https://github.com/openai/openai-python"
    )


def test_strips_git_suffix():
    assert normalize_github_repo_url("https://github.com/openai/openai-python.git") == (
        "https://github.com/openai/openai-python"
    )


@pytest.mark.parametrize(
    "value",
    [
        "file:///etc",
        "git@github.com:a/b.git",
        "https://evil.example/a/b",
        "https://user:pass@github.com/a/b",
        "https://github.com/a",
        "https://github.com/a/b/issues",
        "http://github.com/a/b",
        "https://github.com/a/b?tab=readme",
    ],
)
def test_rejects_unsafe_repository_urls(value):
    with pytest.raises(ValueError):
        normalize_github_repo_url(value)


def test_rejects_invalid_owner_or_repository_characters():
    with pytest.raises(ValueError):
        normalize_github_repo_url("https://github.com/owner name/repo")


def test_scan_file_policy_accepts_dotenv_and_rejects_dependencies(tmp_path):
    from app.services.github_service import should_scan_path

    dotenv = tmp_path / ".env"
    dotenv.write_text("SAFE=value", encoding="utf-8")
    source = tmp_path / "src" / "main.py"
    source.parent.mkdir()
    source.write_text("print('safe')", encoding="utf-8")
    dependency = tmp_path / "node_modules" / "package.json"
    dependency.parent.mkdir()
    dependency.write_text("{}", encoding="utf-8")
    binary = tmp_path / "asset.png"
    binary.write_bytes(b"PNG")

    assert should_scan_path(dotenv, tmp_path)
    assert should_scan_path(source, tmp_path)
    assert not should_scan_path(dependency, tmp_path)
    assert not should_scan_path(binary, tmp_path)


def test_low_findings_do_not_accumulate_into_high_repository_risk():
    from app.services.github_service import summarize_findings

    findings = [
        {"entity_type": "EMAIL", "severity": "low"},
        {"entity_type": "EMAIL", "severity": "low"},
        {"entity_type": "PHONE", "severity": "low"},
    ]

    assert summarize_findings(findings) == {
        "secrets_found": 0,
        "risk_score": 10,
        "risk_level": "Low",
    }


def test_repository_secret_count_only_includes_credentials():
    from app.services.github_service import summarize_findings

    findings = [
        {"entity_type": "EMAIL", "severity": "low"},
        {"entity_type": "API_KEY", "severity": "critical"},
    ]

    assert summarize_findings(findings) == {
        "secrets_found": 1,
        "risk_score": 100,
        "risk_level": "Critical",
    }


def test_api_returns_400_for_invalid_repository_url():
    from app.api.github_scan import scan_github
    from app.schemas.scan_schema import RepoScanRequest

    with pytest.raises(HTTPException) as error:
        asyncio.run(scan_github(RepoScanRequest(repo_url="file:///etc"), db=None))
    assert error.value.status_code == 400
