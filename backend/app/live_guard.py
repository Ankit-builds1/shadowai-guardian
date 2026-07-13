import time
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from app.detectors.regex_detector import detect_all
from app.services.github_service import should_scan_path as repository_should_scan_path


def should_scan_path(path: Path, root: Path, max_file_bytes: int = 1_000_000) -> bool:
    path = Path(path)
    root = Path(root)
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return repository_should_scan_path(path, root, max_file_bytes)


def scan_file(path: Path, root: Path) -> list[dict]:
    path = Path(path)
    root = Path(root)
    if not should_scan_path(path, root):
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    findings = []
    for entity in detect_all(text)["entities"]:
        findings.append(
            {
                "file_path": path.relative_to(root).as_posix(),
                "line_number": text[: entity["start_index"]].count("\n") + 1,
                "entity_type": entity["entity_type"],
                "severity": entity["severity"],
                "redacted_value": entity["redacted_value"],
                "blocking": entity["severity"].lower() in {"critical", "high"},
            }
        )
    return findings


def format_finding(finding: dict) -> str:
    status = "BLOCK" if finding.get("blocking") else "WARN"
    return (
        f"[{status}] {finding['file_path']}:{finding['line_number']} | "
        f"{finding['entity_type']} | {finding['severity']} | {finding['redacted_value']}"
    )


class LiveGuardHandler(FileSystemEventHandler):
    def __init__(self, root: Path, debounce_seconds: float = 0.35):
        self.root = root
        self.debounce_seconds = debounce_seconds
        self._last_seen: dict[str, float] = {}

    def _scan_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        now = time.monotonic()
        key = str(path.resolve())
        if now - self._last_seen.get(key, 0) < self.debounce_seconds:
            return
        self._last_seen[key] = now
        for finding in scan_file(path, self.root):
            print(format_finding(finding), flush=True)

    def on_created(self, event: FileSystemEvent) -> None:
        self._scan_event(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self._scan_event(event)


def create_observer() -> PollingObserver:
    # Polling works across Docker Desktop and network bind mounts where native
    # Linux inotify events are not forwarded from the host filesystem.
    return PollingObserver(timeout=1.0)


def watch_directory(path: str | Path, *, scan_existing: bool = True) -> int:
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Watch directory does not exist: {root}")
    print(f"ShadowAI Live Guard monitoring: {root}", flush=True)
    print("Only this directory is scanned. Press Ctrl+C to stop.", flush=True)
    if scan_existing:
        for candidate in root.rglob("*"):
            for finding in scan_file(candidate, root):
                print(format_finding(finding), flush=True)
    observer = create_observer()
    observer.schedule(LiveGuardHandler(root), str(root), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        return 0
    finally:
        observer.stop()
        observer.join(timeout=5)
