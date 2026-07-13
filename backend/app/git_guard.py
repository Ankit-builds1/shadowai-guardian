import os
import stat
import subprocess
from pathlib import Path

from app.detectors.regex_detector import detect_all
from app.services.github_service import ALLOWED_EXTENSIONS, IGNORED_DIRECTORIES


MANAGED_MARKER = "# ShadowAI Guardian managed hook"
DEFAULT_IMAGE = "shadowai-guardian:local"


def _git_command(repo: Path, *args: str) -> list[str]:
    # Bind-mounted repositories are commonly owned by the Windows host user,
    # not the non-root container user. Scope the trust override to this single
    # Git process so Docker-based guards can inspect the selected mount.
    return ["git", "-c", "safe.directory=*", "-C", str(repo), *args]


def _git(repo: Path, *args: str, input_text: str | None = None, check: bool = True) -> str:
    result = subprocess.run(
        _git_command(repo, *args),
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Git command failed")
    return result.stdout


def _require_repository(repo_path: str | Path) -> Path:
    repo = Path(repo_path).expanduser().resolve()
    if not repo.is_dir():
        raise ValueError(f"Git repository directory does not exist: {repo}")
    result = subprocess.run(
        _git_command(repo, "rev-parse", "--show-toplevel"),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"Path is not a Git repository: {repo}")
    return Path(result.stdout.strip()).resolve()


def _supported_relative_path(value: str) -> bool:
    path = Path(value)
    if any(part in IGNORED_DIRECTORIES for part in path.parts[:-1]):
        return False
    return path.name == ".env" or path.suffix.lower() in ALLOWED_EXTENSIONS


def _scan_text(text: str, file_path: str) -> list[dict]:
    findings = []
    for entity in detect_all(text)["entities"]:
        findings.append(
            {
                "file_path": file_path,
                "line_number": text[: entity["start_index"]].count("\n") + 1,
                "entity_type": entity["entity_type"],
                "severity": entity["severity"],
                "redacted_value": entity["redacted_value"],
                "blocking": entity["severity"].lower() in {"critical", "high"},
            }
        )
    return findings


def _scan_git_blobs(repo: Path, revision: str, names: list[str]) -> list[dict]:
    findings = []
    for name in names:
        if not _supported_relative_path(name):
            continue
        content = _git(repo, "show", f"{revision}:{name}", check=False)
        if not content or len(content.encode("utf-8", errors="ignore")) > 1_000_000:
            continue
        findings.extend(_scan_text(content, name))
    return findings


def scan_staged(repo_path: str | Path) -> list[dict]:
    repo = _require_repository(repo_path)
    names = [
        line.strip()
        for line in _git(repo, "diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines()
        if line.strip()
    ]
    return _scan_git_blobs(repo, "", names)


def scan_outgoing(
    repo_path: str | Path,
    remote: str,
    remote_sha: str,
    local_sha: str,
) -> list[dict]:
    repo = _require_repository(repo_path)
    zero = "0" * 40
    if not local_sha or local_sha == zero:
        return []
    if remote_sha and remote_sha != zero:
        commits = _git(repo, "rev-list", f"{remote_sha}..{local_sha}").splitlines()
    else:
        commits = _git(repo, "rev-list", local_sha, "--not", f"--remotes={remote}").splitlines()
    findings = []
    seen: set[tuple] = set()
    for commit in commits:
        names = [
            line.strip()
            for line in _git(
                repo,
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "--diff-filter=ACMR",
                commit,
            ).splitlines()
            if line.strip()
        ]
        for finding in _scan_git_blobs(repo, commit, names):
            key = (
                finding["file_path"],
                finding["line_number"],
                finding["entity_type"],
                finding["redacted_value"],
            )
            if key not in seen:
                seen.add(key)
                findings.append(finding)
    return findings


def _pre_commit_script() -> str:
    return f"""#!/bin/sh
{MANAGED_MARKER}
set -e
HOOK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BACKUP="$HOOK_DIR/pre-commit.shadowai-backup"
if [ -x "$BACKUP" ]; then "$BACKUP" "$@"; fi
if [ "${{SHADOWAI_BYPASS:-0}}" = "1" ]; then
  echo "ShadowAI Guardian bypassed by SHADOWAI_BYPASS=1" >&2
  exit 0
fi
ROOT=$(git rev-parse --show-toplevel)
IMAGE=${{SHADOWAI_IMAGE:-{DEFAULT_IMAGE}}}
MSYS_NO_PATHCONV=1 docker run --rm -i -v "$ROOT:/workspace/repository:ro" "$IMAGE" git-check staged --repo /workspace/repository
"""


def _pre_push_script() -> str:
    return f"""#!/bin/sh
{MANAGED_MARKER}
set -e
INPUT=$(cat)
HOOK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BACKUP="$HOOK_DIR/pre-push.shadowai-backup"
if [ -x "$BACKUP" ]; then printf '%s\n' "$INPUT" | "$BACKUP" "$@"; fi
if [ "${{SHADOWAI_BYPASS:-0}}" = "1" ]; then
  echo "ShadowAI Guardian bypassed by SHADOWAI_BYPASS=1" >&2
  exit 0
fi
ROOT=$(git rev-parse --show-toplevel)
IMAGE=${{SHADOWAI_IMAGE:-{DEFAULT_IMAGE}}}
printf '%s\n' "$INPUT" | MSYS_NO_PATHCONV=1 docker run --rm -i -v "$ROOT:/workspace/repository:ro" "$IMAGE" git-check push --repo /workspace/repository --remote "$1"
"""


def _install_hook(hooks: Path, name: str, content: str) -> None:
    hook = hooks / name
    backup = hooks / f"{name}.shadowai-backup"
    if hook.exists():
        existing = hook.read_text(encoding="utf-8", errors="ignore")
        if MANAGED_MARKER not in existing and not backup.exists():
            hook.replace(backup)
    hook.write_text(content, encoding="utf-8", newline="\n")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def install_hooks(repo_path: str | Path) -> dict:
    repo = _require_repository(repo_path)
    hooks_value = _git(repo, "rev-parse", "--git-path", "hooks").strip()
    hooks = Path(hooks_value)
    if not hooks.is_absolute():
        hooks = repo / hooks
    hooks.mkdir(parents=True, exist_ok=True)
    _install_hook(hooks, "pre-commit", _pre_commit_script())
    _install_hook(hooks, "pre-push", _pre_push_script())
    return {
        "installed": True,
        "hooks_directory": str(hooks),
        "message": (
            f"ShadowAI Git protection installed in {hooks}. "
            "Critical/high findings block commits and pushes. "
            "Set SHADOWAI_BYPASS=1 only for an explicitly reviewed emergency bypass."
        ),
    }


def render_git_findings(findings: list[dict]) -> str:
    if not findings:
        return "ShadowAI Git Guard: no secrets detected"
    lines = ["ShadowAI Git Guard findings:"]
    for finding in findings:
        status = "BLOCK" if finding["blocking"] else "WARN"
        lines.append(
            f"[{status}] {finding['file_path']}:{finding['line_number']} | "
            f"{finding['entity_type']} | {finding['severity']} | {finding['redacted_value']}"
        )
    return "\n".join(lines)
