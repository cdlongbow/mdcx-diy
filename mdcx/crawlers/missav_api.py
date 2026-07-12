import hashlib
import hmac
import re
import time
from typing import override
from urllib.parse import urlparse

from ..config.manager import manager
from ..config.models import Website
from ..signals import signal
from .base import BaseCrawler, CrawlerData, CrawlerException
from .base.types import NOT_SUPPORT, Context


class MissavApiCrawler(BaseCrawler):
    """
    MissAV 免 Cloudflare 数据源.

    不走 missav.ws 网页(会被 CF 挡死), 而是:
      - 元数据: 直接调 missav 后端 Recombee 推荐 API (client-rapi-missav.recombee.com),
                该域不挂 CF, 故无需浏览器/住宅 IP 即可拿结构化元数据.
      - 封面:   missav 图床 fourhoi.com, 按番号拼 URL (同样免 CF).

    Recombee 返回的字段(实测): title/title_cn(简中)/title_zh(繁中)/各语言标题/
      directors/genres/series/labels|markers/released_at/duration/
      has_chinese_subtitle/has_english_subtitle/is_uncensored_leak/type.
    注意: Recombee 搜索接口**不含演员**(actresses/actors 恒为空), 故演员字段留空.
    若以后需要演员, 需从其它站(javbus/javdb 等)按番号补.

    标题默认用简体中文(title_cn). 只取女优(actresses), 绝不取男优(actors).
    """

    RECOMBEE_HOST = "client-rapi-missav.recombee.com"
    DATABASE_ID = "missav-default"
    PUBLIC_TOKEN = "Ikkg568nlM51RHvldlPvc2GzZPE9R4XGzaH9Qj4zK9npbbbTly1gj9K4mgRn0QlV"
    COVER_HOST = "https://fourhoi.com"
    LANG_SUFFIXES = {"cn", "en", "jp", "ja", "tw", "hk"}

    @staticmethod
    def _log(message: str) -> None:
        signal.add_log(f"\U0001F310 [MISSAV-API] {message}")

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.MISSAV_API

    @classmethod
    @override
    def base_url_(cls) -> str:
        # 占位, 实际不发 missav.ws 请求(走 Recombee + fourhoi)
        return manager.config.get_site_url(Website.MISSAV_API, "https://missav.ws")

    @classmethod
    def _sign_path(cls, path: str) -> str:
        ts = int(time.time())
        unsigned = f"/{cls.DATABASE_ID}{path}"
        unsigned += f"&frontend_timestamp={ts}" if "?" in unsigned else f"?frontend_timestamp={ts}"
        sig = hmac.new(cls.PUBLIC_TOKEN.encode("utf-8"), unsigned.encode("utf-8"), hashlib.sha1).hexdigest()
        return unsigned + f"&frontend_sign={sig}"

    @staticmethod
    def _normalize_number(value: str) -> str:
        return re.sub(r"[^a-z0-9]", "-", (value or "").strip().lower()).strip("-")

    @staticmethod
    def _normalize_number_case(number: str) -> str:
        return re.sub(r"[a-z]+", lambda m: m.group(0).upper(), (number or "").strip())

    @staticmethod
    def _number_from_url(url: str) -> str:
        parts = [p for p in urlparse(url).path.split("/") if p]
        while parts and parts[-1].lower() in MissavApiCrawler.LANG_SUFFIXES:
            parts.pop()
        return parts[-1] if parts else ""

    @staticmethod
    def _ts_to_date(ts) -> str:
        try:
            import datetime

            return datetime.datetime.utcfromtimestamp(float(ts)).strftime("%Y-%m-%d")
        except Exception:
            return ""

    @staticmethod
    def _clean_name(name: str) -> str:
        return (name or "").strip()

    async def _recombee_search(self, ctx: Context, number: str):
        q = self._normalize_number(number)
        path = "/search/users/anonymous/items/"
        body = {
            "searchQuery": q,
            "count": 10,
            "cascadeCreate": True,
            "returnProperties": True,
        }
        signed = self._sign_path(path)
        url = f"https://{self.RECOMBEE_HOST}{signed}"
        json_data, error = await self.async_client.post_json(
            url,
            json_data=body,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            use_proxy=False,  # Recombee 不挂 CF, 直连绕开代理更稳定
        )
        if error or not json_data:
            ctx.debug(f"[MISSAV-API] Recombee 请求失败: {error}")
            return None
        recomms = json_data.get("recomms") or []
        if not recomms:
            ctx.debug("[MISSAV-API] Recombee 无结果")
            return None
        # 优先精确 id 匹配, 其次 id 前缀匹配(含 -uncensored-leak), 最后退回首条
        for it in recomms:
            if (it.get("id") or "").lower() == q:
                return it
        for it in recomms:
            if (it.get("id") or "").lower().startswith(q):
                return it
        return recomms[0]

    def _build_data(self, item: dict, input_number: str) -> CrawlerData:
        values = item.get("values") or {}
        item_id = (item.get("id") or input_number).lower()
        cover_id = self._normalize_number(input_number)  # 纯番号(不含 -uncensored-leak), 用于封面

        data = CrawlerData()
        data.number = self._normalize_number_case(cover_id)
        # 标题: 简体中文优先
        data.title = values.get("title_cn") or values.get("title_zh") or values.get("title") or ""
        data.originaltitle = values.get("title") or data.title
        # 女优 ONLY (actresses), 绝不取男优(actors)
        actresses = values.get("actresses") or []
        data.actors = [self._clean_name(a) for a in actresses if a and a.strip()]
        data.all_actors = data.actors
        # 导演
        data.directors = [d for d in (values.get("directors") or []) if d and d.strip()]
        # 类型
        data.tags = [g for g in (values.get("genres") or []) if g and g.strip()]
        # 系列
        series = values.get("series") or []
        data.series = series[0] if series else ""
        # 发行商/厂牌
        labels = values.get("labels") or values.get("markers") or []
        data.publisher = labels[0] if labels else ""
        data.studio = ""
        # 日期
        released = values.get("released_at")
        if released:
            data.release = self._ts_to_date(released)
            data.year = data.release[:4] if data.release else ""
        # 时长(秒 -> 分)
        duration = values.get("duration")
        if duration:
            try:
                data.runtime = str(max(1, round(int(duration) / 60)))
            except Exception:
                pass
        # 封面(fourhoi, 免 CF)
        data.thumb = f"{self.COVER_HOST}/{cover_id}/cover-n.jpg"
        data.poster = f"{self.COVER_HOST}/{cover_id}/cover.jpg"
        data.image_download = True  # 封面走固定 URL, 需下载校验
        # 无码标记
        data.mosaic = "无码" if values.get("is_uncensored_leak") else ""
        # 简介: missav 无独立剧情简介, 此源不提供
        data.outline = NOT_SUPPORT
        data.originalplot = NOT_SUPPORT
        data.external_id = item_id
        return data

    @override
    async def _run(self, ctx: Context):
        number = (ctx.input.number or "").strip()
        if not number and ctx.input.appoint_url:
            number = self._number_from_url(ctx.input.appoint_url)
        if not number:
            raise CrawlerException("番号为空")

        self._log(f"查询番号: {number} (走 Recombee 免 CF 路线)")
        item = await self._recombee_search(ctx, number)
        if not item:
            raise CrawlerException(f"Recombee 未找到匹配: {number}")

        data = self._build_data(item, number)
        data.source = self.site().value
        data = data.to_result()
        return await self.post_process(ctx, data)

    # 以下三个抽象方法本爬虫用不到(已重写 _run 完全自定义流程),
    # 但基类以 @abstractmethod 声明, 必须提供实现方可实例化.
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
    async def post_process(self, ctx, res):
        if not res.number:
            res.number = self._normalize_number_case(ctx.input.number)
        else:
            res.number = self._normalize_number_case(res.number)
        if not res.originaltitle:
            res.originaltitle = res.title
        if not res.publisher:
            res.publisher = res.studio
        if not res.year and (m := re.search(r"\d{4}", res.release or "")):
            res.year = m.group()
        return res
