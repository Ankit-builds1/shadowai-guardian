from datetime import datetime, timedelta

from app.api.dashboard import build_risk_timeline
from app.services.policy_engine import apply_policy


class ScanStub:
    def __init__(self, created_at: datetime, risk_level: str, risk_score: int):
        self.created_at = created_at
        self.risk_level = risk_level
        self.risk_score = risk_score


def test_strict_policy_blocks_high_risk_prompt():
    scan = {
        "risk_score": 74,
        "risk_level": "High",
        "entities": [{"entity_type": "OPENAI_API_KEY", "severity": "critical"}],
        "injection_detected": False,
    }

    decision = apply_policy(scan, "strict")

    assert decision["policy_mode"] == "Strict Compliance"
    assert decision["action"] == "block"
    assert decision["requires_rewrite"] is True
    assert "OPENAI_API_KEY" in decision["reasons"][0]


def test_developer_policy_warns_on_medium_without_secrets():
    scan = {
        "risk_score": 45,
        "risk_level": "Medium",
        "entities": [],
        "injection_detected": False,
    }

    decision = apply_policy(scan, "developer")

    assert decision["policy_mode"] == "Developer"
    assert decision["action"] == "warn"
    assert decision["requires_rewrite"] is False


def test_risk_timeline_returns_last_seven_days_oldest_first():
    today = datetime(2026, 6, 27, 12, 0, 0)
    scans = [
        ScanStub(today - timedelta(days=1), "High", 80),
        ScanStub(today - timedelta(days=1), "Safe", 0),
        ScanStub(today - timedelta(days=6), "Critical", 95),
        ScanStub(today - timedelta(days=8), "Critical", 100),
    ]

    timeline = build_risk_timeline(scans, today=today, days=7)

    assert len(timeline) == 7
    assert timeline[0]["date"] == "2026-06-21"
    assert timeline[-1]["date"] == "2026-06-27"
    assert timeline[0]["critical"] == 1
    assert timeline[-2]["total"] == 2
    assert timeline[-2]["average_risk"] == 40
