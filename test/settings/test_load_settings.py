def test_load_settings_with_test_env():
    from settings.settings import load_settings
    settings = load_settings()
    assert settings is not None
    assert settings.ENV == "test"
    assert "test" in settings.get_database_url()