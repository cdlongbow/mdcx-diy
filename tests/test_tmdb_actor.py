from pathlib import Path

import pytest
from openpyxl import load_workbook

from mdcx.core import tmdb_actor


@pytest.fixture
def _tmp_actor_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(tmdb_actor.manager, "data_folder", tmp_path)
    monkeypatch.setattr(tmdb_actor.resources, "actor_db", {})
    userdata = tmp_path / "userdata"
    userdata.mkdir(parents=True, exist_ok=True)
    return userdata / "actor_database.xlsx"


def test_expand_name_variants_supports_kana_ko_and_kanji_ko():
    assert tmdb_actor._expand_name_variants("加瀬かなこ") == {"加濑かなこ", "加濑かな子"}
    assert tmdb_actor._expand_name_variants("加瀬かな子") == {"加濑かなこ", "加濑かな子"}


def test_search_actor_db_reverse_matches_variant_and_alias(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        tmdb_actor.resources,
        "actor_db",
        {
            "上原亜衣": {
                "zh_cn": "上原亚衣",
                "zh_tw": "上原亞衣",
                "keyword": "Rio,上原亚衣",
                "href": "",
                "tmdbid": 123,
                "tmdb_url": "https://www.themoviedb.org/person/123",
            }
        },
    )
    monkeypatch.setattr(tmdb_actor.resources, "actor_db_reverse_index", None)

    by_variant = tmdb_actor.search_actor_db_reverse("上原亚衣")
    by_alias = tmdb_actor.search_actor_db_reverse("Rio")

    assert by_variant is not None
    assert by_variant["jp"] == "上原亜衣"
    assert by_variant["tmdbid"] == 123

    assert by_alias is not None
    assert by_alias["jp"] == "上原亜衣"
    assert by_alias["tmdbid"] == 123


def test_search_actor_db_reverse_builds_reusable_index(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        tmdb_actor.resources,
        "actor_db",
        {
            "加瀬かなこ": {
                "zh_cn": "加濑香奈子",
                "zh_tw": "加瀨香奈子",
                "keyword": "Kana,加濑かな子",
                "href": "",
                "tmdbid": 456,
                "tmdb_url": "https://www.themoviedb.org/person/456",
            }
        },
    )
    monkeypatch.setattr(tmdb_actor.resources, "actor_db_reverse_index", None)

    result = tmdb_actor.search_actor_db_reverse("加瀬かな子")

    assert result is not None
    assert result["jp"] == "加瀬かなこ"
    assert tmdb_actor.resources.actor_db_reverse_index is not None
    assert tmdb_actor.search_actor_db_reverse("Kana")["tmdbid"] == 456


def test_is_japan_place_supports_localized_place_names():
    assert tmdb_actor.is_japan_place("东京") is True
    assert tmdb_actor.is_japan_place("神奈川县") is True
    assert tmdb_actor.is_japan_place("中国广东") is False


@pytest.mark.asyncio
async def test_fetch_person_translations_distinguishes_cn_and_tw(monkeypatch: pytest.MonkeyPatch):
    class _StubResponse:
        def __init__(self, payload):
            self.status_code = 200
            self._payload = payload

        def json(self):
            return self._payload

    async def _stub_tmdb_request(*args, **kwargs):
        return _StubResponse(
            {
                "translations": [
                    {
                        "iso_639_1": "zh",
                        "iso_3166_1": "CN",
                        "english_name": "Kana",
                        "data": {"name": "加濑香奈"},
                    },
                    {
                        "iso_639_1": "zh",
                        "iso_3166_1": "TW",
                        "english_name": "Kana",
                        "data": {"name": "加瀨香奈"},
                    },
                ]
            }
        )

    monkeypatch.setattr(tmdb_actor, "_tmdb_request", _stub_tmdb_request)

    result = await tmdb_actor._fetch_person_translations(123, "https://api.tmdb.org", "token", object())

    assert result == {"zh_cn": "加濑香奈", "zh_tw": "加瀨香奈"}


@pytest.mark.asyncio
async def test_query_single_actor_tolerates_missing_http_response(monkeypatch: pytest.MonkeyPatch):
    async def _stub_tmdb_request(*args, **kwargs):
        return None

    monkeypatch.setattr(tmdb_actor, "_tmdb_request", _stub_tmdb_request)
    monkeypatch.setattr(tmdb_actor.manager.config, "show_data_log", False)

    result = await tmdb_actor._query_single_actor("上原亜衣", "https://api.tmdb.org", "token", object())

    assert result is None


@pytest.mark.asyncio
async def test_update_actor_db_row_allows_new_actor_insert_with_tmdbid(_tmp_actor_db: Path):
    status = await tmdb_actor.update_actor_db_row(
        jp="未知演员",
        zh_cn="未知演员",
        tmdbid=54321,
    )

    assert status == "inserted_new_row"

    wb = load_workbook(_tmp_actor_db)
    ws = wb.active
    assert ws.cell(row=2, column=1).value == "未知演员"
    assert ws.cell(row=2, column=6).value == 54321
    wb.close()


@pytest.mark.asyncio
async def test_update_actor_db_row_writes_tmdbid_and_tmdb_url(_tmp_actor_db: Path):
    status = await tmdb_actor.update_actor_db_row(
        jp="上原亜衣",
        zh_cn="上原亚衣",
        keyword="Rio",
        tmdbid=12345,
    )

    assert status == "inserted_new_row"

    wb = load_workbook(_tmp_actor_db)
    ws = wb.active
    assert ws.cell(row=2, column=1).value == "上原亜衣"
    assert ws.cell(row=2, column=2).value == "上原亚衣"
    assert ws.cell(row=2, column=6).value == 12345
    assert ws.cell(row=2, column=7).value == "https://www.themoviedb.org/person/12345"
    assert ws.cell(row=2, column=7).hyperlink.target == "https://www.themoviedb.org/person/12345"
    wb.close()


@pytest.mark.asyncio
async def test_update_actor_db_row_returns_inserted_tmdbid_for_existing_row(_tmp_actor_db: Path):
    await tmdb_actor.update_actor_db_row(jp="北條麻妃", zh_cn="北条麻妃")

    status = await tmdb_actor.update_actor_db_row(
        jp="北條麻妃",
        keyword="北条麻妃,Maki Hojo",
        tmdbid=67890,
        append_keyword=True,
    )

    assert status == "inserted_tmdbid"

    wb = load_workbook(_tmp_actor_db)
    ws = wb.active
    assert ws.cell(row=2, column=6).value == 67890
    assert ws.cell(row=2, column=7).value == "https://www.themoviedb.org/person/67890"
    keywords = {part.strip() for part in str(ws.cell(row=2, column=4).value or "").split(",") if part.strip()}
    assert keywords == {"北条麻妃", "Maki Hojo"}
    wb.close()


@pytest.mark.asyncio
async def test_update_actor_db_row_keeps_existing_tmdbid(_tmp_actor_db: Path):
    await tmdb_actor.update_actor_db_row(jp="加瀬かなこ", tmdbid=111)

    status = await tmdb_actor.update_actor_db_row(jp="加瀬かなこ", tmdbid=222)

    assert status == "kept_existing_tmdbid"

    wb = load_workbook(_tmp_actor_db)
    ws = wb.active
    assert ws.cell(row=2, column=6).value == 111
    assert ws.cell(row=2, column=7).value == "https://www.themoviedb.org/person/111"
    wb.close()
