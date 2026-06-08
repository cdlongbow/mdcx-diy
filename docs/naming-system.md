# 命名系统

> 本文档从 CODE_WIKI.md 提取,详见完整文档

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

使用 **Jinja2** 模板引擎:

```jinja2
# 简单变量
{{ number }}

# 条件渲染
{% if number %}{{ number }}{% endif %}

# 条件嵌套
[{% if number %}{{ number }}{% endif %}]{% if title and title != number %}{{ title }}{% endif %}

# 循环(高级用法)
{% for actor in actors %}{{ actor }}{% if not loop.last %}, {% endif %}{% endfor %}
```

## 常用模板

**目录模板**:
```jinja2
{{ actor }}/{{ number }} {{ actor }}
```

**文件模板**:
```jinja2
{{ number }}
```

**媒体模板**:
```jinja2
[{% if number %}{{ number }}{% endif %}]{% if title and title != number %}{{ title }}{% endif %}
```

## 智能截断

支持按优先级截断字段以适应最大长度限制:

1. 按优先级截断字段
2. 列表字段(演员、导演)按分隔符截断
3. 普通文本直接截断
4. 移除末尾标点和空格

---

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [配置系统](configuration.md) - 配置管理详解
- [数据模型](data-models.md) - 数据结构定义
