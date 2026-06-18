# 依赖关系

> 本文档从 CODE_WIKI.md 提取,详见完整文档

---

## 主要依赖

这些是项目运行时必需的库。

| 依赖 | 版本 | 用途 |
|------|------|------|
| `PyQt6` | ==6.11.0 | UI 框架，用来画界面 |
| `httpx[socks]` | >=0.28.1 | HTTP 客户端，支持 SOCKS 代理 |
| `curl-cffi` | ==0.11.4 | 模拟浏览器指纹，绕过反爬 |
| `parsel` | >=1.10.0 | 解析 HTML |
| `lxml` | >=5.2.0 | 解析 XML 和 HTML |
| `beautifulsoup4` | ==4.13.4 | 解析 HTML |
| `pydantic-settings` | >=2.10.1 | 数据验证和配置管理 |
| `aiofiles` | ==24.1.0 | 异步读写文件 |
| `Pillow` | ==11.3.0 | 处理图片 |
| `opencv-contrib-python-headless` | ==4.13.0.92 | 人脸裁剪（不带 GUI 的版本） |
| `av` | >=15.0.0 | 处理视频 |
| `Jinja2` | >=3.1.6 | 模板引擎，渲染文本 |
| `openpyxl` | >=3.1.0 | 读写 Excel 文件 |
| `defusedxml` | >=0.7.1 | 安全解析 XML，防止 XXE 攻击 |
| `aiolimiter` | ==1.2.1 | 异步限流，控制请求频率 |
| `oshash` | ==0.1.1 | OpenSubtitles 哈希算法 |
| `ping3` | ==4.0.4 | 测试网络延迟 |
| `zhconv` | ==1.4.3 | 简体繁体中文互转 |
| `openai` | ==1.91.0 | 调用 LLM 做翻译 |

## 开发依赖

这些是开发和测试时才需要的库。

| 依赖 | 版本 | 用途 |
|------|------|------|
| `pytest` | >=8.4.1 | 测试框架 |
| `pytest-asyncio` | >=1.1.0 | 支持异步测试 |
| `pytest-cov` | >=6.2.1 | 统计测试覆盖率 |
| `ruff` | >=0.15.0,<0.16.0 | 代码检查和格式化 |
| `pre-commit` | >=4.2.0 | 管理 Git Hooks（提交前自动检查） |
| `pyinstaller` | >=6.14.2 | 打包成可执行文件 |
| `rich` | >=14.1.0 | 终端美化输出 |
| `typer` | >=0.16.0 | CLI 框架，建命令行工具 |
| `types-lxml` | >=2025.3.30 | lxml 的类型提示 |
| `ipykernel` | >=6.30.1 | Jupyter 内核 |

## 网络层

**异步 HTTP 客户端**：
- `httpx.AsyncClient`：主要的 HTTP 客户端
- `curl_cffi.AsyncWebClient`：模拟浏览器指纹

**特性**：
- 连接池管理（复用已建立的连接）
- 请求限流（aiolimiter，控制请求速度）
- 浏览器指纹伪装（curl-cffi，降低被拦截的概率）
- 支持 SOCKS 代理

## 数据持久层

**配置存储**：
- JSON 格式（V2，新版）
- INI 格式（V1，已废弃）

**演员数据库**：
- Excel 格式（`.xlsx`）
- 使用 `openpyxl` 读写

## 日志系统

**信号机制**（[mdcx/signals.py](../mdcx/signals.py)）：
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