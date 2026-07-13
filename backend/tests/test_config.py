from app.core.config import Settings


def test_settings_have_no_default_secret():
    settings = Settings(_env_file=None)
    assert settings.SECRET_KEY == ""
