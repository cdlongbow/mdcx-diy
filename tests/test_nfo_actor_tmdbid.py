import pytest
from lxml import etree

from mdcx.config.enums import NfoInclude
from mdcx.core import nfo as nfo_module
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


def _configure_nfo_writer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nfo_module.manager.config, "download_files", [])
    monkeypatch.setattr(nfo_module.manager.config, "keep_files", [])
    monkeypatch.setattr(nfo_module.manager.config, "outline_format", [])
    monkeypatch.setattr(nfo_module.manager.config, "main_mode", 1)
    monkeypatch.setattr(nfo_module.manager.config, "naming_media", "number title")
    monkeypatch.setattr(nfo_module.manager.config, "update_titletemplate", "number title")
    monkeypatch.setattr(
        nfo_module.manager.config,
        "nfo_include_new",
        [NfoInclude.ACTOR, NfoInclude.ACTOR_TMDBID],
    )
    monkeypatch.setattr(nfo_module.manager.config, "actor_no_name", "佚名")


@pytest.mark.asyncio
async def test_write_nfo_outputs_tmdbid_per_actor(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _configure_nfo_writer(monkeypatch)
    monkeypatch.setattr(nfo_module, "render_name", lambda *args, **kwargs: _RenderedTitle("模板标题"))

    data = CrawlersResult.empty()
    data.number = "ABC-123"
    data.title = "标题"
    data.originaltitle = "原标题"
    data.actors = ["上原亚衣", "北条麻妃"]
    data.original_actors = ["上原亜衣", "北條麻妃"]
    data.actor_tmdb_ids = {"上原亜衣": 101, "北條麻妃": 202}

    nfo_file = tmp_path / "ABC-123.nfo"
    result = await nfo_module.write_nfo(_build_file_info(tmp_path), data, nfo_file, tmp_path, update=True)

    assert result is True

    root = etree.fromstring(nfo_file.read_text(encoding="utf-8").encode("utf-8"))
    actors = root.xpath("//actor")
    assert len(actors) == 2
    assert actors[0].xpath("name/text()") == ["上原亚衣"]
    assert actors[0].xpath("tmdbid/text()") == ["101"]
    assert actors[1].xpath("name/text()") == ["北条麻妃"]
    assert actors[1].xpath("tmdbid/text()") == ["202"]


@pytest.mark.asyncio
async def test_write_nfo_omits_tmdbid_for_unmapped_actor(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _configure_nfo_writer(monkeypatch)
    monkeypatch.setattr(nfo_module, "render_name", lambda *args, **kwargs: _RenderedTitle("模板标题"))

    data = CrawlersResult.empty()
    data.number = "ABC-123"
    data.title = "标题"
    data.originaltitle = "原标题"
    data.actors = ["上原亚衣", "未知演员"]
    data.original_actors = ["上原亜衣", "未知演员"]
    data.actor_tmdb_ids = {"上原亜衣": 101}

    nfo_file = tmp_path / "ABC-123.nfo"
    result = await nfo_module.write_nfo(_build_file_info(tmp_path), data, nfo_file, tmp_path, update=True)

    assert result is True

    root = etree.fromstring(nfo_file.read_text(encoding="utf-8").encode("utf-8"))
    actors = root.xpath("//actor")
    assert len(actors) == 2
    assert actors[0].xpath("name/text()") == ["上原亚衣"]
    assert actors[0].xpath("tmdbid/text()") == ["101"]
    assert actors[1].xpath("name/text()") == ["未知演员"]
    assert actors[1].xpath("tmdbid/text()") == []


@pytest.mark.asyncio
async def test_write_nfo_actor_all_keeps_tmdbid_alignment(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _configure_nfo_writer(monkeypatch)
    monkeypatch.setattr(
        nfo_module.manager.config,
        "nfo_include_new",
        [NfoInclude.ACTOR, NfoInclude.ACTOR_ALL, NfoInclude.ACTOR_TMDBID],
    )
    monkeypatch.setattr(nfo_module, "render_name", lambda *args, **kwargs: _RenderedTitle("模板标题"))

    data = CrawlersResult.empty()
    data.number = "ABC-123"
    data.title = "标题"
    data.originaltitle = "原标题"
    data.actors = ["上原亚衣"]
    data.all_actors = ["上原亚衣", "北条麻妃"]
    data.original_actors = ["上原亜衣", "北條麻妃"]
    data.actor_tmdb_ids = {"上原亜衣": 101, "北條麻妃": 202}

    nfo_file = tmp_path / "ABC-123.nfo"
    result = await nfo_module.write_nfo(_build_file_info(tmp_path), data, nfo_file, tmp_path, update=True)

    assert result is True

    root = etree.fromstring(nfo_file.read_text(encoding="utf-8").encode("utf-8"))
    actors = root.xpath("//actor")
    assert len(actors) == 2
    assert actors[0].xpath("name/text()") == ["上原亚衣"]
    assert actors[0].xpath("tmdbid/text()") == ["101"]
    assert actors[1].xpath("name/text()") == ["北条麻妃"]
    assert actors[1].xpath("tmdbid/text()") == ["202"]
