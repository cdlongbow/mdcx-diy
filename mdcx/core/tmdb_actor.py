"""
TMDB 演员 ID 查询模块
通过 TMDB API 搜索日本成人演员，获取 tmdbid 并缓存到 Excel 文件
"""

import html
import re
import time
from pathlib import Path

from ..config.manager import manager
from ..models.log_buffer import LogBuffer
from ..web_async import AsyncWebClient

JAPAN_PLACE_KEYWORDS = [
    "japan",
    "日本",
    "にほん",
    "にっぽん",
    "tokyo",
    "osaka",
    "kyoto",
    "nagoya",
    "sapporo",
    "fukuoka",
    "hiroshima",
    "sendai",
    "kochi",
    "kagoshima",
    "oita",
    "nara",
    "mie",
    "aichi",
    "hyogo",
    "kanagawa",
    "chiba",
    "saitama",
    "ibaraki",
    "gunma",
    "tochigi",
    "yamanashi",
    "shizuoka",
    "niigata",
    "toyama",
    "ishikawa",
    "fukui",
    "shiga",
    "wakayama",
    "tottori",
    "shimane",
    "okayama",
    "yamaguchi",
    "tokushima",
    "ehime",
    "yamagata",
    "akita",
    "aomori",
    "fukushima",
    "miyagi",
    "kumamoto",
    "miyazaki",
    "saga",
    "nagasaki",
    "okinawa",
    "hokkaido",
    "yokohama",
    "kobe",
    "kawasaki",
    "himeji",
    "utsunomiya",
    "matsuyama",
    "iwate",
    "otaru",
    "higashimurayama",
]


def norm_name(s: str) -> str:
    if not s:
        return ""
    s = html.unescape(str(s)).strip().replace("\u3000", " ")
    s = re.sub(r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.casefold()


def is_japan_place(place: str) -> bool:
    if not place:
        return False
    pl = place.lower()
    for kw in JAPAN_PLACE_KEYWORDS:
        if kw.lower() in pl:
            return True
    return False


async def load_actor_tmdb_cache() -> dict[str, int]:
    excel_path = _get_excel_path()
    cache: dict[str, int] = {}
    if not excel_path.exists():
        return cache
    try:
        import openpyxl

        wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
        ws = wb.active
        for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if row_idx == 1:
                continue
            if len(row) < 2:
                continue
            actor_name = str(row[0] or "").strip()
            tmdbid = str(row[1] or "").strip()
            if actor_name and tmdbid.isdigit():
                cache[actor_name] = int(tmdbid)
        wb.close()
    except ImportError:
        pass
    except Exception:
        pass
    return cache


async def save_actor_tmdb_to_excel(actor_name: str, tmdbid: int) -> None:
    excel_path = _get_excel_path()
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import openpyxl
        from openpyxl.utils import get_column_letter

        if excel_path.exists():
            wb = openpyxl.load_workbook(excel_path)
        else:
            wb = openpyxl.Workbook()

        ws = wb.active
        ws.title = "演员TMDB ID"

        if not ws["A1"].value:
            headers = ["演员名", "tmdbid", "tmdb url"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = openpyxl.styles.Font(bold=True)
                cell.fill = openpyxl.styles.PatternFill("solid", fgColor="C0C0C0")
                cell.alignment = openpyxl.styles.Alignment(horizontal="center")
            ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

        existing_row = None
        for row_idx, row in enumerate(ws.iter_rows(min_col=1, max_col=2, values_only=True), start=1):
            if row_idx == 1:
                continue
            if str(row[0] or "").strip() == actor_name:
                existing_row = row_idx
                break

        if existing_row:
            ws.cell(row=existing_row, column=2, value=tmdbid)
            ws.cell(row=existing_row, column=3).value = None
            ws.cell(
                row=existing_row,
                column=3,
                value=f"https://www.themoviedb.org/person/{tmdbid}",
            )
            ws.cell(row=existing_row, column=3).hyperlink = (
                f"https://www.themoviedb.org/person/{tmdbid}"
            )
        else:
            ws.append([actor_name, tmdbid, ""])
            last_row = ws.max_row
            ws.cell(row=last_row, column=3).value = None
            ws.cell(
                row=last_row,
                column=3,
                value=f"https://www.themoviedb.org/person/{tmdbid}",
            )
            ws.cell(row=last_row, column=3).hyperlink = (
                f"https://www.themoviedb.org/person/{tmdbid}"
            )

        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)) + 2)
                except (TypeError, AttributeError):
                    pass
            adjusted_width = min(max_length, 100)
            ws.column_dimensions[column].width = adjusted_width

        wb.save(excel_path)
        wb.close()
    except ImportError:
        pass
    except PermissionError:
        pass
    except Exception:
        pass


def _get_excel_path() -> Path:
    from ..config.manager import manager

    return manager.data_folder / "userdata" / "actor_tmdbid.xlsx"


async def fetch_actor_tmdb_ids(
    actors: list[str], client: AsyncWebClient
) -> dict[str, int]:
    if not actors:
        return {}

    tmdb_api_base = manager.config.tmdb_api_base.strip()
    tmdb_api_key = manager.config.tmdb_api_key.strip()

    if not tmdb_api_key:
        return {}

    if not tmdb_api_base:
        tmdb_api_base = "api.tmdb.org"

    protocol = "https://"
    if tmdb_api_base.startswith("http://"):
        protocol = "http://"
        tmdb_api_base = tmdb_api_base[7:]
    elif tmdb_api_base.startswith("https://"):
        protocol = "https://"
        tmdb_api_base = tmdb_api_base[8:]

    base_url = f"{protocol}{tmdb_api_base}"

    cache = await load_actor_tmdb_cache()
    result: dict[str, int] = {}
    need_query: list[str] = []

    for actor in actors:
        if not actor or not actor.strip():
            continue
        actor_stripped = actor.strip()
        if actor_stripped in cache:
            result[actor_stripped] = cache[actor_stripped]
        else:
            need_query.append(actor_stripped)

    if not need_query:
        return result

    LogBuffer.log().write(f"\n 🎬 [TMDB] 开始查询 {len(need_query)} 个演员的 TMDB ID")

    for actor_name in need_query:
        try:
            tmdbid = await _query_single_actor(actor_name, base_url, tmdb_api_key, client)
            if tmdbid:
                result[actor_name] = tmdbid
                cache[actor_name] = tmdbid
                await save_actor_tmdb_to_excel(actor_name, tmdbid)
                LogBuffer.log().write(
                    f"  ✅ [TMDB] {actor_name} -> tmdbid={tmdbid}"
                )
            else:
                LogBuffer.log().write(
                    f"  ⚠️ [TMDB] {actor_name} 未找到匹配的 TMDB 演员"
                )
        except Exception as e:
            LogBuffer.log().write(
                f"  ❌ [TMDB] {actor_name} 查询失败: {e}"
            )
        time.sleep(0.5)

    matched = len(result) - len([a for a in actors if a.strip() in cache])
    LogBuffer.log().write(
        f" 🎬 [TMDB] 查询完成: 缓存命中 {len(actors) - len(need_query)} 个, "
        f"本次匹配 {matched} 个, 共 {len(result)} 个"
    )
    return result


async def _query_single_actor(
    actor_name: str, base_url: str, api_key: str, client: AsyncWebClient
) -> int | None:
    search_url = f"{base_url}/3/search/person"
    target = norm_name(actor_name)

    resp = await client.get(
        search_url,
        params={
            "api_key": api_key,
            "query": actor_name,
            "include_adult": "true",
            "language": "zh-CN",
            "page": 1,
        },
        follow_redirects=True,
    )

    if resp.status_code != 200:
        return None

    data = resp.json()
    results = data.get("results", [])

    if not results:
        return None

    candidates: list[dict] = []

    for item in results[:10]:
        pid = item.get("id")
        if not pid:
            continue

        gender = item.get("gender")
        if gender not in (0, 1):
            continue

        detail_url = f"{base_url}/3/person/{pid}"
        detail_resp = await client.get(
            detail_url,
            params={"api_key": api_key, "language": "zh-CN"},
            follow_redirects=True,
        )

        if detail_resp.status_code != 200:
            continue

        detail = detail_resp.json()
        place = detail.get("place_of_birth", "")

        if not is_japan_place(place):
            continue

        all_names = set()
        for x in [item.get("name"), item.get("original_name"), detail.get("name")]:
            if x:
                all_names.add(str(x).strip())
        for a in detail.get("also_known_as", []):
            if a:
                all_names.add(str(a).strip())

        all_norm = {norm_name(n) for n in all_names if n}
        is_match = target in all_norm

        popularity = float(item.get("popularity", 0))
        known_for_count = len(detail.get("known_for", [])) if "known_for" in detail else 0
        place_has_japan = "japan" in place.lower() or "日本" in place

        candidates.append(
            {
                "pid": pid,
                "is_match": is_match,
                "popularity": popularity,
                "known_for_count": known_for_count,
                "place_has_japan": place_has_japan,
                "name": detail.get("name", ""),
            }
        )

    matched = [c for c in candidates if c["is_match"]]

    if not matched:
        return None

    matched.sort(
        key=lambda x: (x["popularity"], x["known_for_count"], x["place_has_japan"]),
        reverse=True,
    )

    if len(matched) > 1:
        LogBuffer.log().write(
            f"  ⚠️ [TMDB] 演员「{actor_name}」匹配到 {len(matched)} 个结果，"
            f"已自动选择 tmdbid={matched[0]['pid']} "
            f"(popularity={matched[0]['popularity']:.2f})"
        )

    return matched[0]["pid"]
