from app.detectors.regex_detector import detect_all


def test_local_sqlite_urls_are_not_credentials():
    text = "DATABASE_URL=sqlite+aiosqlite:////data/shadowai.db"

    result = detect_all(text)

    assert not any(item["entity_type"] == "DATABASE_URL" for item in result["entities"])


def test_remote_database_urls_are_detected():
    result = detect_all("DATABASE_URL=" + "postgres" + "ql://user:pass@example.invalid/app")

    assert any(item["entity_type"] == "DATABASE_URL" for item in result["entities"])
