from pathlib import Path

import pytest

from scripts import build


def test_app_icon_path_windows(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(build.platform, "system", lambda: "Windows")
    manager = build.BuildManager(app_name="MDCx", app_version="2.0.0", create_dmg=False, debug=False)

    assert manager._app_icon_path() == "resources/Img/MDCx.ico"


def test_app_icon_path_macos(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(build.platform, "system", lambda: "Darwin")
    manager = build.BuildManager(app_name="MDCx", app_version="2.0.0", create_dmg=True, debug=False)

    assert manager._app_icon_path() == "resources/Img/MDCx.icns"


def test_generate_spec_windows_command(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(build.platform, "system", lambda: "Windows")
    manager = build.BuildManager(app_name="MDCx", app_version="2.0.0", create_dmg=False, debug=False)

    captured = {}

    def _fake_run_command(args, success_msg=None, error_msg=None):
        captured["args"] = list(args)

    monkeypatch.setattr(manager, "_run_command", _fake_run_command)
    manager._generate_spec()

    args = captured["args"]
    assert args[0] == "pyi-makespec"
    assert "--onefile" in args
    assert "--name" in args and "MDCx" in args
    assert "--add-data" in args
    assert "resources:resources" in args
    assert "libs:." in args
    assert "resources/Img/MDCx.ico" in args
    assert "--osx-bundle-identifier" not in args


def test_build_app_windows_checks_exe_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(build.platform, "system", lambda: "Windows")
    manager = build.BuildManager(app_name="MDCx", app_version="2.0.0", create_dmg=False, debug=False)

    monkeypatch.chdir(tmp_path)
    dist = tmp_path / "dist"
    dist.mkdir()
    expected_output = dist / "MDCx.exe"
    expected_output.write_text("payload", encoding="utf-8")

    commands = []

    def _fake_run_command(args, success_msg=None, error_msg=None):
        commands.append(list(args))

    monkeypatch.setattr(manager, "_run_command", _fake_run_command)
    manager._build_app()

    assert commands == [["pyinstaller", "MDCx.spec", "-y"]]
    assert expected_output.exists()
