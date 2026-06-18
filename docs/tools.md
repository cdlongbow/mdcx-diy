# 工具模块

> 本文档从 CODE_WIKI.md 提取，详见完整文档

---

## 演员数据库 ([mdcx/tools/actress_db.py](../mdcx/tools/actress_db.py))

**功能**：管理 Excel 格式的演员数据库

**主要功能**：
- 加载演员数据库
- 搜索演员信息
- 更新演员数据

简单说：这个工具让你用 Excel 表格管理演员信息，可以查、改、增。

## Emby 演员 ([mdcx/tools/emby_actor_info.py](../mdcx/tools/emby_actor_info.py))

**功能**：更新 Emby/Jellyfin 演员信息

**数据来源**：
- Wikipedia：获取简介、出生日期、出生地等
- 本地数据库：获取中文名、别名等

## Emby 演员图片 ([mdcx/tools/emby_actor_image.py](../mdcx/tools/emby_actor_image.py))

**功能**：更新 Emby/Jellyfin 演员图片

**图片来源**：
- graphis.ne.jp：日本写真网站
- Gfriends 本地仓库/GitHub：头像库
- 本地文件夹

## 缺失文件检测 ([mdcx/tools/missing.py](../mdcx/tools/missing.py))

**功能**：检测缺失的文件

简单说：帮你找出媒体库里少了哪些文件。

## 字幕管理 ([mdcx/tools/subtitle.py](../mdcx/tools/subtitle.py))

**功能**：批量字幕处理

## Wiki 工具 ([mdcx/tools/wiki.py](../mdcx/tools/wiki.py))

**功能**：查询 Wikipedia 信息

---

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [数据模型](data-models.md) - 数据结构定义
- [配置系统](configuration.md) - 配置管理详解
- [爬虫系统](crawler-system.md) - 爬虫框架详解
