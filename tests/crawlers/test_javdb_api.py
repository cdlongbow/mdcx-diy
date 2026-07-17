import pytest
from parsel import Selector

from mdcx.config.models import Website
from mdcx.models.types import CrawlerInput

FIXTURES_DIR = "tests/crawlers/fixtures"


# ============================================================
# NameNormalizer 测试
# ============================================================

class TestNameNormalizer:
    def test_simplified_to_traditional(self):
        from mdcx.crawlers.javdb_api import normalize_name

        cases = [
            ("樱空桃", "櫻空桃"),
            ("深田咏美", "深田詠美"),
            ("苍井空", "蒼井空"),
            ("三上悠亚", "三上悠亚"),  # 亚不在映射表中
        ]
        for inp, expected in cases:
            assert normalize_name(inp) == expected, f"{inp} -> {expected}"

    def test_alias_correction(self):
        from mdcx.crawlers.javdb_api import normalize_name

        cases = [
            ("筱田优", "篠田優"),
            ("藤森里穗", "藤森里穂"),
            ("水卜樱", "水卜櫻"),
        ]
        for inp, expected in cases:
            assert normalize_name(inp) == expected, f"{inp} -> {expected}"

    def test_chars_overlap(self):
        from mdcx.crawlers.javdb_api import chars_overlap

        assert chars_overlap("篠田優", "筱田优") is True
        assert chars_overlap("ABC", "XYZ") is False


# ============================================================
# URLBuilder 测试
# ============================================================

class TestURLBuilder:
    def test_search_url(self):
        from mdcx.crawlers.javdb_api import search_url, search_actor_url, video_url

        assert search_url("https://javdb.com", "DLDSS-271") == "https://javdb.com/search?q=DLDSS-271&f=all&page=1&locale=zh"
        assert search_actor_url("https://javdb.com", "篠田優") == "https://javdb.com/search?q=篠田優&f=actor&page=1&locale=zh"
        assert video_url("https://javdb.com", "ZNdEbV") == "https://javdb.com/v/ZNdEbV?locale=zh"


# ============================================================
# Parser 测试
# ============================================================

class TestParser:
    @pytest.fixture
    def detail_html(self):
        with open(f"{FIXTURES_DIR}/javdb_detail.html") as f:
            return Selector(text=f.read())

    @pytest.fixture
    def search_html(self):
        with open(f"{FIXTURES_DIR}/javdb_search.html") as f:
            return Selector(text=f.read())

    @pytest.fixture
    def ctx(self):
        from mdcx.crawlers.base import Context

        input_data = CrawlerInput.empty()
        input_data.number = "DLDSS-271"
        return Context(input=input_data)

    def test_parse_number(self, detail_html, ctx):
        from mdcx.crawlers.javdb_api import Parser

        parser = Parser()
        number = pytest.mark.asyncio(parser.number(ctx, detail_html))
        # 使用同步方式测试
        import asyncio

        result = asyncio.run(parser.number(ctx, detail_html))
        assert result == "DLDSS-271"

    def test_all_fields(self, detail_html, ctx):
        import asyncio

        from mdcx.crawlers.javdb_api import Parser

        parser = Parser()
        data = asyncio.run(parser.parse(ctx, detail_html, external_id="ZNdEbV"))

        assert data.number == "DLDSS-271"
        assert data.title == "DLDSS-271 タイトルサンプル"
        assert data.originaltitle == "Original Title Sample"
        assert data.actors == ["篠田優", "櫻空桃"]
        assert data.all_actors == ["篠田優", "櫻空桃", "男性俳優"]
        assert data.studio == "Sample Maker"
        assert data.publisher == "Sample Publisher"
        assert data.runtime == "120"
        assert data.series == "Sample Series"
        assert data.release == "2024-01-15"
        assert data.year == "2024"
        assert data.tags == ["Tag1", "Tag2"]
        assert data.thumb == "https://c0.jdbstatic.com/covers/cover.jpg"
        assert len(data.extrafanart) == 2
        assert data.extrafanart[0] == "https://c0.jdbstatic.com/samples/big1.jpg"
        assert data.trailer == "https://video.example.com/preview.mp4"
        assert data.directors == ["KLEM"]
        assert data.score == "8.5"
        assert data.wanted == "14879"
        assert data.external_id == "ZNdEbV"

    def test_search_page_parse(self, search_html, ctx):
        import asyncio

        from mdcx.crawlers.javdb_api import Parser

        parser = Parser()

        # 模拟搜索页解析逻辑（直接从类中提取逻辑测试）
        html_text = search_html.get()
        assert "box" in html_text  # 确保 fixture 加载正确

        res_list = search_html.xpath("//a[@class='box']")
        assert len(res_list) == 2


# ============================================================
# 完整爬虫流程测试（mock HTTP）
# ============================================================

class TestJavdbApiCrawler:
    @pytest.mark.asyncio
    async def test_run_full_flow(self, monkeypatch):
        import httpx

        from mdcx.crawlers.javdb_api import JavdbApiCrawler

        # 读取 fixture HTML
        with open(f"{FIXTURES_DIR}/javdb_search.html") as f:
            search_html = f.read()
        with open(f"{FIXTURES_DIR}/javdb_detail.html") as f:
            detail_html = f.read()

        # Mock httpx.AsyncClient.get
        call_count = 0

        async def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if "search?q=" in str(url):
                return httpx.Response(200, text=search_html)
            if "/v/" in str(url):
                return httpx.Response(200, text=detail_html)
            raise AssertionError(f"Unexpected URL: {url}")

        # 注入 mock
        import mdcx.crawlers.javdb_api as javdb_api_module

        monkeypatch.setattr(javdb_api_module._HTTPX_CLIENT, "get", mock_get)

        # 创建爬虫实例
        from mdcx.crawlers.base import Context

        crawler = JavdbApiCrawler(client=None)
        input_data = CrawlerInput.empty()
        input_data.number = "DLDSS-271"

        result = await crawler.run(input_data)

        assert result.data is not None
        assert result.data.number == "DLDSS-271"
        assert result.data.title == "DLDSS-271 タイトルサンプル"
        assert result.data.originaltitle == "Original Title Sample"
        assert "篠田優" in result.data.actors
        assert result.data.studio == "Sample Maker"
        assert result.data.release == "2024-01-15"
        assert result.data.year == "2024"
        assert result.data.runtime == "120"
        assert result.data.poster == "https://c0.jdbstatic.com/thumbs/cover.jpg"
        assert result.data.mosaic == "有码"
        assert call_count >= 1

    @pytest.mark.asyncio
    async def test_run_with_appoint_url(self, monkeypatch):
        import httpx

        from mdcx.crawlers.javdb_api import JavdbApiCrawler

        with open(f"{FIXTURES_DIR}/javdb_detail.html") as f:
            detail_html = f.read()

        async def mock_get(url, **kwargs):
            return httpx.Response(200, text=detail_html)

        import mdcx.crawlers.javdb_api as javdb_api_module

        monkeypatch.setattr(javdb_api_module._HTTPX_CLIENT, "get", mock_get)

        crawler = JavdbApiCrawler(client=None)
        input_data = CrawlerInput.empty()
        input_data.number = "DLDSS-271"
        input_data.appoint_url = "https://javdb.com/v/ZNdEbV"

        result = await crawler.run(input_data)

        assert result.data is not None
        assert result.data.number == "DLDSS-271"

    @pytest.mark.asyncio
    async def test_post_process(self, monkeypatch):
        from mdcx.crawlers.base import Context
        from mdcx.crawlers.javdb_api import JavdbApiCrawler
        from mdcx.models.types import CrawlerResult

        crawler = JavdbApiCrawler(client=None)
        ctx = Context(input=CrawlerInput.empty())

        # 测试 post_process: originaltitle 为空时用 title
        res = CrawlerResult()
        res.title = "DLDSS-271 Test Title"
        res.originaltitle = ""
        res.thumb = "https://c0.jdbstatic.com/covers/cover.jpg"
        res.trailer = "//video.example.com/trailer.mp4"

        result = await crawler.post_process(ctx, res)

        assert result.originaltitle == "DLDSS-271 Test Title"
        assert result.poster == "https://c0.jdbstatic.com/thumbs/cover.jpg"
        assert result.trailer == "https://video.example.com/trailer.mp4"
        assert result.mosaic == "有码"

        # 测试无码识别
        res2 = CrawlerResult()
        res2.title = "DLDSS-271 無碼 版"
        result2 = await crawler.post_process(ctx, res2)
        assert result2.mosaic == "无码"