import pytest

from mdcx.config.models import Website
from mdcx.crawlers.r18dev import R18devCrawler, _generate_content_id_variations, _normalize_id, _series_number
from mdcx.models.types import CrawlerInput


def test_normalize_id():
    assert _normalize_id("IPX-535") == "ipx00535"
    assert _normalize_id("SSIS-001") == "ssis00001"
    assert _normalize_id("ABF-030") == "abf00030"
    assert _normalize_id("SSIS-1") == "ssis00001"
    assert _normalize_id("midv-512") == "midv00512"


def test_normalize_id_already_normalized():
    assert _normalize_id("ipx00535") == "ipx00535"
    assert _normalize_id("ssis00001") == "ssis00001"


def test_normalize_id_with_spaces():
    assert _normalize_id("IPX 535") == "ipx00535"
    assert _normalize_id("midv 512") == "midv00512"


def test_content_id_variations():
    vars = _generate_content_id_variations("ABF-030")
    assert "118abf00030" in vars
    assert "118abf030" in vars
    assert "436abf00030" not in vars  # 436 is not in our prefix table for abf


def test_content_id_variations_unknown_series():
    vars = _generate_content_id_variations("ZZZ-001")
    assert "1zzz00001" in vars or "zzz00001" in vars


def test_series_number():
    assert _series_number("IPX-535") == ("ipx", "535")
    assert _series_number("SSIS-001") == ("ssis", "001")
    assert _series_number("") == ("", "")


def test_site_enum():
    assert R18devCrawler.site() == Website.R18DEV


def test_display_name():
    assert R18devCrawler.display_name() == "R18.dev"


def test_supports_custom_url():
    assert R18devCrawler.supports_custom_url() is True


def test_parse_json_full_data():
    crawler = R18devCrawler(client=None)
    data = crawler._parse_json(
        {
            "dvd_id": "ipx00535",
            "content_id": "118ipx00535",
            "title_ja": "タイトル",
            "title_en": "Title English",
            "release_date": "2024-01-15",
            "runtime_mins": 120,
            "directors": [{"name_kanji": "監督A", "name_romaji": "Director A"}],
            "maker_name_ja": "メーカー",
            "maker_name_en": "Maker",
            "label_name_ja": "レーベル",
            "label_name_en": "Label",
            "series_name_ja": "シリーズ",
            "series_name_en": "Series",
            "actresses": [
                {"name_kanji": "女優A", "name_romaji": "Actress A"},
                {"name_kanji": "", "name_romaji": "Actress B"},
            ],
            "categories": [
                {"name_ja": "カテゴリA", "name_en": "Category A"},
                {"name_ja": "", "name_en": "Category B"},
            ],
            "jacket_full_url": "https://pics.dmm.co.jp/mono/abc/abcpl.jpg",
            "gallery": [{"image_full": "https://pics.dmm.co.jp/mono/abc/abcjp-1.jpg"}],
            "sample_url": "https://cc3001.dmm.co.jp/pv/abc.mp4",
        },
        ctx=None,
    )

    assert data.number == "IPX-535"
    assert data.title == "タイトル"
    assert data.originaltitle == "タイトル"
    assert data.actors == ["女優A", "Actress B"]
    assert data.all_actors == ["女優A", "Actress B"]
    assert data.studio == "メーカー"
    assert data.publisher == "レーベル"
    assert data.series == "シリーズ"
    assert data.release == "2024-01-15"
    assert data.year == "2024"
    assert data.runtime == "120"
    assert data.tags == ["カテゴリA", "Category B"]
    assert data.thumb == "https://pics.dmm.co.jp/mono/abc/abcpl.jpg"
    assert data.poster == "https://pics.dmm.co.jp/mono/abc/abcpl.jpg"
    assert data.extrafanart == ["https://pics.dmm.co.jp/mono/abc/abcjp-1.jpg"]
    assert data.trailer == "https://cc3001.dmm.co.jp/pv/abc.mp4"
    assert data.directors == ["監督A"]
    assert data.external_id == "118ipx00535"


def test_parse_json_minimal_data():
    crawler = R18devCrawler(client=None)
    data = crawler._parse_json(
        {
            "dvd_id": "ssis001",
            "content_id": "118ssis001",
            "title_ja": "テスト",
            "release_date": "2023-06-01",
            "runtime_mins": 90,
        },
        ctx=None,
    )

    assert data.number == "SSIS-001"
    assert data.title == "テスト"
    assert data.release == "2023-06-01"
    assert data.year == "2023"
    assert data.runtime == "90"
    assert data.actors == []
    assert data.tags == []


def test_parse_json_uses_jacket_from_images():
    crawler = R18devCrawler(client=None)
    data = crawler._parse_json(
        {
            "dvd_id": "test001",
            "content_id": "test001",
            "title_ja": "Test",
            "images": {
                "jacket_image": {
                    "large2": "https://pics.dmm.co.jp/mono/test/large2.jpg",
                    "large": "https://pics.dmm.co.jp/mono/test/large.jpg",
                }
            },
        },
        ctx=None,
    )

    assert data.thumb == "https://pics.dmm.co.jp/mono/test/large2.jpg"


def test_parse_json_trailer_from_sample_object():
    crawler = R18devCrawler(client=None)
    data = crawler._parse_json(
        {
            "dvd_id": "test001",
            "content_id": "test001",
            "title_ja": "Test",
            "sample": {"high": "https://cc3001.dmm.co.jp/pv/high.mp4"},
        },
        ctx=None,
    )

    assert data.trailer == "https://cc3001.dmm.co.jp/pv/high.mp4"


@pytest.mark.asyncio
async def test_run_with_dvd_id_match(monkeypatch):
    api_response = {
        "dvd_id": "ipx00535",
        "content_id": "118ipx00535",
        "title_ja": "タイトル",
        "title_en": "Title English",
        "release_date": "2024-01-15",
        "runtime_mins": 120,
        "maker_name_ja": "メーカー",
        "actresses": [{"name_kanji": "女優A", "name_romaji": "Actress A"}],
        "categories": [{"name_ja": "カテゴリA", "name_en": "Category A"}],
        "jacket_full_url": "https://pics.dmm.co.jp/mono/abc/abcpl.jpg",
    }

    call_count = 0

    class FakeClient:
        async def get_json(self, url, **kwargs):
            nonlocal call_count
            call_count += 1
            if "dvd_id=" in url:
                return (api_response, "")
            if "combined=" in url:
                return (api_response, "")
            return (None, "unknown url")

        async def get_text(self, url, **kwargs):
            return (None, "")

        async def request(self, *args, **kwargs):
            return (None, "")

    crawler = R18devCrawler(client=FakeClient())
    input_data = CrawlerInput.empty()
    input_data.number = "IPX-535"
    result = await crawler.run(input_data)

    assert result.data is not None
    assert result.data.number == "IPX-535"
    assert result.data.title == "タイトル"
    assert result.data.studio == "メーカー"
    assert result.data.actors == ["女優A"]
    assert call_count >= 1


@pytest.mark.asyncio
async def test_run_with_content_id_fallback(monkeypatch):
    api_response = {
        "dvd_id": "abf030",
        "content_id": "118abf00030",
        "title_ja": "ABFタイトル",
        "release_date": "2024-06-01",
        "runtime_mins": 150,
        "maker_name_ja": "メーカーB",
        "actresses": [{"name_kanji": "女優B", "name_romaji": "Actress B"}],
        "categories": [{"name_ja": "カテゴリB", "name_en": "Category B"}],
        "jacket_full_url": "https://pics.dmm.co.jp/mono/abc/abcpl.jpg",
    }

    call_count = 0

    class FakeClient:
        async def get_json(self, url, **kwargs):
            nonlocal call_count
            call_count += 1
            if "dvd_id=" in url:
                return (None, "404")
            if "combined=" in url:
                return (api_response, "")
            return (None, "unknown url")

        async def get_text(self, url, **kwargs):
            return (None, "")

        async def request(self, *args, **kwargs):
            return (None, "")

    crawler = R18devCrawler(client=FakeClient())
    input_data = CrawlerInput.empty()
    input_data.number = "ABF-030"
    result = await crawler.run(input_data)

    assert result.data is not None
    assert result.data.number == "ABF-030"
    assert result.data.title == "ABFタイトル"
    assert result.data.studio == "メーカーB"
    assert call_count >= 2


@pytest.mark.asyncio
async def test_post_process_fixes_trailer():
    from mdcx.crawlers.base.types import CrawlerData

    crawler = R18devCrawler(client=None)
    data = CrawlerData(
        number="TEST-001",
        title="Test",
        trailer="//example.com/video.mp4",
    )
    result = data.to_result()
    result = await crawler.post_process(None, result)

    assert result.trailer == "https://example.com/video.mp4"


@pytest.mark.asyncio
async def test_post_process_fills_originaltitle():
    from mdcx.crawlers.base.types import CrawlerData

    crawler = R18devCrawler(client=None)
    data = CrawlerData(
        number="TEST-001",
        title="Test Title",
        originaltitle="",
    )
    result = data.to_result()
    result = await crawler.post_process(None, result)

    assert result.originaltitle == "Test Title"
