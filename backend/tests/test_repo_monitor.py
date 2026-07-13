import pytest

from app.repo_monitor import finding_fingerprint, monitor_repository


def test_fingerprint_ignores_finding_order():
    left = {
        "findings": [
            {"file_path": "a", "line_number": 1, "entity_type": "API_KEY", "severity": "critical"},
            {"file_path": "b", "line_number": 2, "entity_type": "EMAIL", "severity": "low"},
        ]
    }
    right = {"findings": list(reversed(left["findings"]))}
    assert finding_fingerprint(left) == finding_fingerprint(right)


@pytest.mark.parametrize("interval", [0, 29, 86401])
def test_monitor_rejects_unsafe_intervals(interval):
    with pytest.raises(ValueError):
        monitor_repository(
            "https://github.com/openai/openai-python",
            interval,
            max_cycles=0,
        )


def test_monitor_prints_initial_and_changed_results_only(capsys):
    first = {
        "repo_url": "https://github.com/openai/openai-python",
        "files_scanned": 1,
        "secrets_found": 0,
        "risk_score": 0,
        "risk_level": "Safe",
        "findings": [],
    }
    changed = {
        **first,
        "secrets_found": 1,
        "risk_score": 90,
        "risk_level": "Critical",
        "findings": [
            {
                "file_path": "config.env",
                "line_number": 1,
                "entity_type": "API_KEY",
                "severity": "critical",
                "redacted_value": "sk-A***WXYZ [API_KEY_REDACTED]",
            }
        ],
    }
    results = iter([first, first, changed])

    assert monitor_repository(
        first["repo_url"],
        30,
        scanner=lambda _: next(results),
        sleeper=lambda _: None,
        max_cycles=3,
    ) == 0

    output = capsys.readouterr().out
    assert output.count("ShadowAI Repository Scan") == 2
    assert "API_KEY" in output
