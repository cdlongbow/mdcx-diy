#!/usr/bin/env python3
"""
TMDB ID 验证工具（GUI 版，但自动降级为 CLI 如果没有 tkinter）
"""

import os
from pathlib import Path

# 检查 tkinter
HAS_TKINTER = False
try:
    import tkinter  # noqa: F401

    HAS_TKINTER = True
    print("✅ tkinter 可用，使用 GUI 模式")
except ImportError:
    print("⚠️  tkinter 不可用，使用命令行模式")
    print("   安装：sudo apt-get install python3-tk")

# 导入 GUI 版本
if HAS_TKINTER:
    os.system(f"python3 '{Path(__file__).parent / 'verify_actor_tmdb_gui.py'}'")
else:
    # 命令行版本
    print("\n📋 命令行模式说明:")
    print("  python3 scripts/verify_actor_tmdb_gui.py resources/userdata/actor_database.xlsx [验证数量]")
    print("\n示例:")
    print("  python3 scripts/verify_actor_tmdb_gui.py resources/userdata/actor_database.xlsx 100")
    print("  (验证前 100 条记录)")
