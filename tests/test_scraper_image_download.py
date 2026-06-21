import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# Mock PyQt6 before importing any mdcx modules
_pyqt6_mock = types.ModuleType("PyQt6")
_pyqt6_mock.QtWidgets = types.ModuleType("PyQt6.QtWidgets")
_pyqt6_mock.QtWidgets.QMessageBox = type("QMessageBox", (), {"NoIcon": 0})
_pyqt6_mock.QtCore = types.ModuleType("PyQt6.QtCore")
sys.modules.setdefault("PyQt6", _pyqt6_mock)
sys.modules.setdefault("PyQt6.QtWidgets", _pyqt6_mock.QtWidgets)
sys.modules.setdefault("PyQt6.QtCore", _pyqt6_mock.QtCore)

from mdcx.models.flags import Flags  # noqa: E402
from mdcx.models.types import CrawlersResult, FileInfo, OtherInfo  # noqa: E402


class _CallTracker:
    def __init__(self):
        self.calls: list[str] = []

    def track(self, name: str):
        async def _fn(*_args, **_kwargs):
            self.calls.append(name)
            return True

        return _fn


@pytest.mark.asyncio
async def test_download_images_serial_order(monkeypatch: pytest.MonkeyPatch):
    from mdcx.core import scraper as scraper_module

    Flags.reset()
    tracker = _CallTracker()

    monkeypatch.setattr(scraper_module, "thumb_download", tracker.track("thumb_download"))
    monkeypatch.setattr(scraper_module, "fanart_download", tracker.track("fanart_download"))
    monkeypatch.setattr(scraper_module, "poster_download", tracker.track("poster_download"))
    monkeypatch.setattr(scraper_module, "pic_some_deal", tracker.track("pic_some_deal"))
    monkeypatch.setattr(scraper_module, "add_mark", tracker.track("add_mark"))
    monkeypatch.setattr(scraper_module, "extrafanart_download", tracker.track("extrafanart_download"))
    monkeypatch.setattr(scraper_module, "extrafanart_copy2", tracker.track("extrafanart_copy2"))
    monkeypatch.setattr(scraper_module, "extrafanart_extras_copy", tracker.track("extrafanart_extras_copy"))

    scraper = scraper_module.Scraper(crawler_provider=object())
    res = CrawlersResult.empty()
    other = OtherInfo.empty()
    file_info = FileInfo.empty()
    file_info.cd_part = ""
    file_info.mosaic = "有码"

    result = await scraper._download_images(
        res=res,
        other=other,
        file_info=file_info,
        folder_new_path=Path("/tmp/test"),
        thumb_final_path=Path("/tmp/test/thumb.jpg"),
        fanart_final_path=Path("/tmp/test/fanart.jpg"),
        poster_final_path=Path("/tmp/test/poster.jpg"),
        media_context=None,
        single_folder_catched=True,
    )

    assert result is True
    # 并行版本不保证绝对顺序，仅验证依赖约束
    thumb_pos = tracker.calls.index("thumb_download")
    poster_pos = tracker.calls.index("poster_download")
    pic_pos = tracker.calls.index("pic_some_deal")
    mark_pos = tracker.calls.index("add_mark")
    assert thumb_pos < poster_pos, "thumb must be before poster"
    assert poster_pos < pic_pos, "poster must be before pic_some_deal"
    assert pic_pos < mark_pos, "pic_some_deal must be before add_mark"
    # fanart 和 extrafanart 无依赖约束，可在任意位置


@pytest.mark.asyncio
async def test_download_images_returns_false_on_thumb_failure(monkeypatch: pytest.MonkeyPatch):
    from mdcx.core import scraper as scraper_module

    Flags.reset()

    async def fail_thumb(*_args, **_kwargs):
        return False

    monkeypatch.setattr(scraper_module, "thumb_download", fail_thumb)
    monkeypatch.setattr(scraper_module, "fanart_download", AsyncMock())
    monkeypatch.setattr(scraper_module, "poster_download", AsyncMock())

    scraper = scraper_module.Scraper(crawler_provider=object())
    res = CrawlersResult.empty()
    other = OtherInfo.empty()
    file_info = FileInfo.empty()
    file_info.cd_part = ""
    file_info.mosaic = "有码"

    result = await scraper._download_images(
        res=res,
        other=other,
        file_info=file_info,
        folder_new_path=Path("/tmp/test"),
        thumb_final_path=Path("/tmp/test/thumb.jpg"),
        fanart_final_path=Path("/tmp/test/fanart.jpg"),
        poster_final_path=Path("/tmp/test/poster.jpg"),
        media_context=None,
    )

    assert result is False


@pytest.mark.asyncio
async def test_download_images_returns_false_on_poster_failure(monkeypatch: pytest.MonkeyPatch):
    from mdcx.core import scraper as scraper_module

    Flags.reset()

    tracker = _CallTracker()
    monkeypatch.setattr(scraper_module, "thumb_download", tracker.track("thumb_download"))

    async def fail_poster(*_args, **_kwargs):
        return False

    monkeypatch.setattr(scraper_module, "fanart_download", AsyncMock())
    monkeypatch.setattr(scraper_module, "poster_download", fail_poster)

    scraper = scraper_module.Scraper(crawler_provider=object())
    res = CrawlersResult.empty()
    other = OtherInfo.empty()
    file_info = FileInfo.empty()
    file_info.cd_part = ""
    file_info.mosaic = "有码"

    result = await scraper._download_images(
        res=res,
        other=other,
        file_info=file_info,
        folder_new_path=Path("/tmp/test"),
        thumb_final_path=Path("/tmp/test/thumb.jpg"),
        fanart_final_path=Path("/tmp/test/fanart.jpg"),
        poster_final_path=Path("/tmp/test/poster.jpg"),
        media_context=None,
    )

    assert result is False
    assert tracker.calls == ["thumb_download"], f"Expected only thumb before failure, got {tracker.calls}"
