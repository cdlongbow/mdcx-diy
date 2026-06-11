import asyncio
from asyncio import Event
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict

from .enums import FileMode
from .types import ScrapeResult


class FileDoneDict(TypedDict):
    poster: Path | None
    thumb: Path | None
    fanart: Path | None
    trailer: Path | None
    local_poster: Path | None
    local_thumb: Path | None
    local_fanart: Path | None
    local_trailer: Path | None


def _new_lock():
    return asyncio.Lock()


@dataclass
class _Flags:
    _counter_lock: asyncio.Lock = field(default_factory=_new_lock, repr=False)

    async def increment(self, name: str, value: int = 1) -> int:
        async with self._counter_lock:
            current = getattr(self, name, 0) + value
            setattr(self, name, current)
            return current

    # 指定刮削 #todo 改为传参
    appoint_url: str = ""
    website_name: str = ""

    # 刮削相关
    rest_time_convert: int = 0
    rest_time_convert_: int = 0
    total_kills: int = 0
    now_kill: int = 0
    success_save_time: float = 0.0
    next_start_time: float = 0.0
    count_claw: int = 0
    can_save_remain: bool = False
    remain_list: list[Path] = field(default_factory=list)
    new_again_dic: dict[Path, tuple[str, str, str]] = field(default_factory=dict)
    again_dic: dict[Path, tuple[str, str, str]] = field(default_factory=dict)
    start_time: float = 0.0
    file_mode: FileMode = FileMode.Default
    counting_order: int = 0
    total_count: int = 0
    rest_now_begin_count: int = 0
    sleep_end: Event = field(default_factory=Event)
    rest_next_begin_time: float = 0.0
    scrape_starting: int = 0
    scrape_started: int = 0
    scrape_done: int = 0
    succ_count: int = 0
    fail_count: int = 0
    file_new_path_dic: dict[Path, list[Path]] = field(default_factory=dict)
    pic_catch_set: set[Path] = field(default_factory=set)
    file_done_dic: dict[str, FileDoneDict] = field(default_factory=dict)
    extrafanart_deal_set: set[Path] = field(default_factory=set)
    trailer_deal_set: set[Path] = field(default_factory=set)
    theme_videos_deal_set: set[Path] = field(default_factory=set)
    nfo_deal_set: set[Path] = field(default_factory=set)
    json_get_set: set[str] = field(default_factory=set)
    json_get_status: dict[str, bool | None] = field(default_factory=dict)
    json_data_dic: dict[str, ScrapeResult] = field(default_factory=dict)
    img_path: str = ""
    failed_list: list[tuple[Path, str]] = field(default_factory=list)
    scrape_start_time: float = 0.0
    success_list: set[Path] = field(default_factory=set)
    stop_other: bool = True
    stop_requested: bool = False

    # show
    log_txt: Any = None
    scrape_like_text: str = ""
    main_mode_text: str = ""

    single_file_path: Path = field(default_factory=Path)

    # for missing
    actor_numbers_dic: dict[str, list[str]] = field(default_factory=dict)
    local_number_set: set[str] = field(default_factory=set)
    local_number_cnword_set: set[str] = field(default_factory=set)

    def reset(self) -> None:
        self.failed_list = []
        self.counting_order = 0
        self.total_count = 0
        self.rest_now_begin_count = 0
        self.sleep_end.set()
        self.scrape_starting = 0
        self.scrape_started = 0
        self.scrape_done = 0
        self.succ_count = 0
        self.fail_count = 0
        self.file_new_path_dic = {}
        self.pic_catch_set = set()
        self.file_done_dic = {}
        self.extrafanart_deal_set = set()
        self.trailer_deal_set = set()
        self.theme_videos_deal_set = set()
        self.nfo_deal_set = set()
        self.json_get_set = set()
        self.json_get_status = {}
        self.json_data_dic = {}
        self.img_path = ""
        self.stop_requested = False
        self.stop_other = True
        self.scrape_start_time = 0.0
        self.success_list = set()
        self.next_start_time = 0.0
        self.total_kills = 0
        self.now_kill = 0
        self.success_save_time = 0.0
        self.rest_time_convert = 0
        self.rest_time_convert_ = 0
        self.rest_next_begin_time = 0.0
        self.single_file_path = Path()
        self.actor_numbers_dic = {}
        self.local_number_set = set()
        self.local_number_cnword_set = set()


Flags = _Flags()
