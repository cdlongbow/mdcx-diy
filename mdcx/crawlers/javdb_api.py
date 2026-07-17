import asyncio
import random
import re
import time
from typing import override
from urllib.parse import urljoin

import httpx
from parsel import Selector

from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, CrawlerData, CrawlerException, DetailPageParser, extract_all_texts, extract_text

# ============================================================
# NameNormalizer — 演员名规范化 (移植自 javdbapi ids.go)
# ============================================================

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
    "难": "難",
    "响": "響",
    "领": "領",
    "页": "頁",
    "风": "風",
    "飞": "飛",
    "馆": "館",
    "龙": "龍",
    "龟": "龜",
    "麦": "麥",
    "麻": "麻",
    "黄": "黃",
    "鱼": "魚",
    "鸟": "鳥",
    "鸡": "雞",
    "马": "馬",
    "骨": "骨",
    "高": "高",
    "鬼": "鬼",
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


def normalize_name(name: str) -> str:
    result = []
    for ch in name:
        if ch in _s2t_map:
            result.append(_s2t_map[ch])
        else:
            result.append(ch)
    for i, ch in enumerate(result):
        if ch in _alias_map:
            result[i] = _alias_map[ch]
    return "".join(result)


def chars_overlap(a: str, b: str) -> bool:
    set_a = set(a)
    for ch in b:
        if ch in set_a:
            return True
    return False


# ============================================================
# URLBuilder — URL 构造 (移植自 javdbapi internal/siteurl/build.go)
# ============================================================


def video_url(base_url: str, video_id: str) -> str:
    return f"{base_url}/v/{video_id}?locale=zh"


def search_url(base_url: str, keyword: str, page: int = 1) -> str:
    return f"{base_url}/search?q={keyword}&f=all&page={page}&locale=zh"


def search_actor_url(base_url: str, keyword: str, page: int = 1) -> str:
    return f"{base_url}/search?q={keyword}&f=actor&page={page}&locale=zh"


# ============================================================
# Parser — 详情页解析器
# ============================================================


class Parser(DetailPageParser):
    async def number(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//a[@class="button is-white copy-to-clipboard"]/@data-clipboard-text')
        return result or ctx.input.number

    async def title(self, ctx, html: Selector) -> str:
        return extract_text(html, 'string(//h2[@class="title is-4"]/strong[@class="current-title"])')

    async def originaltitle(self, ctx, html: Selector) -> str:
        return extract_text(html, 'string(//h2[@class="title is-4"]/span[@class="origin-title"])')

    async def actors(self, ctx, html: Selector) -> list[str]:
        return (
            html.css("span:has(strong.female)")
            .xpath("//strong[contains(@class, 'female')]/preceding-sibling::a/text()")
            .getall()
        )

    async def all_actors(self, ctx, html: Selector) -> list[str]:
        return (html.css("span:has(strong.female)") or html.css("span:has(strong.male)")).xpath("a/text()").getall()

    async def studio(self, ctx, html: Selector) -> str:
        return extract_text(
            html,
            '//strong[contains(text(),"片商:")]/../span/a/text()',
            '//strong[contains(text(),"Maker:")]/../span/a/text()',
        )

    async def publisher(self, ctx, html: Selector) -> str:
        return extract_text(
            html,
            '//strong[contains(text(),"發行:")]/../span/a/text()',
            '//strong[contains(text(),"Publisher:")]/../span/a/text()',
        )

    async def runtime(self, ctx, html: Selector) -> str:
        result = extract_text(
            html,
            '//strong[contains(text(),"時長")]/../span/text()',
            '//strong[contains(text(),"Duration:")]/../span/text()',
        )
        return result.replace(" 分鍾", "").replace(" minute(s)", "")

    async def series(self, ctx, html: Selector) -> str:
        return extract_text(
            html,
            '//strong[contains(text(),"系列:")]/../span/a/text()',
            '//strong[contains(text(),"Series:")]/../span/a/text()',
        )

    async def release(self, ctx, html: Selector) -> str:
        return extract_text(
            html,
            '//strong[contains(text(),"日期:")]/../span/text()',
            '//strong[contains(text(),"Released Date:")]/../span/text()',
        )

    async def year(self, ctx, html: Selector) -> str:
        release_date = await self.release(ctx, html)
        try:
            result = re.search(r"\d{4}", release_date)
            return result.group() if result else release_date
        except Exception:
            return release_date

    async def tags(self, ctx, html: Selector) -> list[str]:
        tags = extract_all_texts(
            html,
            '//strong[contains(text(),"類別:")]/../span/a/text()',
            '//strong[contains(text(),"Tags:")]/../span/a/text()',
        )
        tags = [tag.replace("\\xa0", "").replace("'", "").replace(" ", "").strip() for tag in tags if tag.strip()]
        return list(dict.fromkeys(tags))

    async def thumb(self, ctx, html: Selector) -> str:
        return extract_text(html, "//img[@class='video-cover']/@src")

    async def extrafanart(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, "//div[@class='tile-images preview-images']/a[@class='tile-item']/@href")

    async def trailer(self, ctx, html: Selector) -> str:
        return extract_text(html, "//video[@id='preview-video']/source/@src")

    async def directors(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(
            html,
            '//strong[contains(text(),"導演:")]/../span/a/text()',
            '//strong[contains(text(),"Director:")]/../span/a/text()',
        )

    async def score(self, ctx, html: Selector) -> str:
        result = extract_text(html, "//span[@class='score-stars']/../text()")
        try:
            score_match = re.search(r"(\d{1}\.\d+)", result)
            return score_match.group(1) if score_match else ""
        except Exception:
            return ""

    async def wanted(self, ctx, html: Selector) -> str:
        html_text = html.get()
        result = re.search(r"(\d+)(人想看| want to watch it)", html_text)
        return result.group(1) if result else ""

    async def image_download(self, ctx, html: Selector) -> bool:
        return False


# ============================================================
# JavdbApiCrawler — 主爬虫类
# ============================================================


_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/139.0.0.0 Safari/537.36"
)

_HTTPX_CLIENT = httpx.AsyncClient(
    headers={"User-Agent": _USER_AGENT},
    follow_redirects=True,
    timeout=30.0,
)


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
        return manager.config.get_site_url(Website.JAVDB_API, "https://javdb.com")

    @override
    def _get_headers(self, ctx) -> dict[str, str] | None:
        cookie = manager.config.javdb
        if cookie:
            return {"cookie": cookie, "User-Agent": _USER_AGENT}

    @staticmethod
    def _build_headers() -> dict[str, str]:
        cookie = manager.config.javdb
        headers = {"User-Agent": _USER_AGENT}
        if cookie:
            headers["cookie"] = cookie
        return headers

    async def _throttle_page_request(self, ctx, request_type: str, url: str) -> None:
        now = time.monotonic()
        if self._last_page_request_at > 0:
            interval = random.uniform(2.0, 3.0)
            wait_seconds = interval - (now - self._last_page_request_at)
            if wait_seconds > 0:
                ctx.debug(f"JavdbApi 请求限流({request_type})，等待 {wait_seconds:.2f}s: {url}")
                await asyncio.sleep(wait_seconds)
        self._last_page_request_at = time.monotonic()

    async def _httpx_get(self, url: str, ctx) -> str | None:
        async with self._page_request_lock:
            await self._throttle_page_request(ctx, "HTTP", url)
            try:
                resp = await _HTTPX_CLIENT.get(url, headers=self._build_headers())
                if resp.status_code == 403:
                    body = resp.text
                    if "ray-id" in body or "cdn-cgi/challenge-platform" in body:
                        ctx.debug(f"JavdbApi 触发 Cloudflare 拦截: {url}")
                        return None
                resp.raise_for_status()
                return resp.text
            except httpx.HTTPStatusError as e:
                ctx.debug(f"JavdbApi HTTP 错误 {e.response.status_code}: {url}")
                return None
            except httpx.RequestError as e:
                ctx.debug(f"JavdbApi 请求异常: {e}")
                return None

    @override
    async def _fetch_search(self, ctx, url: str, use_browser: bool | None = False) -> tuple[str | None, str]:
        html = await self._httpx_get(url, ctx)
        if html is None:
            return None, "JavdbApi: 搜索页请求失败"
        return html, ""

    @override
    async def _fetch_detail(self, ctx, url: str, use_browser: bool | None = False) -> tuple[str | None, str]:
        html = await self._httpx_get(url, ctx)
        if html is None:
            return None, "JavdbApi: 详情页请求失败"
        return html, ""

    @override
    async def _generate_search_url(self, ctx) -> list[str]:
        number = ctx.input.number.strip()
        if "." in number:
            m = re.search(r"\D+(\d{2}\.\d{2}\.\d{2})$", number)
            if m:
                old_date = m.group(1)
                new_date = "20" + old_date.replace(".", "")
                number = number.replace(old_date, new_date)
        search_url = f"{self.base_url}/search?q={number}&locale=zh"
        ctx.debug(f"搜索地址: {search_url}")
        return [search_url]

    @override
    async def _parse_search_page(self, ctx, html: Selector, search_url: str) -> list[str] | None:
        html_text = html.get()
        if "ray-id" in html_text or "cdn-cgi/challenge-platform" in html_text:
            raise CrawlerException(
                "搜索结果: 被 Cloudflare 5 秒盾拦截！请尝试更换cookie或使用其他域名！"
            )
        if "The owner of this website has banned your access" in html_text:
            raise CrawlerException(
                f"由于请求过多，javdb网站暂时禁止了你当前IP的访问！！点击 {search_url} 查看详情！"
            )
        if "Due to copyright restrictions" in html_text:
            raise CrawlerException(
                f"由于版权限制，javdb网站禁止了日本IP的访问！！请更换日本以外代理！点击 {search_url} 查看详情！"
            )

        res_list = html.xpath("//a[@class='box']")
        if not res_list:
            return None

        info_list = []
        for each in res_list:
            href = extract_text(each, "@href")
            title = extract_text(each, "div[@class='video-title']/strong/text()")
            meta = extract_text(each, "div[@class='meta']/text()")
            if href:
                info_list.append([href, title, meta])

        number = ctx.input.number
        for href, title, meta in info_list:
            if number.upper() in title.upper():
                return [urljoin(self.base_url, href)]

        clean_number = number.upper().replace(".", "").replace("-", "").replace(" ", "")
        for href, title, meta in info_list:
            clean_content = (title + meta).upper().replace("-", "").replace(".", "").replace(" ", "")
            if clean_number in clean_content:
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
        if res.thumb:
            res.poster = res.thumb.replace("/covers/", "/thumbs/")
        res.mosaic = "无码" if any(keyword in res.title for keyword in ["無碼", "無修正", "Uncensored"]) else "有码"
        if res.trailer and res.trailer.startswith("//"):
            res.trailer = "https:" + res.trailer
        return res

    async def close(self):
        await _HTTPX_CLIENT.aclose()
