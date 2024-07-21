from pytest import MonkeyPatch

from tons import settings


def test_settings_current_config_path(tons_workdir):
    # SETUP
    with MonkeyPatch.context() as monkeypatch_context:
        monkeypatch_context.setattr(settings, "GLOBAL_CONFIG_PATH", [tons_workdir / "config.yaml"])
        monkeypatch_context.setattr(settings, "CUSTOM_CONFIG_PATH", None)

        import importlib

        importlib.reload(settings)

    # ASSERT
    assert (
        settings.current_config_path() == settings.CUSTOM_CONFIG_PATH
        or settings.current_config_path() == settings.GLOBAL_CONFIG_PATH
    )
