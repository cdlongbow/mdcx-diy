# 依赖关系

> 本文档从 CODE_WIKI.md 提取,详见完整文档

---

## 主要依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `PyQt6` | ==6.11.0 | UI 框架 |
| `httpx[socks]` | >=0.28.1 | HTTP 客户端（支持 SOCKS 代理） |
| `curl-cffi` | ==0.11.4 | 浏览器指纹伪装 |
| `parsel` | >=1.10.0 | HTML 解析 |
| `lxml` | >=5.2.0 | XML/HTML 解析 |
| `beautifulsoup4` | ==4.13.4 | HTML 解析 |
| `pydantic-settings` | >=2.10.1 | 数据验证与配置管理 |
| `aiofiles` | ==24.1.0 | 异步文件操作 |
| `Pillow` | ==11.3.0 | 图片处理 |
| `opencv-contrib-python-headless` | ==4.13.0.92 | 人脸裁剪（无 GUI 依赖版） |
| `av` | >=15.0.0 | 视频处理 |
| `Jinja2` | >=3.1.6 | 模板引擎 |
| `openpyxl` | >=3.1.0 | Excel 处理 |
| `defusedxml` | >=0.7.1 | 安全 XML 解析（防止 XXE 攻击） |
| `aiolimiter` | ==1.2.1 | 异步限流器 |
| `oshash` | ==0.1.1 | OpenSubtitles 哈希 |
| `ping3` | ==4.0.4 | 网络延迟检测 |
| `zhconv` | ==1.4.3 | 简繁中文转换 |
| `openai` | ==1.91.0 | LLM 翻译 API 客户端 |

## 开发依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `pytest` | >=8.4.1 | 测试框架 |
| `pytest-asyncio` | >=1.1.0 | 异步测试支持 |
| `pytest-cov` | >=6.2.1 | 测试覆盖率 |
| `ruff` | >=0.15.0,<0.16.0 | 代码检查和格式化 |
| `pre-commit` | >=4.2.0 | Git Hooks 管理 |
| `pyinstaller` | >=6.14.2 | 打包发布 |
| `rich` | >=14.1.0 | 终端美化输出 |
| `typer` | >=0.16.0 | CLI 框架 |
| `types-lxml` | >=2025.3.30 | lxml 类型桩 |
| `ipykernel` | >=6.30.1 | Jupyter 内核 |

## 网络层

**异步 HTTP 客户端**:
- `httpx.AsyncClient`:主要 HTTP 客户端
- `curl_cffi.AsyncWebClient`:浏览器指纹伪装

**特性**:
- 连接池管理
- 请求限流（aiolimiter）
- 浏览器指纹伪装
- 支持 SOCKS 代理

## 数据持久层

**配置存储**:
- JSON 格式(V2)
- INI 格式(V1,已废弃)

**演员数据库**:
- Excel 格式(`.xlsx`)
- 使用 `openpyxl` 读写

## 日志系统

**信号机制** ([mdcx/signals.py](../mdcx/signals.py)):
- Qt 信号机制
- 线程安全的日志系统
- UI 更新信号

---

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [配置系统](configuration.md) - 配置管理详解
- [爬虫系统](crawler-system.md) - 爬虫框架详解
- [工具模块](tools.md) - 工具模块详解
