"""
演员 TMDB ID 查询模块。

通过 TMDB API 搜索日本成人演员，获取 tmdbid 及多语言翻译，统一管理演员数据库 xlsx。
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from ..config.manager import manager
from ..config.resources import resources
from ..models.log_buffer import LogBuffer
from ..utils import convert_half


async def _read_text_file(path: Path, encoding: str = "utf-8") -> str:
    return await asyncio.to_thread(path.read_text, encoding=encoding)


# ============= 速率限制器 =============


class _TmdbRateLimiter:
    """令牌桶限流器，控制 TMDB API 请求速率。"""

    def __init__(self, rate: float = 3.5, burst: int = 10):
        self.rate = rate
        self._tokens = float(burst)
        self._max_tokens = float(burst)
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            self._tokens = min(self._max_tokens, self._tokens + (now - self._last) * self.rate)
            self._last = now
            if self._tokens < 1:
                delay = (1 - self._tokens) / self.rate
                await asyncio.sleep(delay)
                self._tokens = 0
            else:
                self._tokens -= 1


_tmdb_rate_limiter = _TmdbRateLimiter()


def _tmdb_debug_enabled() -> bool:
    return bool(getattr(manager.config, "show_data_log", False))


# ============= HTTP 适配器 =============


class _TmdbResponse:
    """Unified response wrapper for TMDB API calls."""

    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self._text = text

    def json(self) -> dict[str, Any]:
        return json.loads(self._text)


async def _tmdb_request(client: Any, method: str, url: str, **kwargs) -> _TmdbResponse | None:
    """
    Unified HTTP request for both curl_cffi AsyncWebClient and aiohttp ClientSession.
    Returns _TmdbResponse or None on failure.
    """
    await _tmdb_rate_limiter.acquire()
    params = kwargs.get("params")
    if hasattr(client, "request"):
        resp, err = await client.request(method, url, params=params)
        if resp is None:
            return None
        return _TmdbResponse(resp.status, resp.text)
    elif hasattr(client, method.lower()):
        send = getattr(client, method.lower())
        resp = await send(url, params=params, allow_redirects=kwargs.get("follow_redirects", True))
        return _TmdbResponse(resp.status, await resp.text())
    return None


def is_japan_place(place: str) -> bool:
    if not place:
        return False
    p = place.lower()
    japan_keywords = [
        "japan",
        "日本",
        "北海道",
        "青森",
        "岩手",
        "宫城",
        "秋田",
        "山形",
        "福岛",
        "茨城",
        "栃木",
        "群马",
        "埼玉",
        "千叶",
        "东京",
        "神奈川",
        "新潟",
        "富山",
        "石川",
        "福井",
        "山梨",
        "长野",
        "岐阜",
        "静冈",
        "爱知",
        "三重",
        "滋贺",
        "京都",
        "大阪",
        "兵库",
        "奈良",
        "和歌山",
        "鸟取",
        "岛根",
        "冈山",
        "广岛",
        "山口",
        "德岛",
        "香川",
        "爱媛",
        "高知",
        "福冈",
        "佐贺",
        "长崎",
        "熊本",
        "大分",
        "宫崎",
        "鹿儿岛",
        "冲绳",
        "横滨",
        "札幌",
        "神户",
        "川崎",
        "仙台",
        "町田",
        "八王子",
        "品川",
        "涩谷",
        "新宿",
        "池袋",
        "浅草",
        "秋叶原",
        "原宿",
        "六本木",
        "银座",
        "上野",
        "下北泽",
        "吉祥寺",
        "武藏野",
        "国分寺",
        "立川",
        "日野",
        "多摩",
        "青梅",
        # 常见日语地名后缀（仅当长度>=3时匹配，避免单字误匹配中文）
        "都",
        "道",
        "府",
        "县",
        "市",
        "町",
        "村",
        "区",
    ]
    # 排除明显非日本籍（中国地址中 "都" 常见于 "广东/成都"）
    if "中国" in p or "china" in p:
        return False
    for kw in japan_keywords:
        if len(kw) >= 2 and kw in p:
            return True
        if len(kw) == 1 and len(p) >= 3 and p.endswith(kw):
            return True
    return False


# ============= 演员数据库 xlsx 管理 =============

COL_JP = 0
COL_ZH_CN = 1
COL_ZH_TW = 2
COL_KEYWORD = 3
COL_HREF = 4
COL_TMDBID = 5
COL_TMDB_URL = 6

DB_HEADERS = ["日文原名", "中文名", "繁体名", "别名", "链接", "tmdbid", "tmdb url"]


_ACTOR_NAME_VARIANT_MAP = str.maketrans(
    {
        "亜": "亚",
        "亞": "亚",
        "条": "条",
        "條": "条",
        "瀬": "濑",
        "濑": "濑",
        "沢": "泽",
        "澤": "泽",
        "桜": "樱",
        "櫻": "樱",
        "髙": "高",
        "﨑": "崎",
    }
)


def norm_name(name: str) -> str:
    return convert_half(name or "").translate(_ACTOR_NAME_VARIANT_MAP)


def _expand_name_variants(name: str) -> set[str]:
    normalized = norm_name(name)
    if not normalized:
        return set()

    variants = {normalized}

    if normalized.endswith("こ"):
        variants.add(normalized[:-1] + "子")
    if normalized.endswith("子"):
        variants.add(normalized[:-1] + "こ")

    return variants


def _get_db_path() -> Path:
    return manager.data_folder / "userdata" / "actor_database.xlsx"


def _format_db_worksheet(ws) -> None:
    """格式化演员数据库工作表：固定表头、自动筛选、列宽、边框、超链接、表头样式。"""
    try:
        import openpyxl
        from openpyxl.utils import get_column_letter

        # 固定表头
        ws.freeze_panes = "A2"

        # 自动筛选
        last_col = get_column_letter(len(DB_HEADERS))
        ws.auto_filter.ref = f"A1:{last_col}{ws.max_row}"

        # 表头样式
        header_fill = openpyxl.styles.PatternFill("solid", fgColor="F2F2F2")
        header_font = openpyxl.styles.Font(bold=True, size=11)
        header_align = openpyxl.styles.Alignment(horizontal="center", vertical="center", wrap_text=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align

        # 表格边框
        thin = openpyxl.styles.Side(style="thin", color="D0D0D0")
        border = openpyxl.styles.Border(left=thin, right=thin, top=thin, bottom=thin)
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=len(DB_HEADERS)):
            for cell in row:
                cell.border = border

        # 链接列和 tmdb url 列超链接：每次保存都校验并修复
        for row in ws.iter_rows(min_row=2, values_only=False):
            href_cell = row[COL_HREF]
            tmdb_cell = row[COL_TMDB_URL]
            href_val = str(href_cell.value or "").strip()
            if href_val and href_val.startswith("http"):
                existing_target = href_cell.hyperlink.target if href_cell.hyperlink else None
                if existing_target != href_val:
                    href_cell.hyperlink = href_val
                    href_cell.style = "Hyperlink"
            tmdb_val = str(tmdb_cell.value or "").strip()
            if tmdb_val and tmdb_val.startswith("http"):
                existing_target = tmdb_cell.hyperlink.target if tmdb_cell.hyperlink else None
                if existing_target != tmdb_val:
                    tmdb_cell.hyperlink = tmdb_val
                    tmdb_cell.style = "Hyperlink"

        # 自动列宽
        caps = {1: 25, 2: 15, 3: 15, 4: 60, 5: 50, 6: 12, 7: 42}
        col_max = [0] * (len(DB_HEADERS) + 1)
        for row in ws.iter_rows(min_row=2, values_only=True):
            for ci, cell in enumerate(row, 1):
                if cell is None or ci > len(DB_HEADERS):
                    continue
                s = str(cell)
                width = sum(2 if "\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" else 1 for c in s)
                col_max[ci] = max(col_max[ci], width)
        for ci in range(1, len(DB_HEADERS) + 1):
            letter = get_column_letter(ci)
            ws.column_dimensions[letter].width = min(col_max[ci] + 2, caps.get(ci, 80))
    except Exception:
        pass


def _norm_name_set(names: list[str]) -> set[str]:
    """生成一组规范化后的名字（全半角统一、零宽字符清理、大小写统一）"""
    result = set()
    for n in names:
        if n:
            result.update(_expand_name_variants(n))
    return result


def _full_to_half(s: str) -> str:
    result = []
    for ch in s:
        cp = ord(ch)
        if cp == 0x3000:
            result.append(" ")
        elif 0xFF01 <= cp <= 0xFF5E:
            result.append(chr(cp - 0xFEE0))
        else:
            result.append(ch)
    return "".join(result)


def _actor_index_keys(name: str) -> set[str]:
    if not name:
        return set()
    variants = _expand_name_variants(name)
    result = set(variants)
    result.add(_full_to_half(norm_name(name)).upper())
    for variant in variants:
        result.add(_full_to_half(variant).upper())
    return {key for key in result if key}


def _build_actor_db_reverse_index(actor_db: dict[str, dict]) -> dict[str, str]:
    index: dict[str, str] = {}
    for jp, data in actor_db.items():
        candidates = [jp]
        if data.get("zh_cn"):
            candidates.append(data["zh_cn"])
        if data.get("zh_tw"):
            candidates.append(data["zh_tw"])
        if data.get("keyword"):
            candidates.extend(k.strip() for k in data["keyword"].split(",") if k.strip())

        for candidate in candidates:
            for key in _actor_index_keys(candidate):
                index.setdefault(key, jp)
    return index


async def load_actor_db() -> dict[str, dict]:
    """
    加载演员数据库 xlsx。
    返回: {jp_name: {"zh_cn": ..., "zh_tw": ..., "keyword": "...", "href": "...", "tmdbid": int|None, "tmdb_url": "..."}}
    """
    db_path = _get_db_path()
    db: dict[str, dict] = {}
    if not db_path.exists():
        return db
    try:
        import openpyxl

        wb = openpyxl.load_workbook(db_path, read_only=True, data_only=True)
        ws = wb.active
        for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if row_idx == 1:
                continue
            if len(row) < 1:
                continue
            jp = str(row[COL_JP] or "").strip()
            if not jp:
                continue
            tmdbid_val = None
            tmdbid_raw = str(row[COL_TMDBID] or "").strip() if len(row) > COL_TMDBID else ""
            if tmdbid_raw and tmdbid_raw.isdigit():
                tmdbid_val = int(tmdbid_raw)
            db[jp] = {
                "zh_cn": str(row[COL_ZH_CN] or "").strip() if len(row) > COL_ZH_CN else "",
                "zh_tw": str(row[COL_ZH_TW] or "").strip() if len(row) > COL_ZH_TW else "",
                "keyword": str(row[COL_KEYWORD] or "").strip() if len(row) > COL_KEYWORD else "",
                "href": str(row[COL_HREF] or "").strip() if len(row) > COL_HREF else "",
                "tmdbid": tmdbid_val,
                "tmdb_url": str(row[COL_TMDB_URL] or "").strip() if len(row) > COL_TMDB_URL else "",
            }
        wb.close()
    except ImportError:
        pass
    except Exception:
        pass
    return db


async def update_actor_db_row(
    jp: str,
    zh_cn: str = "",
    zh_tw: str = "",
    keyword: str = "",
    href: str = "",
    tmdbid: int | None = None,
    append_keyword: bool = False,
) -> str:
    """
    更新或添加演员数据库行。已有值不覆盖，仅填空白；keyword 在 append_keyword=True 时追加去重。
    """
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import openpyxl

        write_status = "unchanged"

        if db_path.exists():
            wb = openpyxl.load_workbook(db_path)
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "演员数据库"
            for col, header in enumerate(DB_HEADERS, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = openpyxl.styles.Font(bold=True)
                cell.fill = openpyxl.styles.PatternFill("solid", fgColor="C0C0C0")
                cell.alignment = openpyxl.styles.Alignment(horizontal="center")

        ws = wb.active
        if ws.title != "演员数据库":
            ws.title = "演员数据库"

        existing_row = None
        for row_idx, row in enumerate(ws.iter_rows(min_col=1, max_col=7, values_only=True), start=1):
            if row_idx == 1:
                continue
            if str(row[0] or "").strip() == jp:
                existing_row = row_idx
                break

        if existing_row:
            if not ws.cell(row=existing_row, column=COL_ZH_CN + 1).value and zh_cn:
                ws.cell(row=existing_row, column=COL_ZH_CN + 1, value=zh_cn)
            if not ws.cell(row=existing_row, column=COL_ZH_TW + 1).value and zh_tw:
                ws.cell(row=existing_row, column=COL_ZH_TW + 1, value=zh_tw)

            if keyword:
                existing_kw = str(ws.cell(row=existing_row, column=COL_KEYWORD + 1).value or "").strip()
                if append_keyword:
                    new_kws = {k.strip() for k in keyword.split(",") if k.strip()}
                    existing_kws_set = set()
                    if existing_kw:
                        existing_kws_set = {k.strip() for k in existing_kw.split(",") if k.strip()}
                    merged = existing_kws_set | new_kws
                    ws.cell(row=existing_row, column=COL_KEYWORD + 1, value=",".join(sorted(merged)))
                elif not existing_kw:
                    ws.cell(row=existing_row, column=COL_KEYWORD + 1, value=keyword)

            if not ws.cell(row=existing_row, column=COL_HREF + 1).value and href:
                ws.cell(row=existing_row, column=COL_HREF + 1, value=href)
            if tmdbid is not None and not ws.cell(row=existing_row, column=COL_TMDBID + 1).value:
                ws.cell(row=existing_row, column=COL_TMDBID + 1, value=tmdbid)
                write_status = "inserted_tmdbid"
                ws.cell(row=existing_row, column=COL_TMDB_URL + 1).value = None
                ws.cell(
                    row=existing_row,
                    column=COL_TMDB_URL + 1,
                    value=f"https://www.themoviedb.org/person/{tmdbid}",
                )
                ws.cell(
                    row=existing_row, column=COL_TMDB_URL + 1
                ).hyperlink = f"https://www.themoviedb.org/person/{tmdbid}"
            elif tmdbid is not None:
                write_status = "kept_existing_tmdbid"
        else:
            ws.append([jp, zh_cn, zh_tw, keyword, href, tmdbid or "", ""])
            write_status = "inserted_new_row"
            last_row = ws.max_row
            if tmdbid:
                ws.cell(row=last_row, column=COL_TMDB_URL + 1).value = None
                ws.cell(
                    row=last_row,
                    column=COL_TMDB_URL + 1,
                    value=f"https://www.themoviedb.org/person/{tmdbid}",
                )
                ws.cell(row=last_row, column=COL_TMDB_URL + 1).hyperlink = f"https://www.themoviedb.org/person/{tmdbid}"

        _format_db_worksheet(ws)

        wb.save(db_path)
        wb.close()
        return write_status
    except ImportError:
        return "missing_openpyxl"
    except PermissionError:
        return "file_locked"
    except Exception as e:
        return f"write_failed:{e}"


def search_actor_db_reverse(query_name: str) -> dict | None:
    """
    反向搜索演员数据库：用任意语言的演员名搜索。返回匹配的整行数据，或 None。
    """
    actor_db = resources.actor_db
    if not actor_db:
        return None

    reverse_index = getattr(resources, "actor_db_reverse_index", None)
    if reverse_index is None:
        reverse_index = _build_actor_db_reverse_index(actor_db)
        resources.actor_db_reverse_index = reverse_index

    for key in _actor_index_keys(query_name):
        jp = reverse_index.get(key)
        if jp and jp in actor_db:
            data_copy = dict(actor_db[jp])
            data_copy["jp"] = jp
            return data_copy

    return None


# ============= XML → xlsx 迁移 =============


async def migrate_xml_to_xlsx() -> bool:
    """
    将 mapping_actor.xml + actor_tmdbid.xlsx 迁移到 actor_database.xlsx。
    迁移成功后返回 True。
    """
    db_path = _get_db_path()
    if db_path.exists():
        return True

    xml_path = manager.data_folder / "userdata" / "mapping_actor.xml"
    old_tmdb_path = manager.data_folder / "userdata" / "actor_tmdbid.xlsx"

    migrated = False
    try:
        if xml_path.exists():
            parser = None
            try:
                from lxml import etree

                parser = etree.HTMLParser(encoding="utf-8")
            except ImportError:
                pass
            if parser:
                content = await _read_text_file(xml_path)
                xml_data = etree.HTML(content.encode("utf-8"), parser)
                actor_objects = xml_data.xpath("//a")

                old_tmdb_cache = {}
                if old_tmdb_path.exists():
                    try:
                        import openpyxl

                        wb = openpyxl.load_workbook(old_tmdb_path, read_only=True, data_only=True)
                        ws = wb.active
                        for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
                            if row_idx == 1:
                                continue
                            if len(row) >= 2:
                                name = str(row[0] or "").strip()
                                tid = str(row[1] or "").strip()
                                if name and tid.isdigit():
                                    old_tmdb_cache[name] = int(tid)
                        wb.close()
                    except Exception:
                        pass

                import openpyxl

                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "演员数据库"
                for col, header in enumerate(DB_HEADERS, 1):
                    cell = ws.cell(row=1, column=col, value=header)
                    cell.font = openpyxl.styles.Font(bold=True)
                    cell.fill = openpyxl.styles.PatternFill("solid", fgColor="C0C0C0")
                    cell.alignment = openpyxl.styles.Alignment(horizontal="center")

                for ob in actor_objects:
                    jp = ob.get("jp") or ""
                    zh_cn = ob.get("zh_cn") or ""
                    zh_tw = ob.get("zh_tw") or ""
                    keyword = ob.get("keyword") or ""
                    href = ob.get("href") or ""

                    if not jp and keyword:
                        first_kw = keyword.strip(",").split(",")[0]
                        jp = first_kw

                    if not jp:
                        continue

                    tmdbid = old_tmdb_cache.get(jp)

                    ws.append([jp, zh_cn, zh_tw, keyword, href, tmdbid or "", ""])
                    if tmdbid:
                        last_row = ws.max_row
                        ws.cell(row=last_row, column=COL_TMDB_URL + 1).value = None
                        ws.cell(
                            row=last_row,
                            column=COL_TMDB_URL + 1,
                            value=f"https://www.themoviedb.org/person/{tmdbid}",
                        )
                        ws.cell(
                            row=last_row, column=COL_TMDB_URL + 1
                        ).hyperlink = f"https://www.themoviedb.org/person/{tmdbid}"

                _format_db_worksheet(ws)
                wb.save(db_path)
                wb.close()
                migrated = True
                LogBuffer.log().write(f"  ℹ️ [演员数据库] 已从 XML 迁移 {len(actor_objects)} 条记录")
    except Exception as e:
        LogBuffer.log().write(f"  ⚠️ [演员数据库] 迁移失败: {e}")

    return migrated


# ============= TMDB API 查询 =============


async def fetch_actor_tmdb_ids(actors: list[str], client: Any) -> dict[str, int]:
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

    actor_db = resources.actor_db or {}
    result: dict[str, int] = {}
    need_query: list[tuple[str, str]] = []

    for actor in actors:
        if not actor or not actor.strip():
            continue
        actor_stripped = actor.strip()
        row = None
        if actor_stripped in actor_db and actor_db[actor_stripped].get("tmdbid"):
            result[actor_stripped] = actor_db[actor_stripped]["tmdbid"]
            continue

        row = search_actor_db_reverse(actor_stripped)
        if row and row.get("tmdbid"):
            result[actor_stripped] = row["tmdbid"]
            LogBuffer.log().write(f"  ℹ️ [TMDB] {actor_stripped} -> tmdbid={row['tmdbid']} (xlsx反查缓存)")
            continue

        need_query.append((actor_stripped, row.get("jp") if row and row.get("jp") else actor_stripped))

    if not need_query:
        return result

    LogBuffer.log().write(f"\n 🎬 [TMDB] 开始查询 {len(need_query)} 个演员的 TMDB ID")

    async def _query_and_update(actor_name: str, query_name: str) -> None:
        try:
            query_result = await _query_single_actor(query_name, base_url, tmdb_api_key, client)
            if query_result:
                tmdbid = query_result["pid"]
                result[actor_name] = tmdbid

                translations = query_result.get("translations", {})
                zh_cn = translations.get("zh_cn", "")
                zh_tw = translations.get("zh_tw", "")
                aka = query_result.get("also_known_as", [])
                keyword_str = ",".join(aka) if aka else ""

                write_status = await update_actor_db_row(
                    jp=query_name,
                    zh_cn=zh_cn,
                    zh_tw=zh_tw,
                    keyword=keyword_str,
                    tmdbid=tmdbid,
                    append_keyword=True,
                )

                LogBuffer.log().write(
                    f"  ✅ [TMDB] {actor_name} -> tmdbid={tmdbid}{f' (中文:{zh_cn})' if zh_cn else ''}"
                )
                if write_status == "inserted_tmdbid":
                    LogBuffer.log().write(f"  ✅ [演员数据库] 已写入 {actor_name} -> tmdbid={tmdbid}")
                elif write_status == "inserted_new_row":
                    LogBuffer.log().write(f"  ✅ [演员数据库] 已新增 {actor_name}，并写入 tmdbid={tmdbid}")
                elif write_status == "kept_existing_tmdbid":
                    LogBuffer.log().write(f"  ℹ️ [演员数据库] {actor_name} 已存在 tmdbid，保留原值")
                elif write_status == "missing_openpyxl":
                    LogBuffer.log().write(f"  ⚠️ [演员数据库] 缺少 openpyxl，未写入 {actor_name} 的 tmdbid")
                elif write_status == "file_locked":
                    LogBuffer.log().write(f"  ⚠️ [演员数据库] 文件被占用，未写入 {actor_name} 的 tmdbid")
                elif write_status.startswith("write_failed:"):
                    LogBuffer.log().write(
                        f"  ⚠️ [演员数据库] 写入失败，未保存 {actor_name} 的 tmdbid: {write_status.split(':', 1)[1]}"
                    )
            else:
                LogBuffer.log().write(f"  ⚠️ [TMDB] {actor_name} 未找到匹配的 TMDB 演员")
        except Exception as e:
            LogBuffer.log().write(f"  ❌ [TMDB] {actor_name} 查询失败: {e}")

    semaphore = asyncio.Semaphore(3)

    async def _limited_query(actor_name: str, query_name: str) -> None:
        async with semaphore:
            await _query_and_update(actor_name, query_name)

    tasks = [asyncio.create_task(_limited_query(actor_name, query_name)) for actor_name, query_name in need_query]
    await asyncio.gather(*tasks)

    old_db = dict(resources.actor_db) if resources.actor_db else {}
    resources.reload_actor_db()

    cached_before = len([a for a in actors if a.strip() in old_db and old_db[a.strip()].get("tmdbid")])
    LogBuffer.log().write(
        f" 🎬 [TMDB] 查询完成: 缓存命中 {len(actors) - len(need_query)} 个, "
        f"本次匹配 {len(result) - cached_before} 个, 共 {len(result)} 个"
    )
    return result


async def _query_single_actor(actor_name: str, base_url: str, api_key: str, client: Any) -> dict | None:
    """
    查询单个演员的 TMDB 信息。返回匹配结果或 None。
    """
    search_url = f"{base_url}/3/search/person"
    target_variants = _expand_name_variants(actor_name)

    resp = await _tmdb_request(
        client,
        "GET",
        search_url,
        params={
            "api_key": api_key,
            "query": actor_name,
            "include_adult": "true",
            "language": "zh-CN",
            "page": 1,
        },
    )

    if resp is None or resp.status_code != 200:
        return None

    try:
        data = resp.json()
    except (json.JSONDecodeError, ValueError):
        return None
    results = data.get("results", [])

    if _tmdb_debug_enabled():
        LogBuffer.log().write(
            f"  🔎 [TMDB] 搜索演员「{actor_name}」返回 {len(results)} 个候选，目标规范名={sorted(target_variants)}"
        )
    else:
        LogBuffer.log().write(f"  🔎 [TMDB] 搜索演员「{actor_name}」返回 {len(results)} 个候选")

    if not results:
        return None

    candidates: list[dict] = []

    for item in results[:5]:
        pid = item.get("id")
        if not pid:
            continue

        gender = item.get("gender")
        if gender not in (0, 1):
            continue

        detail_url = f"{base_url}/3/person/{pid}"
        detail_resp = await _tmdb_request(client, "GET", detail_url, params={"api_key": api_key, "language": "zh-CN"})

        if detail_resp is None or detail_resp.status_code != 200:
            continue

        try:
            detail = detail_resp.json()
        except (json.JSONDecodeError, ValueError):
            continue
        place = detail.get("place_of_birth", "")

        all_names = set()
        for x in [item.get("name"), item.get("original_name"), detail.get("name")]:
            if x:
                all_names.add(str(x).strip())
        aka_list = detail.get("also_known_as", [])
        for a in aka_list:
            if a:
                all_names.add(str(a).strip())

        all_norm = _norm_name_set(list(all_names))
        is_match = bool(target_variants & all_norm)

        _pop = item.get("popularity", 0) or 0
        popularity = float(_pop) if isinstance(_pop, (int, float, str)) else 0.0
        known_for_count = len(detail.get("known_for", [])) if "known_for" in detail else 0
        place_has_japan = is_japan_place(place)

        translations = await _fetch_person_translations(pid, base_url, api_key, client)

        candidates.append(
            {
                "pid": pid,
                "is_match": is_match,
                "adult": bool(item.get("adult")),
                "popularity": popularity,
                "known_for_count": known_for_count,
                "place_has_japan": place_has_japan,
                "name": detail.get("name", ""),
                "raw_names": sorted(all_names),
                "all_norm": sorted(all_norm),
                "translations": translations,
                "also_known_as": [a for a in aka_list if a],
            }
        )

        if _tmdb_debug_enabled():
            LogBuffer.log().write(
                f"    {'✅' if is_match else '·'} [TMDB] pid={pid} name={detail.get('name', '')} "
                f"place={place or '-'} aliases={sorted(all_names)} norm={sorted(all_norm)}"
            )

    matched = [c for c in candidates if c["is_match"]]

    if not matched:
        LogBuffer.log().write(f"  ⚠️ [TMDB] 演员「{actor_name}」所有候选均未通过名字匹配")
        return None

    matched.sort(
        key=lambda x: (x["place_has_japan"], x["adult"], x["popularity"], x["known_for_count"]),
        reverse=True,
    )

    if len(matched) > 1:
        LogBuffer.log().write(
            f"  ⚠️ [TMDB] 演员「{actor_name}」匹配到 {len(matched)} 个结果，"
            f"已自动选择 tmdbid={matched[0]['pid']} "
            f"(popularity={matched[0]['popularity']:.2f})"
        )

    return matched[0]


async def _fetch_person_translations(pid: int, base_url: str, api_key: str, client: Any) -> dict:
    """
    从 TMDB translations API 获取演员的多语言翻译。
    """
    result = {"zh_cn": "", "zh_tw": ""}
    try:
        trans_url = f"{base_url}/3/person/{pid}/translations"
        trans_resp = await _tmdb_request(client, "GET", trans_url, params={"api_key": api_key})
        if trans_resp is None or trans_resp.status_code != 200:
            return result

        try:
            trans_data = trans_resp.json()
        except (json.JSONDecodeError, ValueError):
            return result
        for trans in trans_data.get("translations", []):
            iso = trans.get("iso_639_1", "")
            region = trans.get("iso_3166_1", "")
            en_name = trans.get("english_name", "")
            data = trans.get("data", {})
            native_name = data.get("name", "")

            if iso == "zh" and region == "CN":
                result["zh_cn"] = data.get("name") or en_name or ""
            elif iso == "zh" and region == "TW":
                result["zh_tw"] = data.get("name") or en_name or ""
            elif iso == "zh":
                name_to_use = native_name or en_name
                if name_to_use:
                    if not result["zh_cn"]:
                        result["zh_cn"] = name_to_use
                    if not result["zh_tw"]:
                        result["zh_tw"] = name_to_use
    except Exception:
        pass

    return result


# ============= Info XML → xlsx 迁移 =============


async def migrate_info_xml_to_xlsx() -> bool:
    """
    将 mapping_info.xml 迁移到 info_database.xlsx。
    迁移成功后返回 True。
    """
    from openpyxl.utils import get_column_letter

    db_path = manager.data_folder / "userdata" / "info_database.xlsx"
    if db_path.exists():
        return True

    xml_path = manager.data_folder / "userdata" / "mapping_info.xml"
    if not xml_path.exists():
        return False

    try:
        parser = None
        try:
            from lxml import etree

            parser = etree.HTMLParser(encoding="utf-8")
        except ImportError:
            pass
        if not parser:
            return False

        content = await _read_text_file(xml_path)
        xml_data = etree.HTML(content.encode("utf-8"), parser)
        info_objects = xml_data.xpath("//a")

        try:
            import openpyxl
        except ImportError:
            LogBuffer.log().write("  ⚠️ [信息映射表] 缺少 openpyxl 库，无法迁移")
            return False

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "信息映射表"
        headers = ["日文名", "中文名", "繁体名", "别名"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill("solid", fgColor="C0C0C0")
            cell.alignment = openpyxl.styles.Alignment(horizontal="center")

        for ob in info_objects:
            jp = ob.get("jp") or ""
            zh_cn = ob.get("zh_cn") or ""
            zh_tw = ob.get("zh_tw") or ""
            keyword = ob.get("keyword") or ""
            ws.append([jp, zh_cn, zh_tw, keyword])

        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)) + 2)
                except (TypeError, AttributeError):
                    pass
            adjusted_width = min(max_length, 30)
            ws.column_dimensions[column].width = adjusted_width

        wb.save(db_path)
        wb.close()
        LogBuffer.log().write(f"  ℹ️ [信息映射表] 已从 XML 迁移 {len(info_objects)} 条记录")
        return True
    except Exception as e:
        LogBuffer.log().write(f"  ⚠️ [信息映射表] 迁移失败: {e}")
        return False
