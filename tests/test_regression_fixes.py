"""回归测试：验证已修复的 bug。

这些测试不依赖完整项目导入，直接测试修复的逻辑。
"""

import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

# 仓库根目录：相对本文件定位，避免硬编码 /workspace（CI 容器约定路径在本地不存在）。
REPO = Path(__file__).resolve().parent.parent


# ============================================================
# Bug 1: 运算符优先级 — mdcx/core/utils.py:141
# 修复前: key == OUTLINE or key == ORIGINALPLOT and len(value) > 100
# 修复后: (key == OUTLINE or key == ORIGINALPLOT) and len(value) > 100
# ============================================================
def test_operator_precedence_fix():
    """验证 show_movie_info 中 OUTLINE/ORIGINALPLOT 的截断条件正确加括号。"""
    source = (REPO / "mdcx/core/utils.py").read_text()
    # 检查修复后的代码包含括号
    assert (
        "(key == CrawlerResultFields.OUTLINE or key == CrawlerResultFields.ORIGINALPLOT) and len(value) > 100" in source
    ), "运算符优先级未修复：括号缺失"


def test_operator_precedence_logic():
    """验证修复前后的逻辑差异。"""
    OUTLINE = "outline"
    ORIGINALPLOT = "originalplot"

    # 修复前的逻辑（and 优先级高于 or）
    def old_logic(key, value):
        return key == OUTLINE or key == ORIGINALPLOT and len(value) > 100

    # 修复后的逻辑（括号确保 or 先求值）
    def new_logic(key, value):
        return (key == OUTLINE or key == ORIGINALPLOT) and len(value) > 100

    long_value = "x" * 200
    short_value = "short"

    # OUTLINE + 短值：修复前=True（bug），修复后=False（正确）
    assert old_logic(OUTLINE, short_value) is True  # bug: 无条件为 True
    assert new_logic(OUTLINE, short_value) is False  # 修复后: 短值不截断

    # OUTLINE + 长值：修复前=True，修复后=True
    assert old_logic(OUTLINE, long_value) is True
    assert new_logic(OUTLINE, long_value) is True

    # ORIGINALPLOT + 短值：修复前=False，修复后=False
    assert old_logic(ORIGINALPLOT, short_value) is False
    assert new_logic(ORIGINALPLOT, short_value) is False

    # ORIGINALPLOT + 长值：修复前=True，修复后=True
    assert old_logic(ORIGINALPLOT, long_value) is True
    assert new_logic(ORIGINALPLOT, long_value) is True

    # 其他 key + 长值：修复前=False，修复后=False
    assert old_logic("title", long_value) is False
    assert new_logic("title", long_value) is False


# ============================================================
# Bug 2: asyncio 未导入 — mdcx/core/file.py
# 修复前: import os (重复), 缺少 import asyncio
# 修复后: import asyncio, import os
# ============================================================
def test_asyncio_import_exists():
    """验证 file.py 导入了 asyncio。"""
    source = (REPO / "mdcx/core/file.py").read_text()
    assert "import asyncio" in source, "asyncio 未导入"


def test_no_duplicate_os_import():
    """验证 file.py 没有重复的 import os。"""
    source = (REPO / "mdcx/core/file.py").read_text()
    count = source.count("import os")
    assert count == 1, f"import os 出现了 {count} 次，应该有 1 次"


# ============================================================
# Bug 3: 异步中同步 time.sleep — scraper.py, tmdb_actor.py
# 修复前: time.sleep(0.5)
# 修复后: await asyncio.sleep(0.5)
# ============================================================
def test_no_blocking_sleep_in_async_scraper():
    """验证 scraper.py 的异步函数中不再使用同步 time.sleep。"""
    source = (REPO / "mdcx/core/scraper.py").read_text()
    # 检查 _process_one_file_with_context 方法中的 TMDB 部分
    # 找到 time.sleep 的行，确认不在 await 上下文中
    lines = source.split("\n")
    in_async_context = False
    for i, line in enumerate(lines):
        if "async def _process_one_file_with_context" in line:
            in_async_context = True
        elif in_async_context and line.strip().startswith("async def "):
            in_async_context = False
        if in_async_context and "time.sleep(" in line and "asyncio" not in line:
            raise AssertionError(f"scraper.py:{i + 1} 异步函数中使用同步 time.sleep: {line.strip()}")


def test_no_blocking_sleep_in_async_tmdb_actor():
    """验证 tmdb_actor.py 的异步函数中不再使用同步 time.sleep。"""
    source = (REPO / "mdcx/core/tmdb_actor.py").read_text()
    lines = source.split("\n")
    in_async_context = False
    for i, line in enumerate(lines):
        if "async def fetch_actor_tmdb_ids" in line:
            in_async_context = True
        elif in_async_context and line.strip().startswith("async def "):
            in_async_context = False
        elif in_async_context and line.strip().startswith("def "):
            in_async_context = False
        if in_async_context and "time.sleep(" in line and "asyncio" not in line:
            raise AssertionError(f"tmdb_actor.py:{i + 1} 异步函数中使用同步 time.sleep: {line.strip()}")


def test_asyncio_sleep_used():
    """验证修复后使用非阻塞的 asyncio.sleep(而非 time.sleep)。"""
    scraper = (REPO / "mdcx/core/scraper.py").read_text()
    tmdb = (REPO / "mdcx/core/tmdb_actor.py").read_text()
    assert "await asyncio.sleep(" in scraper
    assert "await asyncio.sleep(" in tmdb


# ============================================================
# Bug 4: 阻塞 shutil.rmtree — mdcx/core/file.py
# 修复前: shutil.rmtree(path, ignore_errors=True)
# 修复后: await asyncio.to_thread(shutil.rmtree, path, ignore_errors=True)
# ============================================================
def test_no_blocking_rmtree_in_async():
    """验证 file.py 中 async 函数不再直接调用 shutil.rmtree。"""
    source = (REPO / "mdcx/core/file.py").read_text()
    lines = source.split("\n")
    # 找到所有 shutil.rmtree 调用
    for i, line in enumerate(lines):
        stripped = line.strip()
        if "shutil.rmtree" in stripped and not stripped.startswith("#"):
            assert "asyncio.to_thread" in stripped, f"file.py:{i + 1} 同步调用 shutil.rmtree: {stripped}"


def test_rmtree_async_nonblocking():
    """验证 asyncio.to_thread(shutil.rmtree) 不会阻塞事件循环。"""
    import time

    async def main():
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试目录
            test_dir = Path(tmpdir) / "test_subdir"
            test_dir.mkdir()
            (test_dir / "file.txt").write_text("hello")

            start = time.monotonic()
            # 使用 to_thread 删除
            await asyncio.to_thread(shutil.rmtree, test_dir, ignore_errors=True)
            elapsed = time.monotonic() - start

            assert not test_dir.exists(), "目录未删除"
            assert elapsed < 1.0, f"删除操作耗时过长: {elapsed}s"

    asyncio.run(main())


# ============================================================
# Bug 5: get_file_info_v2 静默吞异常
# 修复前: except Exception: (无 as e, 无 LogBuffer.error)
# 修复后: except Exception as e: + LogBuffer.error().write(...)
# ============================================================
def test_get_file_info_v2_exception_bound():
    """验证 get_file_info_v2 最外层 except 子句绑定了异常对象并写入 LogBuffer.error。"""
    source = (REPO / "mdcx/core/file.py").read_text()
    lines = source.split("\n")
    # 找到 "except Exception as e:" 后面紧跟 LogBuffer.error().write 的行
    found = False
    for i, line in enumerate(lines):
        if "except Exception as e:" in line and i > 600:  # get_file_info_v2 的 except 在 ~681 行
            for j in range(i + 1, min(i + 5, len(lines))):
                if "LogBuffer.error()" in lines[j] and "get_file_info_v2 error" in lines[j]:
                    found = True
                    break
    assert found, "get_file_info_v2 的最外层 except 未绑定异常或写入 LogBuffer.error"


# ============================================================
# Bug 6: Flags.file_done_dic[number] KeyError
# 修复前: Flags.file_done_dic[number]["local_poster"]
# 修复后: Flags.file_done_dic.get(number, {}).get("local_poster")
# ============================================================
def test_file_done_dic_safe_access():
    """验证 file.py 中 Flags.file_done_dic[number]["local_*"] 使用安全访问。"""
    source = (REPO / "mdcx/core/file.py").read_text()
    lines = source.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        # 只检查 elif p := 模式下的直接索引访问（读取），排除 .update() 写入
        if "Flags.file_done_dic" in stripped and "[number][" in stripped:
            raise AssertionError(f"file.py:{i + 1} 直接索引访问 Flags.file_done_dic[number][...]: {stripped}")
        # 验证修复后的 .get() 模式存在
    for field in ["local_poster", "local_thumb", "local_fanart"]:
        assert f'.get(number, {{}}).get("{field}")' in source, f"file.py 中缺少安全的 .get() 访问模式: {field}"


# ============================================================
# Bug 7: definition 可能为 None — naming/fields.py
# 修复前: file_info.definition.replace("UHD8", "UHD")
# 修复后: (file_info.definition or "").replace("UHD8", "UHD")
# ============================================================
def test_definition_none_safety():
    """验证 definition 字段在 None 时不会抛出 AttributeError。"""
    source = (REPO / "mdcx/core/naming/fields.py").read_text()
    assert '(file_info.definition or "").replace("UHD8", "UHD")' in source, "definition 未做 None 防护"


# ============================================================
# Bug 8: nfo.py 异常处理改进
# 修复前: print(traceback.format_exc()) / pass
# 修复后: LogBuffer.log().write(traceback.format_exc())
# ============================================================
def test_nfo_exception_logging():
    """验证 nfo.py 中异常处理不再使用 print 或 pass。"""
    source = (REPO / "mdcx/core/nfo.py").read_text()
    lines = source.split("\n")

    # 检查 score 部分的 except
    for i, line in enumerate(lines):
        if "except Exception:" in line:
            # 检查下一行
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                assert next_line != "pass", f"nfo.py:{i + 1} except 块使用 pass 静默吞异常"
                assert "print(traceback" not in next_line, f"nfo.py:{i + 1} except 块使用 print 输出 traceback"


# ============================================================
# Bug 9: start_new_scrape 异常未绑定
# 修复前: except Exception:
# 修复后: except Exception as e: + LogBuffer.error().write(...)
# ============================================================
def test_start_new_scrape_exception_bound():
    """验证 start_new_scrape 的 except 子句绑定了异常对象。"""
    source = (REPO / "mdcx/core/scraper.py").read_text()
    lines = source.split("\n")
    in_function = False
    for i, line in enumerate(lines):
        if "def start_new_scrape" in line:
            in_function = True
        elif in_function and line.strip().startswith("def "):
            in_function = False
        if in_function and "except Exception" in line:
            assert "as e" in line, f"scraper.py:{i + 1} except 未绑定异常对象: {line.strip()}"


# ============================================================
# 死代码清理验证
# ============================================================
def test_no_dead_code_in_core_files():
    """验证核心文件中已清理注释掉的死代码。"""
    checks = {
        "main.py": ["newWin2 = CutWindow()"],
        "mdcx/core/utils.py": ["json_data[each] = json_data[each].replace"],
        "mdcx/core/scraper.py": [
            "res.outline = split_path(file_path)[1]",
            "res.tag = file_path",
            "self.move_trailer_video",
        ],
        "mdcx/core/nfo.py": ["json_data.website = website"],
    }
    for file_path, dead_patterns in checks.items():
        source = (REPO / file_path).read_text()
        for pattern in dead_patterns:
            # 检查是否有注释掉的该行（# 开头）
            for line in source.split("\n"):
                stripped = line.strip()
                if stripped.startswith("#") and pattern in stripped:
                    raise AssertionError(f"{file_path} 中存在死代码: {stripped}")


if __name__ == "__main__":
    import pytest as _pytest

    sys.exit(_pytest.main([__file__, "-v"]))
