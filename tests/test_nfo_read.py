from types import SimpleNamespace

import pytest

from mdcx.config.enums import Language, NfoInclude, OutlineShow, ReadMode
from mdcx.core import nfo as nfo_module
from mdcx.gen.field_enums import CrawlerResultFields
from mdcx.models.types import CrawlersResult, FileInfo


class _RenderedTitle:
    def __init__(self, text: str):
        self.text = text


def _build_file_info(tmp_path) -> FileInfo:
    file_info = FileInfo.empty()
    file_info.number = "ABC-123"
    file_info.file_path = tmp_path / "ABC-123.mp4"
    file_info.folder_path = tmp_path
    file_info.file_name = "ABC-123"
    return file_info


@pytest.mark.asyncio
async def test_get_nfo_data_reads_multiline_plot_via_xpath(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setattr(nfo_module.manager.config, "read_mode", [])
    monkeypatch.setattr(
        nfo_module.manager.config.__class__,
        "get_field_config",
        lambda self, field: SimpleNamespace(
            language=Language.ZH_CN if field == CrawlerResultFields.OUTLINE else Language.JP
        ),
    )

    video_path = tmp_path / "JUMS-150.mp4"
    video_path.write_bytes(b"")
    nfo_path = tmp_path / "JUMS-150.nfo"
    nfo_path.write_text(
        """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
  <title>[JUMS-150]巡 一周年8小时</title>
  <originaltitle>JUMS-150 めぐり The First Anniversary 8時間</originaltitle>
  <num>JUMS-150</num>
  <plot><![CDATA[中文简介第一段

中文简介第二段

極上のエロスを纏ってカムバックした国民的AV女優『めぐり』。

由 百度 提供翻译]]></plot>
  <outline><![CDATA[中文简介第一段

中文简介第二段

極上のエロスを纏ってカムバックした国民的AV女優『めぐり』。

由 百度 提供翻译]]></outline>
  <originalplot><![CDATA[極上のエロスを纏ってカムバックした国民的AV女優『めぐり』。]]></originalplot>
</movie>
""",
        encoding="utf-8",
    )

    data, info = await nfo_module.get_nfo_data(video_path, "JUMS-150")

    assert data is not None
    assert info is not None
    assert data.outline == "中文简介第一段\n\n中文简介第二段"
    assert data.originalplot == "極上のエロスを纏ってカムバックした国民的AV女優『めぐり』。"
    assert data.outline_from == "百度"


@pytest.mark.asyncio
async def test_get_nfo_data_strips_only_leading_number_prefix(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setattr(nfo_module.manager.config, "read_mode", [])
    monkeypatch.setattr(
        nfo_module.manager.config.__class__,
        "get_field_config",
        lambda self, field: SimpleNamespace(language=Language.JP if field != CrawlerResultFields.OUTLINE else Language.ZH_CN),
    )

    video_path = tmp_path / "ABC-123.mp4"
    video_path.write_bytes(b"")
    nfo_path = tmp_path / "ABC-123.nfo"
    nfo_path.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<movie>
  <title>ABC-123 特别篇 ABC-123 完整版</title>
  <originaltitle>ABC-123 オリジナル ABC-123 完全版</originaltitle>
  <num>ABC-123</num>
</movie>
""",
        encoding="utf-8",
    )

    data, info = await nfo_module.get_nfo_data(video_path, "ABC-123")

    assert data is not None
    assert info is not None
    assert data.title == "特别篇 ABC-123 完整版"
    assert data.originaltitle == "オリジナル ABC-123 完全版"


@pytest.mark.asyncio
async def test_nfo_outline_roundtrip_keeps_outline_source_and_originalplot(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setattr(nfo_module.manager.config, "download_files", [])
    monkeypatch.setattr(nfo_module.manager.config, "keep_files", [])
    monkeypatch.setattr(nfo_module.manager.config, "main_mode", 1)
    monkeypatch.setattr(nfo_module.manager.config, "naming_media", "number title")
    monkeypatch.setattr(nfo_module.manager.config, "update_titletemplate", "number title")
    monkeypatch.setattr(
        nfo_module.manager.config,
        "nfo_include_new",
        [NfoInclude.PLOT_, NfoInclude.OUTLINE, NfoInclude.ORIGINALPLOT, NfoInclude.ORIGINALTITLE],
    )
    monkeypatch.setattr(nfo_module.manager.config, "outline_format", [OutlineShow.SHOW_JP_ZH, OutlineShow.SHOW_FROM])
    monkeypatch.setattr(nfo_module.manager.config, "read_mode", [])
    monkeypatch.setattr(nfo_module.manager.config, "actor_no_name", "佚名")
    monkeypatch.setattr(nfo_module, "render_name", lambda *args, **kwargs: _RenderedTitle("ABC-123 中文标题"))
    monkeypatch.setattr(
        nfo_module.manager.config.__class__,
        "get_field_config",
        lambda self, field: SimpleNamespace(
            language=Language.ZH_CN if field == CrawlerResultFields.OUTLINE else Language.JP
        ),
    )

    file_info = _build_file_info(tmp_path)
    file_info.file_path.write_bytes(b"")
    data = CrawlersResult.empty()
    data.number = "ABC-123"
    data.title = "中文标题"
    data.originaltitle = "日文标题"
    data.outline = "中文简介"
    data.originalplot = "日文简介"
    data.outline_from = "Baidu"

    nfo_file = tmp_path / "ABC-123.nfo"
    result = await nfo_module.write_nfo(file_info, data, nfo_file, tmp_path, update=True)

    assert result is True

    roundtrip_data, info = await nfo_module.get_nfo_data(file_info.file_path, "ABC-123")

    assert roundtrip_data is not None
    assert info is not None
    assert roundtrip_data.title == "中文标题"
    assert roundtrip_data.originaltitle == "日文标题"
    assert roundtrip_data.outline == "中文简介"
    assert roundtrip_data.originalplot == "日文简介"
    assert roundtrip_data.outline_from == "百度"


@pytest.mark.asyncio
async def test_get_nfo_data_read_update_preserves_actor_prefix_tag(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setattr(nfo_module.manager.config, "read_mode", [ReadMode.READ_UPDATE_NFO])
    monkeypatch.setattr(
        nfo_module.manager.config.__class__,
        "get_field_config",
        lambda self, field: SimpleNamespace(
            language=Language.ZH_CN if field == CrawlerResultFields.OUTLINE else Language.JP
        ),
    )

    video_path = tmp_path / "ABC-123.mp4"
    video_path.write_bytes(b"")
    nfo_path = tmp_path / "ABC-123.nfo"
    nfo_path.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<movie>
  <title>ABC-123 标题</title>
  <originaltitle>ABC-123 タイトル</originaltitle>
  <num>ABC-123</num>
  <actor><name>上原亚衣</name></actor>
  <tag>演员: 上原亚衣</tag>
  <tag>系列: 测试系列</tag>
  <tag>中文字幕</tag>
  <tag>巨乳</tag>
</movie>
""",
        encoding="utf-8",
    )

    data, info = await nfo_module.get_nfo_data(video_path, "ABC-123")

    assert data is not None
    assert info is not None
    assert data.tag == "演员: 上原亚衣,系列: 测试系列,巨乳"
