import json

from app.cli import main, scan_prompt_for_cli


def test_safe_prompt_is_allowed():
    result = scan_prompt_for_cli("Summarize this public paragraph", "developer")
    assert result["policy_decision"]["action"] == "allow"


def test_secret_output_is_redacted(capsys):
    fixture_value = "sk-" + "ABCDEFGHIJKLMNOPQRSTUVWX"
    assert main(["prompt", fixture_value]) == 2
    output = capsys.readouterr().out
    assert fixture_value not in output
    assert "API_KEY" in output
    assert "BLOCK" in output


def test_json_output_is_machine_readable_and_redacted(capsys):
    import app.ml.predict as prediction

    prediction.model = None
    fixture_value = "sk-" + "ABCDEFGHIJKLMNOPQRSTUVWX"
    assert main(["prompt", fixture_value, "--json"]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["risk_level"] == "Critical"
    assert fixture_value not in json.dumps(payload)


def test_warning_returns_one(monkeypatch):
    monkeypatch.setattr(
        "app.cli.scan_prompt_for_cli",
        lambda *_: {
            "risk_score": 45,
            "risk_level": "Medium",
            "entities": [],
            "policy_decision": {"action": "warn", "policy_mode": "Developer", "reasons": ["Review"]},
            "safe_text": "",
        },
    )
    assert main(["prompt", "review me"]) == 1


def test_info_lists_live_guard_commands(capsys):
    assert main(["info"]) == 0
    output = capsys.readouterr().out
    assert "watch" in output
    assert "install-hooks" in output
    assert "monitor-repo" in output


def test_repo_rejects_non_github_url_without_cloning(capsys):
    assert main(["repo", "file:///etc"]) == 3
    assert "Only public" in capsys.readouterr().err
