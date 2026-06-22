#!/usr/bin/python
from typing import Any, override

from ..config.manager import manager
from ..config.models import Website
from .base import BaseCrawler, Context, CrawlerData, CrawlerException


class XcityCrawler(BaseCrawler):
    _cached_program: dict[str, Any] | None = None

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.XCITY

    @classmethod
    @override
    def base_url_(cls) -> str:
        return manager.config.get_site_url(Website.XCITY, "https://tc.xcity.jp")

    @override
    async def _generate_search_url(self, ctx: Context) -> list[str] | str | None:
        return f"{self.base_url}/api/search?q={ctx.input.number.replace('-', '')}"

    @override
    async def _parse_search_page(self, ctx: Context, html: Any, search_url: str) -> list[str] | str | None:
        import json

        try:
            data = json.loads(html.get())
        except Exception as e:
            ctx.debug(f"xcity JSON解析失败: {e}")
            return None

        program_list = (data.get("frontprogramlist") or {}).get("program") or []
        if not program_list:
            ctx.debug("xcity 搜索没有匹配结果")
            return None

        self._cached_program = program_list[0]

        program_id = program_list[0].get("id")
        if program_id:
            return [f"{self.base_url}/avod/detail?id={program_id}"]

        ctx.debug("xcity 搜索结果缺少 id")
        return None

    @override
    async def _parse_detail_page(self, ctx: Context, html: Any, detail_url: str) -> CrawlerData | None:
        program = self._cached_program
        if not program:
            raise CrawlerException("xcity 数据缺失: 未获取到节目数据")

        title = program.get("title") or ""
        originaltitle = program.get("titleKana") or title
        if not title:
            raise CrawlerException("数据获取失败: 未获取到title")

        actors = []
        for person in program.get("person") or []:
            name = person.get("name")
            if name:
                actors.append(name)

        genre = program.get("genre") or []

        release = (program.get("releaseDate") or "").replace("/", "-")

        runtime = str(program.get("duration") or "")

        series_name = ""
        series_data = program.get("series")
        if isinstance(series_data, dict):
            series_name = series_data.get("name") or ""

        maker_name = ""
        maker_data = program.get("maker")
        if isinstance(maker_data, dict):
            maker_name = maker_data.get("name") or ""

        label_name = ""
        label_data = program.get("label")
        if isinstance(label_data, dict):
            label_name = label_data.get("name") or ""

        front_image = (program.get("frontPackageImage") or "").replace("/medium/", "/large/")
        back_image = (program.get("backPackageImage") or "").replace("/medium/", "/large/")

        return CrawlerData(
            number=ctx.input.number,
            title=title,
            originaltitle=originaltitle,
            actors=actors,
            all_actors=actors,
            outline=program.get("synopsis") or "",
            originalplot=program.get("synopsis") or "",
            tags=genre,
            release=release,
            year=release[:4] if len(release) >= 4 else "",
            runtime=runtime,
            series=series_name,
            studio=maker_name,
            publisher=label_name,
            thumb=back_image,
            poster=front_image,
            image_download=False,
            mosaic="有码",
            external_id=detail_url,
        )
