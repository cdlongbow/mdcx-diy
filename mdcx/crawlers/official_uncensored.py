#!/usr/bin/env python3
import json
import re
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import urljoin

from lxml import etree

from .base import Context, CrawlerData, CrawlerException

UncensoredOfficialSite = Literal["caribbeancom", "heyzo", "1pondo", "pacopacomama", "10musume"]


@dataclass(frozen=True)
class UncensoredOfficialSpec:
    source: UncensoredOfficialSite
    base_url: str
    studio: str
    json_base_url: str = ""
    sample_base_url: str = ""


UNCENSORED_OFFICIAL_SITES: dict[UncensoredOfficialSite, UncensoredOfficialSpec] = {
    "caribbeancom": UncensoredOfficialSpec(
        source="caribbeancom",
        base_url="https://www.caribbeancom.com",
        studio="Caribbeancom",
        sample_base_url="https://smovie.caribbeancom.com",
    ),
    "heyzo": UncensoredOfficialSpec(
        source="heyzo",
        base_url="https://www.heyzo.com",
        studio="HEYZO",
    ),
    "1pondo": UncensoredOfficialSpec(
        source="1pondo",
        base_url="https://www.1pondo.tv",
        studio="1Pondo",
        json_base_url="https://www.1pondo.tv",
        sample_base_url="https://smovie.1pondo.tv",
    ),
    "pacopacomama": UncensoredOfficialSpec(
        source="pacopacomama",
        base_url="https://www.pacopacomama.com",
        studio="Pacopacomama",
        json_base_url="https://www.pacopacomama.com",
        sample_base_url="https://smovie.pacopacomama.com",
    ),
    "10musume": UncensoredOfficialSpec(
        source="10musume",
        base_url="https://www.10musume.com",
        studio="10Musume",
        json_base_url="https://www.10musume.com",
        sample_base_url="https://smovie.10musume.com",
    ),
}

DIGIT_PREFIX_ALIASES: dict[str, UncensoredOfficialSite] = {
    "1pon": "1pondo",
    "1pondo": "1pondo",
    "10mu": "10musume",
    "10musume": "10musume",
    "carib": "caribbeancom",
    "caribbeancom": "caribbeancom",
    "caribbeancompr": "caribbeancom",
    "paco": "pacopacomama",
    "pacoma": "pacopacomama",
    "pacopacomama": "pacopacomama",
}

DIGIT_NUMBER_RE = re.compile(r"^(?P<head>\d{6})(?P<sep>[-_])(?P<tail>\d{2,4})$")
DIGIT_NUMBER_WITH_PREFIX_RE = re.compile(
    r"^(?P<prefix>1pondo|1pon|10musume|10mu|caribbeancom|caribbeancompr|carib|pacopacomama|pacoma|paco)"
    r"[-_ ]*(?P<head>\d{6})(?P<sep>[-_])(?P<tail>\d{2,4})$",
    re.IGNORECASE,
)
HEYZO_RE = re.compile(r"^heyzo[-_ ]*(?P<id>\d{3,})$", re.IGNORECASE)


def _clean_text(value: object) -> str:
    text = str(value or "").strip()
    return re.sub(r"\s+", " ", text)


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys([item for item in items if item]))


def split_names(value: object) -> list[str]:
    text = str(value or "")
    if not text.strip():
        return []
    return _dedupe([_clean_text(item) for item in re.split(r"[,/|、，\n\r]+", text) if _clean_text(item)])


def split_tags(value: object) -> list[str]:
    if isinstance(value, list):
        return _dedupe([_clean_text(item) for item in value])
    text = str(value or "")
    return _dedupe([_clean_text(item) for item in re.split(r"[,/|、，\n\r]+", text) if _clean_text(item)])


def get_year(release: str) -> str:
    if match := re.search(r"\d{4}", release or ""):
        return match.group()
    return ""


def normalize_release(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if match := re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", text):
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return text[:10]


def seconds_to_minutes(value: object) -> str:
    try:
        seconds = int(float(str(value).strip()))
    except (TypeError, ValueError):
        return ""
    if seconds <= 0:
        return ""
    return str(max(1, seconds // 60))


def hms_to_minutes(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if match := re.search(r"(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", text):
        parts = [int(part or 0) for part in match.groups()]
        if match.group(3) is None:
            hours = 0
            minutes, seconds = parts[0], parts[1]
        else:
            hours, minutes, seconds = parts
        total_minutes = hours * 60 + minutes
        if total_minutes == 0 and seconds > 0:
            return "1"
        return str(total_minutes)
    return ""


def iso8601_duration_to_minutes(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    match = re.fullmatch(
        r"P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?",
        text,
        re.IGNORECASE,
    )
    if not match:
        return ""
    days = int(match.group("days") or 0)
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    total_minutes = days * 24 * 60 + hours * 60 + minutes
    if total_minutes == 0 and seconds > 0:
        return "1"
    return str(total_minutes) if total_minutes > 0 else ""


def _prefixless_digit_parts(number: str) -> tuple[str, str, str] | None:
    value = (number or "").strip().lower().replace(" ", "")
    if match := DIGIT_NUMBER_RE.fullmatch(value):
        return match.group("head"), match.group("sep"), match.group("tail")
    if match := DIGIT_NUMBER_WITH_PREFIX_RE.fullmatch(value):
        return match.group("head"), match.group("sep"), match.group("tail")
    return None


def normalize_uncensored_official_id(number: str) -> str:
    value = (number or "").strip().lower().replace(" ", "")
    if match := HEYZO_RE.fullmatch(value):
        return match.group("id")
    if parts := _prefixless_digit_parts(number):
        head, sep, tail = parts
        return f"{head}{sep}{tail}"
    return value.strip("-_. ")


def route_uncensored_official(number: str) -> UncensoredOfficialSite | None:
    value = (number or "").strip().lower().replace(" ", "")
    if not value:
        return None

    if HEYZO_RE.fullmatch(value):
        return "heyzo"

    prefix_match = DIGIT_NUMBER_WITH_PREFIX_RE.fullmatch(value)
    if prefix_match:
        prefix = prefix_match.group("prefix").lower()
        alias_site = DIGIT_PREFIX_ALIASES[prefix]
        if alias_site in {"caribbeancom", "1pondo", "pacopacomama", "10musume"}:
            return alias_site

    if match := DIGIT_NUMBER_RE.fullmatch(value):
        sep = match.group("sep")
        tail = match.group("tail")
        if sep == "-":
            return "caribbeancom"
        if sep == "_":
            if len(tail) == 2:
                return "10musume"
            if int(tail) >= 100:
                return "pacopacomama"
            return "1pondo"

    return None


def detail_url_for_uncensored_official(site: UncensoredOfficialSite, movie_id: str) -> str:
    spec = UNCENSORED_OFFICIAL_SITES[site]
    if site == "caribbeancom":
        return f"{spec.base_url}/moviepages/{movie_id}/index.html"
    if site == "heyzo":
        return f"{spec.base_url}/moviepages/{movie_id}/index.html"
    return f"{spec.base_url}/movies/{movie_id}/"


def json_url_for_uncensored_official(site: UncensoredOfficialSite, movie_id: str) -> str:
    spec = UNCENSORED_OFFICIAL_SITES[site]
    return f"{spec.json_base_url}/dyn/phpauto/movie_details/movie_id/{movie_id}.json"


async def crawl_uncensored_official(ctx: Context, client, number: str) -> CrawlerData | None:
    site = route_uncensored_official(number)
    if site is None:
        return None

    movie_id = normalize_uncensored_official_id(number)
    if not movie_id:
        return None

    ctx.debug(f"official uncensored route: {site} ({movie_id})")
    if site == "caribbeancom":
        return await _crawl_caribbeancom(ctx, client, movie_id)
    if site == "heyzo":
        return await _crawl_heyzo(ctx, client, movie_id)
    return await _crawl_json_site(ctx, client, site, movie_id)


def _selector(html: str):
    return etree.fromstring(html, etree.HTMLParser())


def _first_xpath_text(html, *xpaths: str) -> str:
    for xpath in xpaths:
        results = html.xpath(xpath)
        for result in results:
            text = result if isinstance(result, str) else result.xpath("string()")
            text = _clean_text(text)
            if text:
                return text
    return ""


def _all_xpath_texts(html, *xpaths: str) -> list[str]:
    values: list[str] = []
    for xpath in xpaths:
        results = html.xpath(xpath)
        for result in results:
            text = result if isinstance(result, str) else result.xpath("string()")
            text = _clean_text(text)
            if text:
                values.append(text)
    return _dedupe(values)


def _all_xpath_attrs(html, xpath: str) -> list[str]:
    return _dedupe([_clean_text(item) for item in html.xpath(xpath) if _clean_text(item)])


def _urljoin_all(base_url: str, urls: list[str]) -> list[str]:
    return _dedupe([urljoin(base_url, url) for url in urls if url])


def _caribbean_spec_value(html, labels: set[str]) -> str:
    for row in html.xpath("//li[contains(concat(' ', normalize-space(@class), ' '), ' movie-spec ')]"):
        label = _first_xpath_text(row, ".//*[contains(concat(' ', normalize-space(@class), ' '), ' spec-title ')]")
        label = label.rstrip(":：").strip()
        if label in labels:
            return _first_xpath_text(row, ".//*[contains(concat(' ', normalize-space(@class), ' '), ' spec-content ')]")
    return ""


async def _crawl_caribbeancom(ctx: Context, client, movie_id: str) -> CrawlerData:
    spec = UNCENSORED_OFFICIAL_SITES["caribbeancom"]
    detail_url = ctx.input.appoint_url or detail_url_for_uncensored_official("caribbeancom", movie_id)
    ctx.debug(f"official uncensored detail: {detail_url}")
    ctx.debug_info.detail_urls = [detail_url]
    html_content, error = await client.get_text(detail_url, encoding="euc-jp")
    if html_content is None:
        raise CrawlerException(f"official uncensored request failed: {error}")

    html = _selector(html_content)
    title = _first_xpath_text(html, '//*[@itemprop="name"]/text()', "//h1/text()")
    if not title:
        raise CrawlerException("official uncensored data failed: title")

    release = normalize_release(_caribbean_spec_value(html, {"配信日", "発売日"}))
    runtime = hms_to_minutes(_caribbean_spec_value(html, {"再生時間", "収録時間"}))
    actors = split_names(_caribbean_spec_value(html, {"出演", "女優"}))
    tags = split_tags(_caribbean_spec_value(html, {"タグ"}))
    series = _caribbean_spec_value(html, {"シリーズ"})
    studio = _caribbean_spec_value(html, {"メーカー", "レーベル"}) or spec.studio
    outline = _first_xpath_text(
        html,
        '//*[@itemprop="description"]',
        '//meta[@name="description"]/@content',
        '//meta[@property="og:description"]/@content',
    )
    thumb = urljoin(spec.base_url, f"/moviepages/{movie_id}/images/l_l.jpg")
    extrafanart = _urljoin_all(
        spec.base_url,
        _all_xpath_attrs(
            html,
            "//a[contains(@href, '/moviepages/') and contains(@href, '/images/l/')]/@href",
        ),
    )
    extrafanart = [url for url in extrafanart if url != thumb and "/member/" not in url]

    return CrawlerData(
        number=movie_id,
        title=title,
        originaltitle=title,
        actors=actors,
        all_actors=actors,
        outline=outline,
        originalplot=outline,
        tags=tags,
        release=release,
        year=get_year(release),
        runtime=runtime,
        score="",
        series=series,
        directors=[],
        studio=studio,
        publisher=studio,
        thumb=thumb,
        poster="",
        extrafanart=extrafanart,
        trailer=f"{spec.sample_base_url}/sample/movies/{movie_id}/sample.mp4",
        image_download=False,
        mosaic="无码",
        external_id=detail_url,
        wanted="",
        source=spec.source,
    )


def _load_json_ld(html) -> dict[str, Any]:
    for item in html.xpath('//script[@type="application/ld+json"]/text()'):
        try:
            data = json.loads(item)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            for child in data:
                if isinstance(child, dict) and child.get("@type") == "Movie":
                    return child
        if isinstance(data, dict) and data.get("@type") == "Movie":
            return data
    return {}


def _absolute_protocol_url(url: object, base_url: str) -> str:
    text = str(url or "").strip()
    if text.startswith("//"):
        return "https:" + text
    return urljoin(base_url, text) if text else ""


def _json_ld_actors(value: object) -> list[str]:
    if isinstance(value, dict):
        return split_names(value.get("name"))
    if isinstance(value, list):
        names: list[str] = []
        for item in value:
            if isinstance(item, dict):
                names.extend(split_names(item.get("name")))
            else:
                names.extend(split_names(item))
        return _dedupe(names)
    return split_names(value)


async def _crawl_heyzo(ctx: Context, client, movie_id: str) -> CrawlerData:
    spec = UNCENSORED_OFFICIAL_SITES["heyzo"]
    detail_url = ctx.input.appoint_url or detail_url_for_uncensored_official("heyzo", movie_id)
    ctx.debug(f"official uncensored detail: {detail_url}")
    ctx.debug_info.detail_urls = [detail_url]
    html_content, error = await client.get_text(detail_url)
    if html_content is None:
        raise CrawlerException(f"official uncensored request failed: {error}")

    html = _selector(html_content)
    json_ld = _load_json_ld(html)
    title = _clean_text(json_ld.get("name")) or _first_xpath_text(
        html, '//meta[@property="og:title"]/@content', "//h1/text()"
    )
    if not title:
        raise CrawlerException("official uncensored data failed: title")

    actors = _json_ld_actors(json_ld.get("actor"))
    release = normalize_release(json_ld.get("dateCreated"))
    runtime = iso8601_duration_to_minutes(json_ld.get("duration"))
    thumb = _absolute_protocol_url(
        json_ld.get("image") or _first_xpath_text(html, '//meta[@property="og:image"]/@content'),
        spec.base_url,
    )
    trailer = ""
    if isinstance(json_ld.get("video"), dict):
        trailer = _absolute_protocol_url(json_ld["video"].get("contentUrl"), spec.base_url)
    if not trailer:
        trailer = f"https://sample.heyzo.com/contents/{int(movie_id) // 1000 * 1000}/{movie_id}/sample.mp4"
    outline = _clean_text(json_ld.get("description")) or _first_xpath_text(html, '//meta[@name="description"]/@content')
    tags = _all_xpath_texts(
        html,
        "//a[contains(@href, 'category_') and not(contains(@class, 'actor'))]/text()",
        "//span[contains(@class, 'tag')]/text()",
    )

    return CrawlerData(
        number=f"HEYZO-{movie_id}",
        title=title,
        originaltitle=title,
        actors=actors,
        all_actors=actors,
        outline=outline,
        originalplot=outline,
        tags=tags,
        release=release,
        year=get_year(release),
        runtime=runtime,
        score="",
        series="",
        directors=[],
        studio=spec.studio,
        publisher=spec.studio,
        thumb=thumb,
        poster="",
        extrafanart=[],
        trailer=trailer,
        image_download=False,
        mosaic="无码",
        external_id=detail_url,
        wanted="",
        source=spec.source,
    )


def _json_value(data: dict[str, Any], *keys: str) -> object:
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return ""


def _json_images(data: dict[str, Any]) -> tuple[str, str, list[str]]:
    thumb = str(_json_value(data, "ThumbHigh", "MovieThumb", "Thumb", "SampleThumb")).strip()
    poster = str(_json_value(data, "Poster", "Jacket", "Thumb")).strip()
    extra_raw = _json_value(data, "Gallery", "GalleryImages", "SampleImages")
    extrafanart: list[str] = []
    if isinstance(extra_raw, list):
        for item in extra_raw:
            if isinstance(item, dict):
                extrafanart.extend(str(value).strip() for value in item.values() if str(value).strip())
            elif str(item).strip():
                extrafanart.append(str(item).strip())
    return thumb, poster, _dedupe(extrafanart)


async def _crawl_json_site(ctx: Context, client, site: UncensoredOfficialSite, movie_id: str) -> CrawlerData:
    spec = UNCENSORED_OFFICIAL_SITES[site]
    detail_url = ctx.input.appoint_url or detail_url_for_uncensored_official(site, movie_id)
    json_url = json_url_for_uncensored_official(site, movie_id)
    ctx.debug(f"official uncensored api: {json_url}")
    ctx.debug_info.search_urls = [json_url]
    ctx.debug_info.detail_urls = [detail_url]
    content, error = await client.get_text(json_url)
    if content is None:
        raise CrawlerException(f"official uncensored request failed: {error}")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise CrawlerException(f"official uncensored json failed: {exc}") from exc

    if not isinstance(data, dict):
        raise CrawlerException("official uncensored json failed: not object")

    title = _clean_text(_json_value(data, "Title", "MovieTitle"))
    if not title:
        raise CrawlerException("official uncensored data failed: title")

    actors = split_names(_json_value(data, "ActressesJa", "Actor", "Actors", "Actresses"))
    release = normalize_release(_json_value(data, "Release", "ReleaseDate", "Year"))
    runtime = seconds_to_minutes(_json_value(data, "Duration", "Runtime"))
    thumb, poster, extrafanart = _json_images(data)
    series = _clean_text(_json_value(data, "Series", "UCNAME"))
    studio = _clean_text(_json_value(data, "UCNAME", "Maker", "Studio")) or spec.studio
    trailer = _clean_text(_json_value(data, "SampleMovie", "SampleMovieHigh", "MovieSample"))
    if not trailer and spec.sample_base_url:
        trailer = f"{spec.sample_base_url}/sample/movies/{movie_id}/sample.mp4"

    return CrawlerData(
        number=movie_id,
        title=title,
        originaltitle=title,
        actors=actors,
        all_actors=actors,
        outline=_clean_text(_json_value(data, "Desc", "Description")),
        originalplot=_clean_text(_json_value(data, "Desc", "Description")),
        tags=split_tags(_json_value(data, "Tag", "Tags", "Genre", "Genres")),
        release=release,
        year=get_year(release),
        runtime=runtime,
        score="",
        series=series,
        directors=[],
        studio=studio,
        publisher=studio,
        thumb=thumb,
        poster=poster,
        extrafanart=extrafanart,
        trailer=trailer,
        image_download=bool(poster),
        mosaic="无码",
        external_id=detail_url,
        wanted="",
        source=spec.source,
    )
