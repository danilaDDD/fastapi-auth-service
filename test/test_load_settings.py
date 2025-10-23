import os


def test_load_settings_with_default_env(monkeypatch):
    from settings.settings import load_settings

    settings = load_settings()
    assert settings is not None
    assert settings.ENV == "dev"
    assert len(settings.get_database_url()) > 5

def test_load_settings_with_test_env(monkeypatch):
    from settings.settings import load_settings

    os.environ['ENV'] = 'test'
    settings = load_settings()
    assert settings is not None
    assert settings.ENV == "test"
    assert "test" in settings.get_database_url()