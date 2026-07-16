#!/usr/bin/env python3
import json
import os
import platform
import sys

from PIL import ImageFile
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from mdcx.consts import IS_DOCKER, IS_MAC, IS_NFC, IS_PYINSTALLER, IS_WINDOWS, MAIN_PATH
from mdcx.controllers.main_window.main_window import MyMAinWindow
from mdcx.controllers.main_window.style import apply_application_palette
from mdcx.core.tmdb_actor import flush_tmdb_query_cache
from mdcx.utils.video import get_video_backend

ImageFile.LOAD_TRUNCATED_IMAGES = True


def _apply_ui_scale_factor():
    mark_file = MAIN_PATH / "MDCx.config"
    if not mark_file.is_file():
        return
    with open(mark_file, encoding="UTF-8") as f:
        config_path = f.read().strip()
    if not config_path or not os.path.isfile(config_path):
        return
    with open(config_path, encoding="UTF-8") as f:
        config = json.load(f)
    scale = config.get("ui_scale_factor", 0.0)
    if scale > 0:
        os.environ["QT_SCALE_FACTOR"] = str(scale)


def show_constants():
    """显示所有运行时常量"""
    constants = {
        "MAIN_PATH": MAIN_PATH,
        "IS_WINDOWS": IS_WINDOWS,
        "IS_MAC": IS_MAC,
        "IS_DOCKER": IS_DOCKER,
        "IS_NFC": IS_NFC,
        "IS_PYINSTALLER": IS_PYINSTALLER,
        "VIDEO_BACKEND": get_video_backend(),
    }
    print("Run time constants:")
    for key, value in constants.items():
        print(f"\t{key}: {value}")


def _create_application() -> tuple[QApplication, MyMAinWindow]:
    if os.path.isfile("highdpi_passthrough"):
        # Qt6 默认启用高 DPI，这里仅保留非整数缩放策略开关，避免 150% 缩放被取整。
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    if platform.system() != "Windows":
        app.setStyle("Fusion")
    apply_application_palette(False)
    if platform.system() != "Windows":
        app.setWindowIcon(QIcon("resources/Img/MDCx.ico"))  # 设置任务栏图标

    ui = MyMAinWindow()
    ui.show()
    app.installEventFilter(ui)
    return app, ui


def main() -> int:
    show_constants()
    _apply_ui_scale_factor()
    app, _ui = _create_application()
    try:
        return_code = app.exec()
        return return_code
    except Exception as e:
        print(e)
        return 1
    finally:
        flush_tmdb_query_cache()


if __name__ == "__main__":
    sys.exit(main())
