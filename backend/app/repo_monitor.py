import hashlib
import json
import sys
import time
from collections.abc import Callable

from app.cli_format import render_repository_result
from app.services.github_service import scan_repository
from app.services.repository_url import normalize_github_repo_url


def finding_fingerprint(result: dict) -> str:
    stable = sorted(
        (
            item.get("file_path", ""),
            int(item.get("line_number", 0)),
            item.get("entity_type", ""),
            item.get("severity", ""),
            item.get("redacted_value", ""),
        )
        for item in result.get("findings", [])
    )
    encoded = json.dumps(stable, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def monitor_repository(
    repo_url: str,
    interval_seconds: int = 300,
    *,
    scanner: Callable[[str], dict] = scan_repository,
    sleeper: Callable[[float], None] = time.sleep,
    max_cycles: int | None = None,
) -> int:
    repo_url = normalize_github_repo_url(repo_url)
    if not 30 <= interval_seconds <= 86_400:
        raise ValueError("Monitor interval must be between 30 and 86400 seconds")
    print(f"Monitoring {repo_url} every {interval_seconds} seconds. Press Ctrl+C to stop.")
    previous: str | None = None
    cycles = 0
    try:
        while max_cycles is None or cycles < max_cycles:
            try:
                result = scanner(repo_url)
            except Exception as exc:
                print(f"Repository monitor scan failed: {exc}", file=sys.stderr, flush=True)
            else:
                fingerprint = finding_fingerprint(result)
                if previous is None or fingerprint != previous:
                    print(render_repository_result(result), flush=True)
                previous = fingerprint
            cycles += 1
            if max_cycles is None or cycles < max_cycles:
                sleeper(interval_seconds)
    except KeyboardInterrupt:
        print("Repository monitoring stopped.")
    return 0
