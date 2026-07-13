from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_compose() -> dict:
    return yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))


def test_compose_exposes_only_loopback():
    compose = load_compose()
    assert compose["services"]["api"]["ports"] == ["127.0.0.1:8000:8000"]
    assert compose["services"]["web"]["ports"] == ["127.0.0.1:3000:3000"]


def test_cli_and_api_share_backend_image():
    compose = load_compose()
    assert compose["services"]["api"]["image"] == compose["services"]["shadowai"]["image"]


def test_database_is_stored_in_named_volume():
    compose = load_compose()
    assert "shadowai_data:/data" in compose["services"]["api"]["volumes"]
    assert "shadowai_data" in compose["volumes"]


def test_api_has_healthcheck_and_web_waits_for_it():
    compose = load_compose()
    assert "healthcheck" in compose["services"]["api"]
    assert compose["services"]["web"]["depends_on"]["api"]["condition"] == "service_healthy"
