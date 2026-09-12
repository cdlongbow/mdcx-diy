import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ...models.model_types import CrawlersResult, FileInfo
from .fields import TRUNCATE_PRIORITY, NamingContext, build_naming_context
from .sanitize import cleanup_rendered_text, sanitize_name
from .template import collect_template_fields, render_template

LIST_TRUNCATE_FIELDS = {"actor", "all_actor", "director"}

# 目录级字段（模板中构成路径一级的 series/actor 等）的稳定截断：为模板里的其它
# 变量字段各预留的最小宽度。截断预算只依赖模板结构与最大长度、不依赖同一批次其它
# 文件的字段长度，保证同一 series/actor 值恒定截成同一目录名（议题 #95）。
DIRECTORY_FIELD_MIN_WIDTH = 8

_JINJA_TAG_PATTERN = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", re.DOTALL)
_FIELD_TOKEN_PATTERN = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)
_FIELD_NAME_PATTERN = re.compile(r"^\s*(?:fields\.)?([A-Za-z_][A-Za-z0-9_]*)")


class NamingTarget(Enum):
    FOLDER = "folder"
    FILE = "file"
    NFO_TITLE = "nfo_title"


@dataclass(frozen=True)
class NameRenderOptions:
    target: NamingTarget
    show_definition_suffix: bool = False
    show_cnword_suffix: bool = False
    show_moword_suffix: bool = False
    max_length: int | None = None


@dataclass(frozen=True)
class NameRenderResult:
    text: str
    template: str
    context: NamingContext
    truncated_fields: list[str] = field(default_factory=list)

    def value(self, field: str) -> str:
        return self.context.get(field)


def _clip_text(value: str, max_length: int) -> str:
    if max_length <= 0:
        return ""
    if len(value) <= max_length:
        return value
    return value[:max_length].rstrip(" ,，、;；:：._+-")


def _clip_list(value: str, max_length: int) -> str:
    if max_length <= 0:
        return ""
    if len(value) <= max_length:
        return value

    delimiter_match = re.search(r"[,，、]", value)
    if not delimiter_match:
        # 单值（无分隔符）无法按项丢弃，回退到字符级截断，避免整字段被清空
        # （议题 #93：单演员目录超宽时被 _clip_list 直接置空，丢失 {{ actor }} 一级目录）
        return _clip_text(value, max_length)

    delimiter = delimiter_match.group(0)
    parts = [part.strip() for part in re.split(r"[,，、]", value) if part.strip()]
    kept: list[str] = []
    for part in parts:
        candidate = delimiter.join([*kept, part])
        if len(candidate) > max_length:
            break
        kept.append(part)
    return delimiter.join(kept)


def _clip_field(field_name: str, value: str, max_length: int) -> str:
    if field_name in LIST_TRUNCATE_FIELDS:
        return _clip_list(value, max_length)
    return _clip_text(value, max_length)


def _finalize_text(text: str, target: NamingTarget) -> str:
    if target == NamingTarget.NFO_TITLE:
        return cleanup_rendered_text(text)
    return sanitize_name(text, allow_path_separator=target == NamingTarget.FOLDER)


def _render_with_values(template: str, values: dict[str, Any], target: NamingTarget) -> str:
    return _finalize_text(render_template(template, values), target)


def _directory_segment_fields(template: str) -> set[str]:
    """找出模板里构成路径一级的字段（其与下一个字段之间存在 "/"）。

    这类字段通常是 series/actor 一级目录名。截断它们会改变归档目录归属，因此必须
    使用与其它字段长度无关的稳定预算，避免同系列/同演员的文件被分到不同目录。
    """
    matches = list(_FIELD_TOKEN_PATTERN.finditer(template or ""))
    fields: set[str] = set()
    for index, match in enumerate(matches):
        after_end = matches[index + 1].start() if index + 1 < len(matches) else len(template or "")
        if "/" not in (template or "")[match.end() : after_end]:
            continue
        name_match = _FIELD_NAME_PATTERN.match(match.group(1))
        if name_match:
            fields.add(name_match.group(1))
    return fields


def _stable_directory_budgets(
    template: str,
    target: NamingTarget,
    max_length: int,
) -> dict[str, int]:
    """计算目录级字段的稳定截断预算（不随其它字段内容变化）。"""
    if target != NamingTarget.FOLDER or max_length <= 0:
        return {}
    directory_fields = _directory_segment_fields(template)
    if not directory_fields:
        return {}

    template_fields = collect_template_fields(template)
    literal_length = len(_JINJA_TAG_PATTERN.sub("", str(template or "")))
    reserved = DIRECTORY_FIELD_MIN_WIDTH * max(0, len(template_fields) - 1)
    budget = max(1, max_length - literal_length - reserved)
    return {field: budget for field in directory_fields if field in template_fields}


def _smart_truncate(
    template: str,
    values: dict[str, Any],
    target: NamingTarget,
    max_length: int,
) -> tuple[str, list[str]]:
    text = _render_with_values(template, values, target)
    if max_length <= 0:
        return text, []

    # 只对模板实际用到的字段做智能缩短：模板外的字段（如未启用的简介/原标题）
    # 既不影响结果，也不该出现在「已智能缩短」日志里（议题 #93 误导性日志）。
    template_fields = collect_template_fields(template)
    was_over = len(text) > max_length
    truncated_fields: list[str] = []
    mutable_values = values.copy()

    # 目录级字段先按稳定预算截断（议题 #95）：同一 series/actor 值在任一文件里都被
    # 截成同一长度，不因同批次其它文件的标题/演员长短不同而分裂归档目录。
    stable_budgets = _stable_directory_budgets(template, target, max_length)
    for field_name in TRUNCATE_PRIORITY:
        budget = stable_budgets.get(field_name)
        if budget is None:
            continue
        current = mutable_values.get(field_name, "")
        if not current or len(current) <= budget:
            continue
        mutable_values[field_name] = _clip_field(field_name, current, budget)
        truncated_fields.append(field_name)
    if truncated_fields:
        text = _render_with_values(template, mutable_values, target)

    if not was_over:
        # 目录级字段为一致性做了主动截断，但整体未超限，无需报告「已缩短」。
        return text, []

    for field_name in TRUNCATE_PRIORITY:
        if len(text) <= max_length:
            break
        if field_name not in template_fields:
            continue
        if field_name in stable_budgets:
            # 目录级字段只走稳定预算，不参与溢出量分摊，避免不同文件截出不同目录名
            continue
        current = mutable_values.get(field_name, "")
        if not current:
            continue
        overflow = len(text) - max_length
        next_length = max(len(current) - overflow, 0)
        next_value = _clip_field(field_name, current, next_length)
        if next_value == current:
            continue
        mutable_values[field_name] = next_value
        truncated_fields.append(field_name)
        text = _render_with_values(template, mutable_values, target)

    if len(text) > max_length:
        text = text[:max_length].rstrip(" ,，、;；:：._+-")
        text = _finalize_text(text, target)
    return text, truncated_fields


def render_name(
    template: str, file_info: FileInfo, data: CrawlersResult, options: NameRenderOptions
) -> NameRenderResult:
    context = build_naming_context(
        file_info,
        data,
        show_definition_suffix=options.show_definition_suffix,
        show_cnword_suffix=options.show_cnword_suffix,
        show_moword_suffix=options.show_moword_suffix,
        escape_path_separator=options.target != NamingTarget.NFO_TITLE,
    )
    values: dict[str, Any] = context.values.copy()
    values["fields"] = context.values

    text, truncated_fields = _smart_truncate(
        template,
        values,
        options.target,
        int(options.max_length or 0),
    )
    fallback = context.get("number") or context.get("title") or context.get("filename") or "MDCx"
    if not text:
        text = sanitize_name(fallback, allow_path_separator=False)
    return NameRenderResult(text=text, template=template, context=context, truncated_fields=truncated_fields)
