import sys
import types
from pathlib import Path
from types import SimpleNamespace

from mdcx.config.enums import Language


class _DummySignal:
    def emit(self, *args, **kwargs):
        return None


class _DummySignals:
    def __init__(self):
        self.log_text = _DummySignal()
        self.scrape_info = _DummySignal()
        self.net_info = _DummySignal()
        self.exec_set_main_info = _DummySignal()
        self.change_buttons_status = _DummySignal()
        self.reset_buttons_status = _DummySignal()
        self.set_label_file_path = _DummySignal()
        self.label_result = _DummySignal()
        self.logs_failed_settext = _DummySignal()
        self.view_success_file_settext = _DummySignal()
        self.exec_set_processbar = _DummySignal()
        self.exec_exit_app = _DummySignal()
        self.view_failed_list_settext = _DummySignal()
        self.exec_show_list_name = _DummySignal()
        self.logs_failed_show = _DummySignal()

    def add_log(self, *args, **kwargs):
        return None

    def show_traceback_log(self, *args, **kwargs):
        return None

    def show_log_text(self, *args, **kwargs):
        return None

    def show_scrape_info(self, *args, **kwargs):
        return None

    def show_net_info(self, *args, **kwargs):
        return None

    def set_main_info(self, *args, **kwargs):
        return None

    def show_list_name(self, *args, **kwargs):
        return None


class _DummyConfig:
    def __init__(self):
        self.show_data_log = False
        self.download_files = []
        self.keep_files = []
        self.outline_format = []
        self.main_mode = 1
        self.naming_media = "number title"
        self.update_titletemplate = "number title"
        self.nfo_include_new = []
        self.actor_no_name = "佚名"
        self.read_mode = []
        self.nfo_tag_series = "series"
        self.nfo_tagline = "release"
        self.add_genre_to_tag = False
        self.extra_genres = False
        self.add_tag_to_genre = False
        self.original_nfo_title = False
        self.use_simple_tag = False
        self.website = ""
        self.tmdb_api_key = ""
        self.tmdb_api_base = ""

    def get_field_config(self, _field):
        return SimpleNamespace(language=Language.JP, translate=False)


class _DummyManager:
    def __init__(self):
        self.config = _DummyConfig()
        self.data_folder = Path("/tmp/mdcx-tests")

    def acquire_computed(self):
        raise RuntimeError("Tests should not acquire computed clients")


class _DummyResources:
    def __init__(self):
        self.actor_db = {}
        self.actor_db_reverse_index = None
        self.info_db = []
        self.info_mapping_data = None

    def u(self, relative_path):
        return manager_module.manager.data_folder / "userdata" / relative_path

    def get_actor_data(self, actor):
        from mdcx.core.tmdb_actor import search_actor_db_reverse

        actor_data = {
            "zh_cn": actor,
            "zh_tw": actor,
            "jp": actor,
            "keyword": [actor],
            "href": "",
            "has_name": False,
        }

        if self.actor_db is not None:
            row = search_actor_db_reverse(actor)
            if row:
                actor_data["zh_cn"] = row.get("zh_cn") or actor
                actor_data["zh_tw"] = row.get("zh_tw") or actor
                actor_data["jp"] = row.get("jp") or actor
                kw = row.get("keyword") or ""
                actor_data["keyword"] = [k.strip() for k in kw.split(",") if k.strip()] if kw else [actor_data["jp"]]
                actor_data["href"] = row.get("href") or ""
                actor_data["has_name"] = True
        return actor_data

    def get_info_data(self, info):
        info_data = {
            "zh_cn": info,
            "zh_tw": info,
            "jp": info,
            "keyword": [info],
            "has_name": False,
        }

        info_key = info.upper()
        for row in self.info_db or []:
            matched = False
            if row.get("keyword"):
                for kw in row["keyword"].split(","):
                    kw = kw.strip()
                    if kw and kw.upper() == info_key:
                        matched = True
                        break
            if not matched:
                for attr in ("zh_cn", "zh_tw", "jp"):
                    if (row.get(attr) or "").upper() == info_key:
                        matched = True
                        break
            if matched:
                info_data["zh_cn"] = row.get("zh_cn") or info
                info_data["zh_tw"] = row.get("zh_tw") or info
                info_data["jp"] = row.get("jp") or info
                kw = row.get("keyword") or ""
                info_data["keyword"] = [k.strip() for k in kw.split(",") if k.strip()] if kw else [info]
                info_data["has_name"] = True
                return info_data
        return info_data

    def reload_actor_db(self):
        import openpyxl

        db_path = self.u("actor_database.xlsx")
        if not db_path.exists():
            self.actor_db = None
            self.actor_db_reverse_index = None
            return

        old_actor_db = self.actor_db
        try:
            wb = openpyxl.load_workbook(db_path, read_only=True, data_only=True)
            ws = wb.active
            db = {}
            for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
                if row_idx == 1:
                    continue
                jp = str(row[0] or "").strip()
                if not jp:
                    continue
                tmdbid_val = None
                if len(row) > 5:
                    tmdbid_raw = str(row[5] or "").strip()
                    if tmdbid_raw.isdigit():
                        tmdbid_val = int(tmdbid_raw)
                db[jp] = {
                    "zh_cn": str(row[1] or "").strip() if len(row) > 1 else "",
                    "zh_tw": str(row[2] or "").strip() if len(row) > 2 else "",
                    "keyword": str(row[3] or "").strip() if len(row) > 3 else "",
                    "href": str(row[4] or "").strip() if len(row) > 4 else "",
                    "tmdbid": tmdbid_val,
                    "tmdb_url": str(row[6] or "").strip() if len(row) > 6 else "",
                }
            wb.close()
            self.actor_db = db
            self.actor_db_reverse_index = None
        except Exception:
            self.actor_db = old_actor_db


manager_module = types.ModuleType("mdcx.config.manager")
manager_module.manager = _DummyManager()
manager_module.get_new_str = lambda a, wanted=False: a
sys.modules.setdefault("mdcx.config.manager", manager_module)

resources_module = types.ModuleType("mdcx.config.resources")
resources_module.COL_JP = 0
resources_module.COL_ZH_CN = 1
resources_module.COL_ZH_TW = 2
resources_module.COL_KEYWORD = 3
resources_module.COL_HREF = 4
resources_module.COL_TMDBID = 5
resources_module.COL_TMDB_URL = 6
resources_module.DB_HEADERS = ["日文原名", "中文名", "繁体名", "别名", "链接", "tmdbid", "tmdb url"]
resources_module._tmdb_person_url = lambda tid: f"https://www.themoviedb.org/person/{tid}"
resources_module.read_actor_db_xlsx = lambda db_path: {}
resources_module.resources = _DummyResources()
sys.modules.setdefault("mdcx.config.resources", resources_module)

signals_module = types.ModuleType("mdcx.signals")
signals_module.signal = _DummySignals()
signals_module.signal_qt = signals_module.signal
signals_module.set_signal = lambda signal_instance: None
sys.modules.setdefault("mdcx.signals", signals_module)
