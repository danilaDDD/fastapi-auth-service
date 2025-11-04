from settings.settings import Settings


def test_env():
    import os
    assert os.getenv('ENV') == 'test'


def test_load_settings_with_test_env(settings: Settings):
    assert settings is not None
    assert settings.ENV == "test"
    assert "test" in settings.get_database_url()