# 命名系统

> 本文档从 CODE_WIKI.md 提取，详见完整文档

---

## 模块结构 ([mdcx/core/naming/](../mdcx/core/naming/))

```
mdcx/core/naming/
├── fields.py            # 字段定义和上下文构建
├── template.py          # 模板引擎
├── renderer.py          # 命名渲染
└── sanitize.py          # 名称清理
```

## 支持的字段

| 字段名 | 说明 |
|--------|------|
| `number` | 番号 |
| `title` | 标题 |
| `originaltitle` | 原始标题 |
| `actor` | 演员列表 |
| `first_actor` | 首位演员 |
| `all_actor` | 全部演员 |
| `letters` | 番号前缀 |
| `first_letter` | 番号首字符 |
| `outline` | 简介 |
| `director` | 导演 |
| `series` | 系列 |
| `studio` | 片商 |
| `publisher` | 发行商 |
| `release` | 发行日期 |
| `year` | 年份 |
| `runtime` | 时长 |
| `mosaic` | 有码/无码 |
| `definition` | 清晰度 |
| `cnword` | 字幕标识 |
| `moword` | 版本标识 |
| `filename` | 原文件名 |
| `wanted` | 想看人数 |
| `score` | 评分 |
| `four_k` | 4K 标识 |

## 模板语法

命名模板使用 **Jinja2** 模板引擎。Jinja2 用 `{{ }}` 输出变量，用 `{% %}` 写逻辑。

```jinja2
# 输出一个字段的值
{{ number }}

# 只有当字段有值时，才显示
{% if number %}{{ number }}{% endif %}

# 条件嵌套：有番号时显示方括号，有标题时显示标题
[{% if number %}{{ number }}{% endif %}]{% if title and title != number %}{{ title }}{% endif %}

# 循环：把多个演员用逗号连接起来
{% for actor in actors %}{{ actor }}{% if not loop.last %}, {% endif %}{% endfor %}
```

简单说：`{{ 字段名 }}` 表示"把这里替换成实际值"，`{% if 条件 %}` 表示"有这个值才显示"。

## 常用模板

**目录模板**：
```jinja2
{{ actor }}/{{ number }} {{ actor }}
```
效果：生成类似 `演员名/番号 演员名` 的文件夹。

**文件模板**：
```jinja2
{{ number }}
```
效果：直接用番号命名文件。

**媒体模板**：
```jinja2
[{% if number %}{{ number }}{% endif %}]{% if title and title != number %}{{ title }}{% endif %}
```
效果：有番号就加 `[番号]`，标题和番号不同时，再拼接标题。

## 智能截断

Windows 和部分系统对文件名长度有限制。系统会自动截断过长的字段：

1. 按优先级决定先截断哪个字段
2. 列表字段（演员、导演）按分隔符截断
3. 普通文本直接截断
4. 去掉末尾的标点和空格

简单说：如果文件路径太长，系统会优先砍掉不重要的字段，确保文件名不超限。

---

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [配置系统](configuration.md) - 配置管理详解
- [数据模型](data-models.md) - 数据结构定义