import sys
import types
from pathlib import Path


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
        self.nfo_tag_series = "series"
        self.nfo_tagline = "release"
        self.add_genre_to_tag = False
        self.extra_genres = False
        self.add_tag_to_genre = False
        self.original_nfo_title = False
        self.use_simple_tag = False
        self.website = ""


class _DummyManager:
    def __init__(self):
        self.config = _DummyConfig()
        self.data_folder = Path("/tmp/mdcx-tests")

    def acquire_computed(self):
        raise RuntimeError("Tests should not acquire computed clients")


class _DummyResources:
    def __init__(self):
        self.actor_db = {}
        self.info_db = []


manager_module = types.ModuleType("mdcx.config.manager")
manager_module.manager = _DummyManager()
manager_module.get_new_str = lambda a, wanted=False: a
sys.modules.setdefault("mdcx.config.manager", manager_module)

resources_module = types.ModuleType("mdcx.config.resources")
resources_module.resources = _DummyResources()
sys.modules.setdefault("mdcx.config.resources", resources_module)

signals_module = types.ModuleType("mdcx.signals")
signals_module.signal = _DummySignals()
signals_module.signal_qt = signals_module.signal
signals_module.set_signal = lambda signal_instance: None
sys.modules.setdefault("mdcx.signals", signals_module)
