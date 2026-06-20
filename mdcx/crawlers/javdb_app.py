import asyncio
import base64
import hashlib
import json
import random
import time
from typing import override

from pydantic import BaseModel, ConfigDict

from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, Context, CrawlerData, CrawlerException

# ============================================================
# 签名算法 - 基于 JavDB 移动端 APK 逆向
# ============================================================

_SECRET = "30820"

_ENCRYPTED_PART1 = "WzE3OCwyMTksMTI3LDE2MSwxODksMTYyLDEyMywxMDMsMTM3LDIxMCwxMjMsMjE5LDE4OSwxNzksMTIzLDIwMiwxMzksMTUwLDEzMywxNjAsMTI2LDIwNywxNjYsMTUxLDE0NiwxNTksMTg4LDEwMCwxMzgsMTM2LDE3NiwxNjEsMTQyLDEwMywxMzUsMTYwLDE0MiwxNzUsMTYwLDEwNCwxMzAsMTIxLDExOCwxMDYsMTMyLDEyNCwxMzAsMTA0LDEzMSwxMjEsMTI2LDE3MywxNDMsMTQwLDEzOCwxMDQsMTMwLDE1OSwxMTgsMTc1LDE0MiwxNTksMTYxLDE1OSwxNDMsMTI0LDEyMywxNjEsMTMxLDEzNywxMzQsMTAxLDEzMSwxNzUsMTU2LDEwMSwxMzEsMTc1LDE1NywxNTcsMTMwLDEzNywxNjAsMTA2LDE0MywxMzcsMTUzLDE2MCwxMzEsMTQwLDEyMiwxMDMsMTQzLDEzNywxMjMsMTU3LDEzMSwxMzcsMTUyLDEwMywxMzIsMTM3LDEyMiwxNzMsMTMwLDE1OSwxMzEsMTU5LDEzMCwxNDAsMTIyLDEwNiwxMzAsMTc1LDEyMywxNTksMTMwLDEyMSwxMzgsMTA0LDEzMiwxMjEsMTM0LDE3NCwxNDMsMTYyLDEyNiwxMDQsMTMwLDEwMywxMjcsMTU3LDEzMCwxMDMsMTI2LDE3NSwxNDIsMTc1LDE1NiwxNzUsMTQyLDE2MiwxMzEsMTYwLDEzMSwxNTksMTYxLDE1OSwxMzAsMTM3LDE1MywxNTksMTQyLDEwMywxNDIsMTczLDEzMSwxNzUsMTM0LDE3MiwxMzIsMTIxLDEyMywxNjEsMTMwLDEwMywxMzQsMTA1LDE0MiwxNDAsMTIyLDExNF0="
_ENCRYPTED_PART2 = "WzE5OCwxNjksMTIzLDEwNiwxNzcsMTY2LDE0MCwxNjIsMTQ3LDE4OSwxNjIsMjE5LDE5OSwxMjIsMTE4LDE1OF0="

_API_BASE = "https://apidd.czssdgz.com"
_API_FALLBACKS = ["https://apidd.spthgb.com", "https://jdforrepam.com"]

_PLATFORM = "android"
_APP_CHANNEL = "official"
_APP_VERSION = "official"
_APP_VERSION_NUMBER = "1.9.35"


def _decrypt(b64_encrypted: str) -> str:
    key_md5 = hashlib.md5(_SECRET.encode()).hexdigest()
    key_bytes = [ord(c) for c in key_md5]
    encrypted = json.loads(base64.b64decode(b64_encrypted))
    raw = "".join(chr(encrypted[i] - key_bytes[min(i, 31)]) for i in range(len(encrypted)))
    return base64.b64decode(raw).decode()


def make_signature() -> str:
    part1 = _decrypt(_ENCRYPTED_PART1)
    part2 = _decrypt(_ENCRYPTED_PART2)
    ts = int(time.time())
    md5_hash = hashlib.md5(f"{ts}{part1}".encode()).hexdigest()
    return f"{ts}.{part2}.{md5_hash}"


def _build_api_params() -> dict:
    return {
        "platform": _PLATFORM,
        "app_channel": _APP_CHANNEL,
        "app_version": _APP_VERSION,
        "app_version_number": _APP_VERSION_NUMBER,
    }


def _get_api_url(host: str, path: str, params: dict | None = None) -> str:
    from urllib.parse import urlencode

    query = _build_api_params()
    if params:
        query.update(params)
    return f"{host}{path}?{urlencode(query)}"


class MovieSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    number: str | None = None
    title: str | None = None
    origin_title: str | None = None
    thumb_url: str | None = None
    cover_url: str | None = None
    duration: int | None = None
    release_date: str | None = None
    has_cnsub: bool | None = None


class MovieDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    number: str | None = None
    title: str | None = None
    origin_title: str | None = None
    summary: str | None = None
    thumb_url: str | None = None
    cover_url: str | None = None
    duration: int | None = None
    score: str | None = None
    release_date: str | None = None
    maker_name: str | None = None
    director_name: str | None = None
    publisher_name: str | None = None
    series_name: str | None = None
    tags: list | None = None
    actors: list | None = None
    preview_images: list | None = None
    preview_video_url: str | None = None
    share_info: str | None = None


# ============================================================
# 爬虫实现
# ============================================================


class JavdbAPICrawler(BaseCrawler):
    def __init__(self, client, base_url="", browser=None):
        super().__init__(client, base_url, browser)
        self._request_lock = asyncio.Lock()
        self._last_request_at = 0.0

    @staticmethod
    def _log(message: str) -> None:
        from ..signals import signal

        signal.add_log(f"[JavdbAPI] {message}")

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.JAVDB_APP

    @classmethod
    @override
    def base_url_(cls) -> str:
        return manager.config.get_site_url(Website.JAVDB_APP, _API_BASE)

    @staticmethod
    def _ensure_https(url: str) -> str:
        if url and not url.startswith("http"):
            return "https:" + url
        return url or ""

    @staticmethod
    def _clean_str(value: str | None) -> str:
        if not value:
            return ""
        return value.strip()

    @staticmethod
    def _clean_int(value: int | None) -> str:
        if value is None or value <= 0:
            return ""
        return str(value)

    async def _request_api(self, path: str, params: dict | None = None) -> dict | None:
        hosts = [_API_BASE] + _API_FALLBACKS
        signature = make_signature()
        headers = {
            "jdsignature": signature,
            "accept-language": "zh",
            "User-Agent": "Dart/3.5 (dart:io)",
        }

        async with self._request_lock:
            if self._last_request_at > 0:
                elapsed = time.monotonic() - self._last_request_at
                delay = random.uniform(3.0, 8.0)
                if elapsed < delay:
                    await asyncio.sleep(delay - elapsed)
            self._last_request_at = time.monotonic()

        last_error = None
        for host in hosts:
            url = _get_api_url(host, path, params)
            try:
                resp, error = await self.async_client.get_json(url, headers=headers)
                if resp is not None:
                    return resp
                last_error = error
            except Exception as e:
                last_error = str(e)
                continue

        self._log(f"API 请求失败: {last_error}")
        return None

    @override
    async def _run(self, ctx: Context) -> CrawlerResult:
        number = self._clean_str(ctx.input.number)
        if not number:
            raise CrawlerException("番号为空")

        # Step 1: Search for the movie by number
        search_resp = await self._request_api("/api/v2/search", {"q": number, "page": "1"})
        if not search_resp:
            raise CrawlerException("搜索请求失败")

        # API response wraps data in "data" key
        search_data_raw = search_resp.get("data", {})
        movies_raw = search_data_raw.get("movies", [])
        if not movies_raw:
            raise CrawlerException("未找到匹配的影片")

        movies = [MovieSummary(**m) for m in movies_raw]

        # Find exact match by number (case-insensitive)
        movie_id = None
        for movie in movies:
            if movie.number and movie.number.upper() == number.upper():
                movie_id = movie.id
                break

        if not movie_id:
            # Use first result if no exact match
            movie_id = movies[0].id

        if not movie_id:
            raise CrawlerException("无法确定影片 ID")

        ctx.debug(f"找到影片 ID: {movie_id}")

        # Step 2: Get movie detail
        detail_resp = await self._request_api(f"/api/v4/movies/{movie_id}")
        if not detail_resp:
            raise CrawlerException("详情请求失败")

        # API response wraps data in "data" key
        detail_data_raw = detail_resp.get("data", {})
        movie_raw = detail_data_raw.get("movie", {})
        if not movie_raw:
            raise CrawlerException("详情数据为空")

        try:
            movie = MovieDetail(**movie_raw)
        except Exception as e:
            ctx.debug(f"详情响应解析失败: {e} {movie_raw=}")
            raise CrawlerException("详情响应解析失败") from e

        # Step 3: Build CrawlerData
        data = CrawlerData(
            number=self._clean_str(movie.number),
            title=self._clean_str(movie.title),
            originaltitle=self._clean_str(movie.origin_title),
            outline=self._clean_str(movie.summary),
            thumb=self._ensure_https(self._clean_str(movie.thumb_url)),
            poster=self._ensure_https(self._clean_str(movie.cover_url)),
            release=self._clean_str(movie.release_date),
            runtime=self._clean_int(movie.duration),
            score=self._clean_str(movie.score),
            studio=self._clean_str(movie.maker_name),
            directors=[self._clean_str(movie.director_name)] if movie.director_name else [],
            publisher=self._clean_str(movie.publisher_name),
            series=self._clean_str(movie.series_name),
            tags=(
                [
                    self._clean_str(tag.get("name"))
                    for tag in (movie.tags or [])
                    if tag and self._clean_str(tag.get("name"))
                ]
                if movie.tags
                else []
            ),
            actors=(
                [
                    self._clean_str(actor.get("name"))
                    for actor in (movie.actors or [])
                    if actor and self._clean_str(actor.get("name"))
                ]
                if movie.actors
                else []
            ),
            all_actors=(
                [
                    self._clean_str(actor.get("name"))
                    for actor in (movie.actors or [])
                    if actor and self._clean_str(actor.get("name"))
                ]
                if movie.actors
                else []
            ),
            extrafanart=[
                self._ensure_https(img.get("thumb_url") or img.get("large_url", ""))
                for img in (movie.preview_images or [])
                if img
            ],
            trailer=self._ensure_https(self._clean_str(movie.preview_video_url)),
            external_id=f"https://javdb573.com/v/{movie_id}",
        )

        # Set image_download to True if we have cover/thumb URLs
        if data.thumb or data.poster:
            data.image_download = True

        data.source = self.site().value
        result = data.to_result()
        return await self.post_process(ctx, result)

    @override
    async def _generate_search_url(self, ctx: Context):
        raise NotImplementedError

    @override
    async def _parse_search_page(self, ctx: Context, html, search_url: str):
        raise NotImplementedError

    @override
    async def _parse_detail_page(self, ctx: Context, html, detail_url: str):
        raise NotImplementedError

    @override
    async def post_process(self, ctx: Context, res: CrawlerResult) -> CrawlerResult:
        if not res.originaltitle:
            res.originaltitle = res.title
        if res.runtime:
            res.year = res.release[:4] if res.release else ""
        return res
