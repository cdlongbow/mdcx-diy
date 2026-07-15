import asyncio

import pytest

from mdcx.config.manager import manager
from mdcx.models.flags import Flags
from mdcx.signals import signal
from mdcx.tools import emby_actor_image, emby_actor_info


@pytest.fixture(autouse=True)
def reset_stop_flags():
    Flags.stop_requested = False
    signal.stop = False
    yield
    Flags.stop_requested = False
    signal.stop = False


@pytest.mark.asyncio
async def test_update_emby_actor_info_stops_and_cancels_pending_tasks(monkeypatch: pytest.MonkeyPatch):
    logs: list[str] = []
    pending_cancelled = asyncio.Event()

    async def fake_get_actor_list():
        return [{"Name": "演员甲", "Id": "1"}, {"Name": "演员乙", "Id": "2"}]

    async def fake_process_actor(actor: dict, emby_on):
        if actor["Name"] == "演员甲":
            Flags.stop_requested = True
            return 1, "first-done"
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            pending_cancelled.set()
            raise

    monkeypatch.setattr(manager.config, "server_type", "emby")
    monkeypatch.setattr(manager.config, "emby_on", [])
    monkeypatch.setattr(emby_actor_info, "_get_emby_actor_list", fake_get_actor_list)
    monkeypatch.setattr(emby_actor_info, "_process_actor_async", fake_process_actor)
    monkeypatch.setattr(emby_actor_info.signal, "change_buttons_status", type("", (), {"emit": lambda self: None})())
    monkeypatch.setattr(emby_actor_info.signal, "reset_buttons_status", type("", (), {"emit": lambda self: None})())
    monkeypatch.setattr(emby_actor_info.signal, "show_log_text", logs.append)

    await emby_actor_info.update_emby_actor_info()

    assert pending_cancelled.is_set()
    assert "⛔️ 演员信息补全已手动停止！" in logs
    assert "first-done" not in logs


@pytest.mark.asyncio
async def test_update_emby_actor_photo_stops_before_execute(monkeypatch: pytest.MonkeyPatch):
    logs: list[str] = []
    executed = False

    async def fake_get_actor_list():
        return [{"Name": "演员甲", "Id": "1"}]

    async def fake_get_gfriends_actor_data():
        Flags.stop_requested = True
        return {"演员甲.jpg": "https://example.com/a.jpg"}

    async def fake_execute(actor_list, gfriends_actor_data):
        nonlocal executed
        executed = True

    monkeypatch.setattr(manager.config, "server_type", "emby")
    monkeypatch.setattr(emby_actor_image, "_get_emby_actor_list", fake_get_actor_list)
    monkeypatch.setattr(emby_actor_image, "_get_gfriends_actor_data", fake_get_gfriends_actor_data)
    monkeypatch.setattr(emby_actor_image, "_update_emby_actor_photo_execute", fake_execute)
    monkeypatch.setattr(emby_actor_image.signal, "change_buttons_status", type("", (), {"emit": lambda self: None})())
    monkeypatch.setattr(emby_actor_image.signal, "reset_buttons_status", type("", (), {"emit": lambda self: None})())
    monkeypatch.setattr(emby_actor_image.signal, "show_log_text", logs.append)

    await emby_actor_image.update_emby_actor_photo()

    assert executed is False
    assert "⛔️ 演员头像补全已手动停止！" in logs


@pytest.mark.asyncio
async def test_update_emby_actor_photo_execute_uploads_primary_and_backdrop(monkeypatch: pytest.MonkeyPatch, tmp_path):
    logs: list[str] = []
    pic_path = tmp_path / "actor.jpg"
    pic_path.write_bytes(b"test")
    backdrop_path = tmp_path / "actor-big.jpg"
    backdrop_path.write_bytes(b"test")
    uploads: list[tuple[str, dict]] = []

    async def fake_get_graphis_pic(actor_name: str):
        return None, None, ""

    async def fake_fix_pic_async(src, dst):
        return None

    def fake_cut_pic(path):
        return None

    # 直接 mock 底层 post_content, 从而能验证 Authorization 头(而非绕过它的 _upload_actor_photo)。
    async def fake_post_content(url: str, data=None, headers=None, **kwargs):
        uploads.append((url, dict(headers or {})))
        return True, ""

    monkeypatch.setattr(manager.config, "server_type", "emby")
    monkeypatch.setattr(manager.config, "emby_on", [])
    monkeypatch.setattr(manager.config, "api_key", "test-token")
    monkeypatch.setattr(emby_actor_image.signal, "show_log_text", logs.append)
    monkeypatch.setattr(emby_actor_image, "_get_graphis_pic", fake_get_graphis_pic)
    monkeypatch.setattr(emby_actor_image, "fix_pic_async", fake_fix_pic_async)
    monkeypatch.setattr(emby_actor_image, "cut_pic", fake_cut_pic)
    monkeypatch.setattr(manager.computed.async_client, "post_content", fake_post_content)

    await emby_actor_image._update_emby_actor_photo_execute(
        [{"Name": "演员甲", "Id": "1", "ServerId": "server-1", "ImageTags": {}, "BackdropImageTags": []}],
        {"演员甲.jpg": pic_path},
    )

    api_key = manager.config.api_key
    expected_auth = f'MediaBrowser Token="{api_key}"'

    # P1-5: api_key 不再出现在 URL 中, 改为通过 Authorization 头携带, 避免泄露到访问/调试日志。
    assert len(uploads) == 2
    primary_url, primary_headers = uploads[0]
    backdrop_url, backdrop_headers = uploads[1]
    assert primary_url.endswith("/emby/Items/1/Images/Primary")
    assert "?api_key=" not in primary_url
    assert backdrop_url.endswith("/emby/Items/1/Images/Backdrop")
    assert "?api_key=" not in backdrop_url
    assert primary_headers.get("Authorization") == expected_auth
    assert backdrop_headers.get("Authorization") == expected_auth
