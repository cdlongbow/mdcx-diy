#!/usr/bin/env python3
import re
from typing import override

from lxml import etree

from ..base.web import check_url, is_dmm_image_url, normalize_media_url
from ..config.enums import Website
from ..config.manager import manager
from .base import BaseCrawler, Context, CralwerException, CrawlerData


def is_not_found(html):
    """检查是否为 404 页面"""
    result = html.xpath("string(//h1)")
    return "Not found" in result


def get_number(html):
    """获取番号"""
    result = html.xpath("//h1/span[1]/text()")
    return result[0].strip() if result else ""


def get_title(html):
    """获取标题 (不包含番号)"""
    result = html.xpath("//h1/span[2]/text()")
    return result[0].strip() if result else ""


def get_cover(html):
    """获取封面大图 (col-md-8 中的 img)"""
    result = html.xpath('//div[@class="col-md-8"]/img/@src')
    return result[0].strip() if result else ""


def get_poster(html):
    """获取小封面图 (Thumbnail Image)"""
    result = html.xpath('//dt[text()="Thumbnail Image"]/following-sibling::dd[1]/img/@src')
    return result[0].strip() if result else ""


def get_release(html):
    """获取发行日期"""
    result = html.xpath('//dt[text()="Release Date"]/following-sibling::dd[1]/text()')
    if not result:
        return ""
    release = result[0].strip()
    # 标准化日期格式
    release = release.replace("/", "-").replace(".", "-")
    match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", release)
    if match:
        return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    return release


def get_year(release):
    """从发行日期提取年份"""
    if release and len(release) >= 4:
        return release[:4]
    return ""


def get_directors(html):
    """获取导演列表"""
    result = html.xpath('//dt[text()="Directors"]/following-sibling::dd[1]//li/text()')
    return [item.strip() for item in result if item.strip()]


def get_tags(html):
    """获取标签/类别列表"""
    result = html.xpath('//dt[text()="Genres"]/following-sibling::dd[1]//li/text()')
    return [item.strip() for item in result if item.strip()]


def get_studio(html):
    """获取制作商 (Makers)"""
    result = html.xpath('//dt[text()="Makers"]/following-sibling::dd[1]//li/text()')
    return result[0].strip() if result else ""


def get_publisher(html):
    """获取发行商/厂牌 (Labels)"""
    result = html.xpath('//dt[text()="Labels"]/following-sibling::dd[1]//li/text()')
    return result[0].strip() if result else ""


def get_runtime(html):
    """获取时长 (分钟)"""
    result = html.xpath('//dt[text()="Volume"]/following-sibling::dd[1]/text()')
    if not result:
        return ""
    match = re.search(r"(\d+)", result[0])
    return match.group(1) if match else ""


def get_score(html):
    """获取评分"""
    result = html.xpath('//dt[text()="User Rating"]/following-sibling::dd[1]/text()')
    if not result:
        return ""
    score = result[0].strip()
    try:
        return str(float(score))
    except ValueError:
        return ""


def get_actors(html):
    """获取演员列表"""
    result = html.xpath('//div[@class="card actress"]//h6/a/text()')
    return [item.strip() for item in result if item.strip()]


def get_extrafanart(html):
    """获取样图列表"""
    result = html.xpath('//div[@id="sample-images"]/a/@href')
    return [item.strip() for item in result if item.strip()]


def get_series(html):
    """获取系列信息 (libredmm 不提供系列字段)"""
    return ""


def get_mosaic(tags):
    """根据标签判断是否有码"""
    tags_str = ",".join(tags)
    return "无码" if "無修正" in tags_str else "有码"


# ---------------------------------------------------------------------------
# 高清图 URL 辅助函数
# ---------------------------------------------------------------------------

_AWS_BASE = "https://awsimgsrc.dmm.co.jp/pics_dig/digital/video"


def _number_variants(number: str) -> tuple[str, str]:
    """返回 (number_00, number_no_00) 两种番号小写格式.

    - number_00: 连字符替换为 "00"，如 "SSIS-001" → "ssis00001"
    - number_no_00: 连字符直接去除，如 "SSIS-001" → "ssis001"
    """
    lower = number.lower()
    return lower.replace("-", "00"), lower.replace("-", "")


def _build_aws_cover_candidates(number: str) -> list[str]:
    """从番号构造高清封面 (thumb/pl.jpg) 候选 URL 列表."""
    number_00, number_no_00 = _number_variants(number)
    candidates: list[str] = []
    if number_00:
        candidates.append(f"{_AWS_BASE}/{number_00}/{number_00}pl.jpg")
    if number_no_00 and number_no_00 != number_00:
        candidates.append(f"{_AWS_BASE}/{number_no_00}/{number_no_00}pl.jpg")
    return candidates


def _build_aws_poster_candidates(number: str, thumb_url: str) -> list[str]:
    """从番号构造高清海报 (poster/ps.jpg) 候选 URL 列表."""
    number_00, number_no_00 = _number_variants(number)
    candidates: list[str] = []
    if number_00:
        candidates.append(f"{_AWS_BASE}/{number_00}/{number_00}ps.jpg")
    if number_no_00 and number_no_00 != number_00:
        candidates.append(f"{_AWS_BASE}/{number_no_00}/{number_no_00}ps.jpg")
    # 如果 thumb_url 是标准 pl.jpg 格式，也尝试直接替换后缀
    if thumb_url and thumb_url.endswith("pl.jpg"):
        ps_url = thumb_url[:-6] + "ps.jpg"
        if ps_url not in candidates:
            candidates.append(ps_url)
    return candidates


def _prefer_dmm_aws_url(url: str) -> str:
    """尝试将低清 pics.dmm.co.jp URL 升级为高清 awsimgsrc.dmm.co.jp URL.

    仅做简单的域名和路径替换，不改变路径结构。
    对 digital 路径有效，对 mono 路径无效（路径结构不同）。
    """
    normalized = normalize_media_url(str(url or "").strip())
    if not normalized:
        return ""
    if "pics.dmm.co.jp" in normalized:
        return normalized.replace("pics.dmm.co.jp", "awsimgsrc.dmm.co.jp/pics_dig").replace("/adult/", "/")
    return normalized


def _upgrade_extrafanart_urls(urls: list[str], number: str) -> list[str]:
    """升级样图 URL 列表: 优先使用高清 CDN，回退到低清原图."""
    number_00, number_no_00 = _number_variants(number)
    result: list[str] = []
    for url in urls:
        normalized = normalize_media_url(str(url or "").strip())
        if not normalized:
            continue
        # 尝试高清 CDN 替换
        aws_url = _prefer_dmm_aws_url(normalized)
        if aws_url and aws_url != normalized:
            # 去重添加：高清优先
            if aws_url not in result:
                result.append(aws_url)
        # 保留原低清 URL 作为后备
        if normalized not in result:
            result.append(normalized)
    return result


class LibredmmCrawler(BaseCrawler):
    @classmethod
    @override
    def site(cls) -> Website:
        return Website.LIBREDMM

    @classmethod
    @override
    def base_url_(cls) -> str:
        return manager.config.get_site_url(Website.LIBREDMM, "https://www.libredmm.com")

    @classmethod
    @override
    def display_name(cls) -> str:
        return "LibreDMM"

    @override
    async def _run(self, ctx: Context):
        number = ctx.input.number
        real_url = ctx.input.appoint_url

        if not real_url:
            # 直接构造详情页 URL: /movies/{number}
            real_url = f"{self.base_url}/movies/{number}"

        ctx.debug(f"番号地址: {real_url}")
        ctx.debug_info.detail_urls = [real_url]

        html_content, error = await self.async_client.get_text(real_url)

        # 如果直接 URL 返回 404，尝试通过搜索查找
        if html_content is None:
            if "404" not in str(error):
                raise CralwerException(f"网络请求错误: {error}")

            # 直接 URL 不存在，尝试搜索（搜索会重定向到匹配的详情页）
            search_url = f"{self.base_url}/search?q={number}"
            ctx.debug(f"直接 URL 返回 404，尝试搜索: {search_url}")
            ctx.debug_info.search_urls = [search_url]

            html_content, error = await self.async_client.get_text(search_url)
            if html_content is None:
                raise CralwerException("搜索结果: 未匹配到番号！")

            # 搜索成功重定向到详情页，更新 real_url
            # 注意：搜索重定向后，详情页 URL 不再是直接构造的 URL

        html_info = etree.fromstring(html_content, etree.HTMLParser())

        # 双重检查：确认不是 404 页面（某些情况下可能返回 200 但内容是 404）
        if is_not_found(html_info):
            raise CralwerException("搜索结果: 未匹配到番号！")

        # 解析页面数据
        web_number = get_number(html_info)
        title = get_title(html_info)
        if not title:
            raise CralwerException("数据获取失败: 未获取到 title")

        # 使用网页上的番号，若无则使用输入番号
        number = web_number or number
        # 从标题中移除番号前缀（如果有的话）
        if title.startswith(number):
            title = title[len(number) :].strip()

        cover_url = get_cover(html_info)
        poster_url = get_poster(html_info)
        release = get_release(html_info)
        directors = get_directors(html_info)
        tags = get_tags(html_info)
        studio = get_studio(html_info)
        publisher = get_publisher(html_info)
        runtime = get_runtime(html_info)
        score = get_score(html_info)
        actors = get_actors(html_info)
        extrafanart = get_extrafanart(html_info)
        mosaic = get_mosaic(tags)

        # ---- 高清图升级 ----
        # 封面 (thumb): 优先高清 CDN > 低清替换域名 > 原始低清
        cover_candidates = _build_aws_cover_candidates(number)
        # 对低清 URL 尝试域名替换作为备选
        aws_cover_from_low = _prefer_dmm_aws_url(cover_url)
        if aws_cover_from_low and aws_cover_from_low not in cover_candidates:
            cover_candidates.append(aws_cover_from_low)
        # 原始低清 URL 作为最后备选
        if cover_url and cover_url not in cover_candidates:
            cover_candidates.append(cover_url)

        validated_cover = ""
        for candidate in cover_candidates:
            if is_dmm_image_url(candidate):
                if await check_url(candidate):
                    validated_cover = candidate
                    break
            else:
                # 非 DMM 域名图片直接采用
                validated_cover = candidate
                break

        if validated_cover and validated_cover != cover_url:
            ctx.debug(f"封面升级为高清: {validated_cover}")
        cover_url = validated_cover or cover_url

        # 海报 (poster): 优先高清 CDN > 低清替换后缀 > 原始低清
        poster_candidates = _build_aws_poster_candidates(number, cover_url)
        # 对低清 poster URL 尝试域名替换
        aws_poster_from_low = _prefer_dmm_aws_url(poster_url)
        if aws_poster_from_low and aws_poster_from_low not in poster_candidates:
            poster_candidates.append(aws_poster_from_low)
        # 原始低清 poster URL
        if poster_url and poster_url not in poster_candidates:
            poster_candidates.append(poster_url)

        validated_poster = ""
        for candidate in poster_candidates:
            if is_dmm_image_url(candidate):
                if await check_url(candidate):
                    validated_poster = candidate
                    break
            else:
                validated_poster = candidate
                break

        if validated_poster and validated_poster != poster_url:
            ctx.debug(f"海报升级为高清: {validated_poster}")
        poster_url = validated_poster or poster_url

        # 样图 (extrafanart): 尝试升级到高清 CDN
        if extrafanart:
            extrafanart = _upgrade_extrafanart_urls(extrafanart, number)

        data = CrawlerData(
            number=number,
            title=title,
            originaltitle=title,
            actors=actors,
            all_actors=actors,
            directors=directors,
            outline="",
            originalplot="",
            tags=tags,
            release=release,
            year=get_year(release),
            runtime=runtime,
            score=score,
            series=get_series(html_info),
            studio=studio,
            publisher=publisher,
            thumb=cover_url,
            poster=poster_url,
            extrafanart=extrafanart,
            trailer="",
            image_download=False,
            mosaic=mosaic,
            external_id=real_url,
            wanted="",
        )
        result = data.to_result()
        result.source = self.site().value
        ctx.debug("数据获取成功！")
        return result

    @override
    async def _generate_search_url(self, ctx: Context) -> list[str] | str | None:
        return None

    @override
    async def _parse_search_page(self, ctx: Context, html, search_url: str) -> list[str] | str | None:
        return None

    @override
    async def _parse_detail_page(self, ctx: Context, html, detail_url: str) -> CrawlerData | None:
        return None
