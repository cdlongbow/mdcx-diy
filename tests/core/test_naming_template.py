from pathlib import Path

import pytest

from mdcx.config.manager import manager
from mdcx.core.file import _generate_file_name, _get_folder_path
from mdcx.core.naming import NameRenderOptions, NamingTarget, render_name
from mdcx.models.model_types import CrawlersResult, FileInfo


def _build_file_info() -> FileInfo:
    file_info = FileInfo.empty()
    file_info.number = "ABC-123"
    file_info.file_path = Path("D:/Media/Input/ABC-123.mp4")
    file_info.folder_path = file_info.file_path.parent
    file_info.file_name = "ABC-123"
    file_info.definition = "1080P"
    return file_info


def _build_result() -> CrawlersResult:
    result = CrawlersResult.empty()
    result.number = "ABC-123"
    result.title = "中文标题"
    result.originaltitle = "Original Title"
    result.release = "2024-01-02"
    result.letters = "ABC"
    return result


def test_empty_field_does_not_remove_user_written_wrappers():
    file_info = _build_file_info()
    result = _build_result()
    result.studio = ""

    rendered = render_name(
        "{{ number }} ({{ filename }}) [{{ studio }}], {{ originaltitle }}, {{ definition }}",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FILE),
    )

    assert rendered.text == "ABC-123 (ABC-123) [], Original Title, 1080P"


def test_jinja_if_segment_is_rendered_only_when_field_has_value():
    file_info = _build_file_info()
    result = _build_result()

    rendered_empty = render_name(
        "{{ number }}{% if studio %} [{{ studio }}]{% endif %}",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FILE),
    )
    result.studio = "Studio A"
    rendered_present = render_name(
        "{{ number }}{% if studio %} [{{ studio }}]{% endif %}",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FILE),
    )

    assert rendered_empty.text == "ABC-123"
    assert rendered_present.text == "ABC-123 [Studio A]"


def test_unknown_template_field_raises_clear_error():
    file_info = _build_file_info()
    result = _build_result()

    with pytest.raises(Exception, match="studioo"):
        render_name(
            "{{ number }} {{ studioo }}",
            file_info,
            result,
            NameRenderOptions(target=NamingTarget.FILE),
        )


def test_number_title_duplicate_is_collapsed_for_media_title():
    file_info = _build_file_info()
    result = _build_result()
    result.title = "ABC-123"

    rendered = render_name(
        "[{{ number }}]{% if title and title != number %}{{ title }}{% endif %}",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.NFO_TITLE),
    )

    assert rendered.text == "[ABC-123]"


def test_plain_legacy_text_is_not_interpreted_as_fields(monkeypatch):
    file_info = _build_file_info()
    result = _build_result()
    file_info.c_word = "-中字"

    monkeypatch.setattr(manager.config, "suffix_sort", [])
    rendered = render_name(
        "numbercnword originaltitle",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FILE),
    )

    assert rendered.text == "numbercnword originaltitle"


def test_folder_template_keeps_template_separator_and_escapes_field_separator(monkeypatch):
    file_info = _build_file_info()
    result = _build_result()
    result.title = "A/B"

    monkeypatch.setattr(manager.config, "folder_name", "{{ letters }}/{{ title }}")
    monkeypatch.setattr(manager.config, "folder_name_max", 60)
    monkeypatch.setattr(manager.config, "folder_moword", False)
    monkeypatch.setattr(manager.config, "folder_hd", False)
    monkeypatch.setattr(manager.config, "folder_cnword", False)
    monkeypatch.setattr(manager.config, "success_file_move", True)
    monkeypatch.setattr(manager.config, "main_mode", 1)
    monkeypatch.setattr(manager.config, "soft_link", 0)

    _, folder_name = _get_folder_path(Path("D:/Media/Output"), file_info, result)

    assert folder_name == "ABC/A-B"


def test_folder_segment_keeps_user_written_hyphen_edges():
    file_info = _build_file_info()
    result = _build_result()

    rendered = render_name(
        "{{ letters }}/-{{ number }}-",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FOLDER),
    )

    assert rendered.text == "ABC/-ABC-123"


def test_long_originaltitle_is_truncated_but_number_is_kept(monkeypatch):
    file_info = _build_file_info()
    result = _build_result()
    result.originaltitle = "很长的原标题" * 20

    monkeypatch.setattr(manager.config, "folder_name", "{{ number }} {{ originaltitle }}")
    monkeypatch.setattr(manager.config, "folder_name_max", 32)
    monkeypatch.setattr(manager.config, "folder_moword", False)
    monkeypatch.setattr(manager.config, "folder_hd", False)
    monkeypatch.setattr(manager.config, "folder_cnword", False)
    monkeypatch.setattr(manager.config, "success_file_move", True)
    monkeypatch.setattr(manager.config, "main_mode", 1)
    monkeypatch.setattr(manager.config, "soft_link", 0)

    _, folder_name = _get_folder_path(Path("D:/Media/Output"), file_info, result)

    assert folder_name.startswith("ABC-123 ")
    assert len(folder_name) <= 32
    assert "..." not in folder_name


def test_truncated_folder_segment_does_not_end_with_dot_or_ellipsis(monkeypatch):
    file_info = _build_file_info()
    result = _build_result()
    result.title = "浜崎真緒, 望月彩花, 黒川紗里奈, 今井ほのか"

    monkeypatch.setattr(manager.config, "folder_name", "{{ title }}/{{ number }}")
    monkeypatch.setattr(manager.config, "folder_name_max", 28)
    monkeypatch.setattr(manager.config, "folder_moword", False)
    monkeypatch.setattr(manager.config, "folder_hd", False)
    monkeypatch.setattr(manager.config, "folder_cnword", False)
    monkeypatch.setattr(manager.config, "success_file_move", True)
    monkeypatch.setattr(manager.config, "main_mode", 1)
    monkeypatch.setattr(manager.config, "soft_link", 0)

    _, folder_name = _get_folder_path(Path("D:/Media/Output"), file_info, result)

    assert folder_name.endswith("/ABC-123")
    assert "..." not in folder_name
    assert all(part and not part.endswith((".", " ")) for part in folder_name.split("/"))


def test_actor_truncation_keeps_complete_actor_names(monkeypatch):
    file_info = _build_file_info()
    result = _build_result()
    result.actor = "浜崎真緒,望月彩花,黒川紗里奈,今井ほのか"

    monkeypatch.setattr(manager.config, "folder_name", "{{ actor }}/{{ number }}")
    monkeypatch.setattr(manager.config, "folder_name_max", 16)
    monkeypatch.setattr(manager.config, "actor_name_max", 10)
    monkeypatch.setattr(manager.config, "folder_moword", False)
    monkeypatch.setattr(manager.config, "folder_hd", False)
    monkeypatch.setattr(manager.config, "folder_cnword", False)
    monkeypatch.setattr(manager.config, "success_file_move", True)
    monkeypatch.setattr(manager.config, "main_mode", 1)
    monkeypatch.setattr(manager.config, "soft_link", 0)

    _, folder_name = _get_folder_path(Path("D:/Media/Output"), file_info, result)

    assert folder_name == "浜崎真緒/ABC-123"


def test_actor_truncation_drops_field_when_first_actor_does_not_fit(monkeypatch):
    file_info = _build_file_info()
    result = _build_result()
    result.actor = "VeryLongActorName,SecondActor"

    monkeypatch.setattr(manager.config, "folder_name", "{{ actor }}/{{ number }}")
    monkeypatch.setattr(manager.config, "folder_name_max", 10)
    monkeypatch.setattr(manager.config, "actor_name_max", 10)
    monkeypatch.setattr(manager.config, "folder_moword", False)
    monkeypatch.setattr(manager.config, "folder_hd", False)
    monkeypatch.setattr(manager.config, "folder_cnword", False)
    monkeypatch.setattr(manager.config, "success_file_move", True)
    monkeypatch.setattr(manager.config, "main_mode", 1)
    monkeypatch.setattr(manager.config, "soft_link", 0)

    _, folder_name = _get_folder_path(Path("D:/Media/Output"), file_info, result)

    assert folder_name == "ABC-123"


def test_folder_segments_avoid_windows_reserved_names(monkeypatch):
    file_info = _build_file_info()
    result = _build_result()
    result.actor = "CON"
    result.title = "COM1.txt"

    monkeypatch.setattr(manager.config, "folder_name", "{{ actor }}/{{ title }}")
    monkeypatch.setattr(manager.config, "folder_name_max", 60)
    monkeypatch.setattr(manager.config, "folder_moword", False)
    monkeypatch.setattr(manager.config, "folder_hd", False)
    monkeypatch.setattr(manager.config, "folder_cnword", False)
    monkeypatch.setattr(manager.config, "success_file_move", True)
    monkeypatch.setattr(manager.config, "main_mode", 1)
    monkeypatch.setattr(manager.config, "soft_link", 0)

    _, folder_name = _get_folder_path(Path("D:/Media/Output"), file_info, result)

    assert folder_name == "CON_/COM1_.txt"


def test_final_hard_truncate_is_sanitized_for_folder_segments():
    file_info = _build_file_info()
    result = _build_result()
    result.actor = "Actor"
    result.title = "Title"

    rendered = render_name(
        "abcdef./Title",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FOLDER, max_length=7),
    )

    assert rendered.text == "abcdef"
    assert all(part and not part.endswith((".", " ")) for part in rendered.text.split("/"))


def test_generate_file_name_uses_new_template(monkeypatch):
    file_info = _build_file_info()
    result = _build_result()
    result.studio = ""

    monkeypatch.setattr(
        manager.config,
        "naming_file",
        "{{ number }}{% if studio %} [{{ studio }}]{% endif %} {{ definition }}",
    )
    monkeypatch.setattr(manager.config, "file_name_max", 60)
    monkeypatch.setattr(manager.config, "file_moword", False)
    monkeypatch.setattr(manager.config, "file_hd", False)
    monkeypatch.setattr(manager.config, "file_cnword", False)
    monkeypatch.setattr(manager.config, "prevent_char", "")
    monkeypatch.setattr(manager.config, "success_file_rename", True)
    monkeypatch.setattr(manager.config, "main_mode", 1)

    assert _generate_file_name("", file_info, result) == "ABC-123 1080P"


def test_single_actor_value_clipped_not_wiped():
    """议题 #93：单演员（无分隔符）超宽时应回退字符级截断，而非整字段清空丢目录。"""
    file_info = _build_file_info()
    result = _build_result()
    result.actor = "A" * 50
    result.number = "MIDV-757"

    rendered = render_name(
        "{{ actor }}/{{ number }}",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FOLDER, max_length=20),
    )

    # 旧实现 _clip_list 会把无分隔符的单值清空 -> 只剩 number（0 个 A）；
    # 新实现回退字符级截断，保留大量 A，演员一级目录不丢失
    assert rendered.text.endswith("/MIDV-757")
    assert rendered.text.count("A") >= 10
    assert len(rendered.text) <= 20
    assert rendered.truncated_fields == ["actor"]


def test_series_clipped_before_actor_in_folder_template():
    """议题 #93：系列名过长时应先缩系列、保留 {{ actor }} 一级目录，而非先丢演员。"""
    file_info = _build_file_info()
    result = _build_result()
    result.series = "很长的系列名" * 40
    result.actor = "小野六"
    result.number = "MIDV-757"

    rendered = render_name(
        "{{ series }}/{{ actor }}/{{ number }}",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FOLDER, max_length=40),
    )

    assert rendered.truncated_fields == ["series"]
    assert "小野六" in rendered.text
    assert "MIDV-757" in rendered.text
    assert len(rendered.text) <= 40


def test_directory_segment_truncation_is_stable_across_files():
    """议题 #95：同系列文件即便标题/演员长短不同，系列一级目录也必须一致。"""
    template = "{{ series }}/{{ actor }}/[{{ release }}]{{ number }}~{{ title }}"
    long_series = ("両親が旅行で不在中に幼馴染がやってきて" * 10)[:108]

    def render_for(title: str, actor: str, number: str, release: str) -> str:
        file_info = _build_file_info()
        result = _build_result()
        result.series = long_series
        result.actor = actor
        result.title = title
        result.number = number
        result.release = release
        rendered = render_name(
            template,
            file_info,
            result,
            NameRenderOptions(target=NamingTarget.FOLDER, max_length=140),
        )
        return rendered.text

    # A：其它字段都很短，整体未超限，但系列仍被主动截到稳定预算
    short_file = render_for("短", "泉百华", "MIDA-209", "2025-07-10")
    # B：标题/演员更长，整体超限
    long_file = render_for("很长很长的标题" * 10, "小野六花", "MIDV-757", "2024-06-28")

    assert short_file.split("/")[0] == long_file.split("/")[0]
    assert long_series.startswith(short_file.split("/")[0])
    assert "MIDV-757" in long_file


def test_truncated_log_lists_only_template_fields():
    """议题 #93：不在模板里的字段（简介/原标题）不应出现在「已智能缩短」日志里。"""
    file_info = _build_file_info()
    result = _build_result()
    result.outline = "很长的简介" * 40
    result.originaltitle = "Original" * 30
    result.title = "很长的标题" * 30
    result.number = "MIDV-757"

    rendered = render_name(
        "{{ title }}/{{ number }}",
        file_info,
        result,
        NameRenderOptions(target=NamingTarget.FOLDER, max_length=30),
    )

    assert rendered.truncated_fields == ["title"]
    assert "outline" not in rendered.truncated_fields
    assert "originaltitle" not in rendered.truncated_fields
    assert len(rendered.text) <= 30
