from pathlib import Path

from app.live_guard import scan_file, should_scan_path
from watchdog.observers.polling import PollingObserver


def test_ignores_dependencies_and_binary_files(tmp_path):
    dependency = tmp_path / "node_modules" / "a.js"
    dependency.parent.mkdir()
    dependency.write_text("password" + "=" + "hidden", encoding="utf-8")
    binary = tmp_path / "image.png"
    binary.write_bytes(b"PNG")

    assert not should_scan_path(dependency, tmp_path)
    assert not should_scan_path(binary, tmp_path)


def test_scans_changed_text_without_returning_secret(tmp_path):
    path = tmp_path / "config.env"
    fixture_value = "pass" + "word" + "=" + "SuperSecret123"
    path.write_text(fixture_value, encoding="utf-8")

    findings = scan_file(path, tmp_path)

    assert findings[0]["entity_type"] == "PASSWORD"
    assert findings[0]["file_path"] == "config.env"
    assert findings[0]["line_number"] == 1
    assert fixture_value not in str(findings)


def test_reports_correct_line_number(tmp_path):
    path = tmp_path / "settings.txt"
    path.write_text("safe\nemail@example.com\n", encoding="utf-8")

    findings = scan_file(path, tmp_path)

    assert findings[0]["line_number"] == 2


def test_oversized_file_is_ignored(tmp_path):
    path = tmp_path / "large.txt"
    path.write_bytes(b"x" * (1_000_001))
    assert not should_scan_path(path, tmp_path)
    assert scan_file(path, tmp_path) == []


def test_path_outside_root_is_ignored(tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("password" + "=" + "SuperSecret123", encoding="utf-8")
    try:
        assert not should_scan_path(outside, tmp_path)
        assert scan_file(outside, tmp_path) == []
    finally:
        outside.unlink(missing_ok=True)


def test_observer_supports_docker_desktop_bind_mounts():
    from app.live_guard import create_observer

    observer = create_observer()
    try:
        assert isinstance(observer, PollingObserver)
    finally:
        observer.stop()
