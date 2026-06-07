# 依赖关系

> 本文档从 CODE_WIKI.md 提取,详见完整文档

---

## 主要依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `PyQt6` | >=6.0 | UI 框架 |
| `httpx` | >=0.24 | HTTP 客户端 |
| `curl-cffi` | >=0.5 | 浏览器指纹伪装 |
| `parsel` | >=1.8 | HTML 解析 |
| `lxml` | >=4.9 | XML/HTML 解析 |
| `beautifulsoup4` | >=4.12 | HTML 解析 |
| `pydantic` | >=2.0 | 数据验证 |
| `asyncio` | - | 异步处理 |
| `aiofiles` | >=23.0 | 异步文件操作 |
| `Pillow` | >=9.0 | 图片处理 |
| `opencv-python` | >=4.8 | 人脸裁剪 |
| `av` | >=10.0 | 视频处理 |
| `Jinja2` | >=3.1 | 模板引擎 |
| `openpyxl` | >=3.1 | Excel 处理 |

## 网络层

**异步 HTTP 客户端**:
- `httpx.AsyncClient`:主要 HTTP 客户端
- `curl_cffi.AsyncWebClient`:浏览器指纹伪装

**特性**:
- 连接池管理
- 请求限流
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

**信号机制** ([mdcx/signals.py](mdcx/signals.py)):
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