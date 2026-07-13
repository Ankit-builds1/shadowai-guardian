import subprocess
from pathlib import Path

from app.git_guard import _git_command, install_hooks, scan_staged


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repository"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.name", "Test User")
    git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("safe\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "initial")
    return repo


def test_git_commands_allow_a_read_only_docker_mount(tmp_path):
    repo = tmp_path / "mounted-repository"
    assert _git_command(repo, "status") == [
        "git",
        "-c",
        "safe.directory=*",
        "-C",
        str(repo),
        "status",
    ]


def test_install_hooks_preserves_existing_hook(tmp_path):
    repo = make_repo(tmp_path)
    hooks = Path(git(repo, "rev-parse", "--git-path", "hooks"))
    if not hooks.is_absolute():
        hooks = repo / hooks
    existing = hooks / "pre-commit"
    existing.write_text("#!/bin/sh\necho existing\n", encoding="utf-8")

    result = install_hooks(repo)

    assert result["installed"] is True
    assert (hooks / "pre-commit.shadowai-backup").exists()
    assert "docker run" in existing.read_text(encoding="utf-8")


def test_install_hooks_is_idempotent(tmp_path):
    repo = make_repo(tmp_path)
    install_hooks(repo)
    install_hooks(repo)
    hooks = Path(git(repo, "rev-parse", "--git-path", "hooks"))
    if not hooks.is_absolute():
        hooks = repo / hooks
    assert not (hooks / "pre-commit.shadowai-backup.shadowai-backup").exists()


def test_staged_secret_is_blocking_and_redacted(tmp_path):
    repo = make_repo(tmp_path)
    fixture_value = "pass" + "word" + "=" + "SuperSecret123"
    (repo / "config.env").write_text(fixture_value, encoding="utf-8")
    git(repo, "add", "config.env")

    findings = scan_staged(repo)

    assert any(item["blocking"] for item in findings)
    assert findings[0]["file_path"] == "config.env"
    assert fixture_value not in str(findings)


def test_clean_staged_content_has_no_findings(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "notes.txt").write_text("public documentation", encoding="utf-8")
    git(repo, "add", "notes.txt")
    assert scan_staged(repo) == []


def test_non_repository_is_rejected(tmp_path):
    try:
        install_hooks(tmp_path)
    except ValueError as exc:
        assert "Git repository" in str(exc)
    else:
        raise AssertionError("Expected a non-repository to be rejected")
