import asyncio
import random
import re
import time
from typing import override
from urllib.parse import urlencode, urljoin

from parsel import Selector

from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, CrawlerData, CrawlerException, DetailPageParser, extract_all_texts, extract_text

_DEFAULT_BASE = "https://javdb573.com"

_SELECTOR_LIST_ITEM = "//a[@class='box']"
_SELECTOR_LIST_CODE = "div[@class='video-title']/strong/text()"
_SELECTOR_LIST_TITLE = "div[@class='video-title']/text()"
_SELECTOR_LIST_DATE = "div[@class='meta']/text()"
_SELECTOR_LIST_SCORE = "div[@class='score']/text()"
_SELECTOR_LIST_COVER = "div[@class='cover']/img/@src"

_SELECTOR_DETAIL_TITLE = "//h2[@class='title is-4']/strong[@class='current-title']/text()"
_SELECTOR_DETAIL_ORIGIN_TITLE = "//h2[@class='title is-4']/span[@class='origin-title']/text()"
_SELECTOR_COVER = "//img[@class='video-cover']/@src"
_SELECTOR_EXTRAFANART = "//div[@class='preview-images']/a[@class='tile-item']/@href"
_SELECTOR_TRAILER = "//video[@id='preview-video']/source/@src"
_SELECTOR_CLIPBOARD = "//a[@class='button is-white copy-to-clipboard']/@data-clipboard-text"

_SELECTOR_SCORE_STARS = "//span[@class='score-stars']/../text()"

_SELECTOR_PANEL_LABELS = {
    "director": '//strong[contains(text(),"導演:")]/../span/a/text()',
    "maker": '//strong[contains(text(),"片商:")]/../span/a/text()',
    "publisher": '//strong[contains(text(),"發行:")]/../span/a/text()',
    "series": '//strong[contains(text(),"系列:")]/../span/a/text()',
    "date": '//strong[contains(text(),"日期:")]/../span/text()',
    "duration": '//strong[contains(text(),"時長")]/../span/text()',
    "tags": '//strong[contains(text(),"類別:")]/../span/a/text()',
}

_SELECTOR_DIRECTOR_EN = '//strong[contains(text(),"Director:")]/../span/a/text()'
_SELECTOR_MAKER_EN = '//strong[contains(text(),"Maker:")]/../span/a/text()'
_SELECTOR_PUBLISHER_EN = '//strong[contains(text(),"Publisher:")]/../span/a/text()'
_SELECTOR_SERIES_EN = '//strong[contains(text(),"Series:")]/../span/a/text()'
_SELECTOR_DATE_EN = '//strong[contains(text(),"Released Date:")]/../span/text()'
_SELECTOR_DURATION_EN = '//strong[contains(text(),"Duration:")]/../span/text()'
_SELECTOR_TAGS_EN = '//strong[contains(text(),"Tags:")]/../span/a/text()'

_SELECTOR_ACTOR_FEMALE = "//strong[contains(@class, 'female')]/preceding-sibling::a/text()"
_SELECTOR_ACTOR_ALL = "//span[strong[contains(@class, 'female')] or strong[contains(@class, 'male')]]/a/text()"

_SELECTOR_WANTED = r"(\d+)(人想看| want to watch it)"

_s2t_map = {
    "斋": "齋",
    "咏": "詠",
    "艺": "藝",
    "冯": "馮",
    "陈": "陳",
    "驿": "驛",
    "苍": "蒼",
    "罗": "羅",
    "条": "條",
    "东": "東",
    "么": "麼",
    "广": "廣",
    "发": "發",
    "义": "義",
    "乌": "烏",
    "书": "書",
    "务": "務",
    "备": "備",
    "复": "復",
    "与": "與",
    "丑": "醜",
    "刘": "劉",
    "卫": "衛",
    "动": "動",
    "协": "協",
    "单": "單",
    "卖": "賣",
    "围": "圍",
    "图": "圖",
    "国": "國",
    "团": "團",
    "园": "園",
    "钟": "鐘",
    "银": "銀",
    "镜": "鏡",
    "长": "長",
    "门": "門",
    "间": "間",
    "阵": "陣",
    "队": "隊",
    "阳": "陽",
    "阴": "陰",
    "响": "響",
    "领": "領",
    "页": "頁",
    "风": "風",
    "飞": "飛",
    "馆": "館",
    "龙": "龍",
    "龟": "龜",
    "麦": "麥",
    "黄": "黃",
    "鱼": "魚",
    "鸟": "鳥",
    "鸡": "雞",
    "马": "馬",
    "齐": "齊",
    "韩": "韓",
    "驱": "驅",
    "岛": "島",
    "爱": "愛",
    "优": "優",
    "樱": "櫻",
    "乡": "鄉",
    "枫": "楓",
    "泽": "澤",
    "结": "結",
    "桥": "橋",
    "圣": "聖",
    "宫": "宮",
    "绪": "緒",
    "铃": "鈴",
}

_alias_map = {
    "筱": "篠",
    "穗": "穂",
    "理": "裏",
    "户": "戸",
}


def normalize_actor_name(name: str) -> str:
    runes = list(name)
    for i, ch in enumerate(runes):
        if ch in _s2t_map:
            runes[i] = _s2t_map[ch]
    for i, ch in enumerate(runes):
        if ch in _alias_map:
            runes[i] = _alias_map[ch]
    return "".join(runes)


class Parser(DetailPageParser):
    async def number(self, ctx, html: Selector) -> str:
        result = extract_text(html, _SELECTOR_CLIPBOARD)
        return result or ctx.input.number

    async def title(self, ctx, html: Selector) -> str:
        return extract_text(html, _SELECTOR_DETAIL_TITLE)

    async def originaltitle(self, ctx, html: Selector) -> str:
        return extract_text(html, _SELECTOR_DETAIL_ORIGIN_TITLE)

    async def actors(self, ctx, html: Selector) -> list[str]:
        return html.xpath(_SELECTOR_ACTOR_FEMALE).getall()

    async def all_actors(self, ctx, html: Selector) -> list[str]:
        return html.xpath(_SELECTOR_ACTOR_ALL).getall()

    async def studio(self, ctx, html: Selector) -> str:
        return extract_text(html, _SELECTOR_PANEL_LABELS["maker"], _SELECTOR_MAKER_EN)

    async def publisher(self, ctx, html: Selector) -> str:
        return extract_text(html, _SELECTOR_PANEL_LABELS["publisher"], _SELECTOR_PUBLISHER_EN)

    async def runtime(self, ctx, html: Selector) -> str:
        result = extract_text(html, _SELECTOR_PANEL_LABELS["duration"], _SELECTOR_DURATION_EN)
        return result.replace(" 分鍾", "").replace(" minute(s)", "")

    async def series(self, ctx, html: Selector) -> str:
        return extract_text(html, _SELECTOR_PANEL_LABELS["series"], _SELECTOR_SERIES_EN)

    async def release(self, ctx, html: Selector) -> str:
        return extract_text(html, _SELECTOR_PANEL_LABELS["date"], _SELECTOR_DATE_EN)

    async def year(self, ctx, html: Selector) -> str:
        release_date = await self.release(ctx, html)
        try:
            result = re.search(r"\d{4}", release_date)
            return result.group() if result else release_date
        except Exception:
            return release_date

    async def tags(self, ctx, html: Selector) -> list[str]:
        tags = extract_all_texts(html, _SELECTOR_PANEL_LABELS["tags"], _SELECTOR_TAGS_EN)
        return list(dict.fromkeys(tags))

    async def thumb(self, ctx, html: Selector) -> str:
        return extract_text(html, _SELECTOR_COVER)

    async def extrafanart(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, _SELECTOR_EXTRAFANART)

    async def trailer(self, ctx, html: Selector) -> str:
        return extract_text(html, _SELECTOR_TRAILER)

    async def directors(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, _SELECTOR_PANEL_LABELS["director"], _SELECTOR_DIRECTOR_EN)

    async def score(self, ctx, html: Selector) -> str:
        result = extract_text(html, _SELECTOR_SCORE_STARS)
        try:
            score_match = re.search(r"(\d{1}\.\d+)", result)
            return score_match.group(1) if score_match else ""
        except Exception:
            return ""

    async def wanted(self, ctx, html: Selector) -> str:
        html_text = html.get()
        result = re.search(_SELECTOR_WANTED, html_text)
        return result.group(1) if result else ""

    async def image_download(self, ctx, html: Selector) -> bool:
        return False


class JavdbApiCrawler(BaseCrawler):
    parser = Parser()

    def __init__(self, client, base_url: str = "", browser=None):
        super().__init__(client=client, base_url=base_url, browser=browser)
        self._page_request_lock = asyncio.Lock()
        self._last_page_request_at = 0.0

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.JAVDB_API

    @classmethod
    @override
    def base_url_(cls) -> str:
        return manager.config.get_site_url(Website.JAVDB_API, _DEFAULT_BASE)

    @override
    def _get_headers(self, ctx) -> dict[str, str] | None:
        if manager.config.javdb:
            return {"cookie": manager.config.javdb}

    async def _throttle_page_request(self, ctx, request_type: str, url: str) -> None:
        now = time.monotonic()
        if self._last_page_request_at > 0:
            interval = random.uniform(1.0, 2.0)
            wait_seconds = interval - (now - self._last_page_request_at)
            if wait_seconds > 0:
                ctx.debug(f"JavdbApi 请求限流({request_type})，等待 {wait_seconds:.2f}s: {url}")
                await asyncio.sleep(wait_seconds)
        self._last_page_request_at = time.monotonic()

    @override
    async def _fetch_search(self, ctx, url: str, use_browser: bool | None = False) -> tuple[str | None, str]:
        async with self._page_request_lock:
            await self._throttle_page_request(ctx, "搜索", url)
            return await self.async_client.get_text(url, headers=self._get_headers(ctx), use_proxy=False)

    @override
    async def _fetch_detail(self, ctx, url: str, use_browser: bool | None = False) -> tuple[str | None, str]:
        async with self._page_request_lock:
            await self._throttle_page_request(ctx, "详情", url)
            return await self.async_client.get_text(url, headers=self._get_headers(ctx), use_proxy=False)

    @override
    async def _generate_search_url(self, ctx) -> list[str]:
        number = ctx.input.number.strip()
        if "." in number:
            old_date = re.findall(r"\D+(\d{2}\.\d{2}\.\d{2})$", number)
            if old_date:
                new_date = "20" + old_date[0]
                number = number.replace(old_date[0], new_date)
        params = urlencode({"f": "all", "q": number, "page": "1"})
        search_url = f"{self.base_url}/search?{params}"
        ctx.debug(f"JavdbApi 搜索地址: {search_url}")
        return [search_url]

    @override
    async def _parse_search_page(self, ctx, html: Selector, search_url: str) -> list[str] | None:
        html_text = html.get() or ""
        if "The owner of this website has banned your access" in html_text:
            raise CrawlerException(f"Javdb 镜像站禁止了当前 IP 的访问！{search_url}")
        if "Due to copyright restrictions" in html_text:
            raise CrawlerException("Javdb 镜像站版权限制，禁止日本 IP 访问！")
        if "ray-id" in html_text or "Just a moment" in html_text:
            raise CrawlerException("Javdb 镜像站被 Cloudflare 拦截，请尝试更换镜像站！")

        res_list = html.xpath(_SELECTOR_LIST_ITEM)
        if not res_list:
            return None

        info_list = []
        for each in res_list:
            href = extract_text(each, "@href")
            code = extract_text(each, _SELECTOR_LIST_CODE)
            title = extract_text(each, _SELECTOR_LIST_TITLE) or code
            meta = extract_text(each, _SELECTOR_LIST_DATE)
            if href:
                info_list.append((href, code, title, meta))

        if not info_list:
            return None

        number = ctx.input.number
        norm_target = number.upper().replace("-", "").replace(".", "").replace(" ", "")

        for href, code, title, meta in info_list:
            if number.upper() in (code or "").upper() or number.upper() in (title or "").upper():
                return [urljoin(self.base_url, href)]

        for href, code, title, meta in info_list:
            combined = (
                ((code or "") + (title or "") + (meta or "")).upper().replace("-", "").replace(".", "").replace(" ", "")
            )
            if norm_target in combined:
                return [urljoin(self.base_url, href)]

        return None

    @override
    async def _parse_detail_page(self, ctx, html: Selector, detail_url: str) -> CrawlerData | None:
        javdbid = ""
        if r := re.search(r"/v/([a-zA-Z0-9]+)", detail_url):
            javdbid = r.group(1)
        return await self.parser.parse(ctx, html, external_id=javdbid)

    @override
    async def post_process(self, ctx, res: CrawlerResult) -> CrawlerResult:
        if not res.originaltitle:
            res.originaltitle = res.title
        res.poster = res.thumb.replace("/covers/", "/thumbs/")
        res.mosaic = "无码" if any(kw in res.title for kw in ["無碼", "無修正", "Uncensored"]) else "有码"
        if res.trailer and res.trailer.startswith("//"):
            res.trailer = "https:" + res.trailer
        return res

    @classmethod
    @override
    def display_name(cls) -> str:
        return "JavDB API"

    @classmethod
    @override
    def supports_custom_url(cls) -> bool:
        return True
