# MDCx

![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Crawlers](https://img.shields.io/badge/Crawlers-42-brightgreen.svg)
![Architecture](https://img.shields.io/badge/Architecture-Async%20%2F%20Modular-blue.svg)

<p align="right">
  <img src="resources/Img/donate-qr.jpg" width="180" alt="赞赏码"><br>
  <sub>如果你觉得不错可否赏我杯奶茶费</sub>
</p>

## 简介

MDCx 从网站抓取视频文件对应的元数据（标题、演员、封面、简介等），生成标准 .nfo 文件和规范命名的文件夹，供 Emby、Jellyfin、Kodi 等媒体服务器直接使用。支持 Windows、macOS、Linux。

## 新手入口

### 普通用户

1. 从 [GitHub Releases](https://github.com/cdlongbow/mdcx/releases) 下载对应系统的版本
2. 设置媒体文件夹、下载选项和刮削网站
3. 先拿 1-3 个文件测试，确认效果后再批量处理

### 遇到问题先看这里

- 运行日志：程序自动在日志目录生成
- 配置文档：`docs/README.md`
- 常见问题：`docs/FAQ.md`

### 开发者

```bash
uv sync --dev
uv run python main.py
```

### 推送前自检

```bash
uv run check
```

首次运行会自动配置 Git hooks（`.githooks/`）。之后每次 `git push` 都会先自动运行自检。

**新工作区首次使用**：运行 `python3 scripts/install_git_hooks.py` 或直接 `uv run check`。

`uv run check` 依次执行：

- `ruff format --check`
- `ruff check`
- `python -m pytest tests/`

### 核心特色

- **42 个网站爬虫** - 有码、无码、FC2、国产、欧美
- **智能番号识别** - 自动判断番号类型并分类处理
- **标准 NFO 生成** - 符合 KODI/Emby/Jellyfin 规范
- **图片处理** - 人脸裁剪、水印、高清封面、图片修复
- **多语言翻译** - 5 个翻译引擎（Google、Baidu、DeepL、DeepLX、LLM）
- **演员数据库管理** - Excel 数据库，TMDB 批量查询
- **Emby/Jellyfin 深度集成** - 自动同步演员信息和图片
- **异步并发架构** - asyncio + 渐进式任务调度
- **灵活配置系统** - 字段优先级、Jinja2 命名模板
- **丰富的工具集** - 字幕管理、缺失检测、海报裁剪等

### 技术亮点

- **模块化设计** - 爬虫、核心、基础、工具层清晰分离
- **浏览器指纹伪装** - curl-cffi 模拟真实浏览器
- **令牌桶限流器** - 精准控制 API 请求频率
- **字段级优先级** - 每个字段可独立设置来源网站
- **渐进式任务调度** - 处理大量文件时不会内存溢出

## 核心特性

### 智能抓取系统

**42 个网站覆盖各类内容**

| 类型 | 网站 |
|-----|------|
| **有码** | DMM、JavDB、JavBus、Jav321、MGStage、Prestige、Official、JavLibrary、MissAV、AVSOX、MMTV、MyWife、Getchu、GetchuDMM、Faleno、Fantastica、Dahlia、Giga、XCity、CableAV、FreeJavBT、Hscangku、AVBASE、Mdtv |
| **无码** | Kin8、JavDB（无码分类）、airav_cc |
| **FC2** | FC2、FC2Club、FC2Hub、FC2PPVDB |
| **国产** | HDOUBAN、CNMDB、MADOUQU、Lulubar、IQQTV、JavDay |
| **欧美** | THEPORNDB |

**智能番号识别**
- 国产番号（MD/MKY 系列）自动标记
- 素人番号（SIRO 系列、短番号）识别
- FC2 番号自动分类
- 欧美番号（XXX.00.00.00 格式）识别
- 无码番号通过格式自动识别

**统一爬虫框架**
- 基类 `GenericBaseCrawler` 定义标准流程
- 上下文管理，避免状态混乱
- 支持自定义 URL 和 UI 隐藏
- 多网站结果智能合并

### 完整的 NFO 生成

**30+ 元数据字段**
- 基本信息：番号、标题、排序标题、剧情简介
- 发行信息：发行日期、年份、分级、国家代码
- 人员信息：演员（多语言）、导演
- 评分信息：公众评分、影评人评分、想看人数
- 分类标签：标签、类型、系列
- 制作信息：制作商、厂牌、发行商
- 媒体资源：海报、缩略图、背景图、预告片 URL
- 外部 ID：javdbid、javlibid 等各网站 ID

### 图片处理

**智能图片处理**
- 多类型图片下载（海报、缩略图、背景图、预告片）
- 人脸检测和智能裁剪（OpenCV）
- 2:3 比例标准海报
- 自定义水印
- 图片修复

**Amazon 高清封面**
- ASIN 条码识别
- Amazon 产品智能搜索（条码快路径、标题搜索、演员兜底三层策略）
- SL1500 尺寸高清封面
- ASIN 数据库缓存（Excel 保存，避免重复搜索）
- 详细文档：[Amazon 缓存系统详解](docs/amazon-cache.md)

### 多语言翻译系统

**5 个翻译引擎**
- Google 翻译
- 百度翻译
- DeepL 翻译
- DeepLX 翻译
- LLM 翻译（支持自定义 API）

**翻译功能**
- 字段级翻译配置
- 多语言支持（简体中文、繁体中文、日语）
- 映射表机制
- 演员真实姓名获取（Av-wiki）
- 降级策略和自动重试

### 灵活的命名系统

**Jinja2 模板引擎**
- 强大的模板语法
- 丰富的变量支持（番号、标题、演员、标签、系列等）
- 智能字符清理
- 三种命名目标（文件夹、文件、媒体库）

**文件处理**
- 批量重命名
- 软链接和硬链接支持
- 字幕自动匹配和管理
- 旧文件和空文件夹清理

### 演员数据库管理

**Excel 格式数据库**
- 字段：ID、日文名、中文名、繁体名、别名、信息链接、TMDB ID
- 信息链接：相关网站链接（LibreDMM、JavDB、TMDB 链接等）
- 导入导出
- 格式化和清理

**TMDB 集成**
- TMDB API 查询和批量获取（Excel 缓存避免重复查询）
- 多语言信息获取
- 令牌桶限流器（每秒 3.5 次请求，突发 10）
- 并发查询（并发数 3）
- 基于日文名、中文名、繁体名和别名的反向缓存搜索
- 名字变体归一化匹配
- 演员 TMDB ID 自动写入 NFO `actor/tmdbid`
- 详细文档：[TMDB 缓存系统详解](docs/tmdb-cache.md)

**数据补全来源**
- TMDB API：电影数据库信息
- Wikidata：维基百科数据
- Gfriends：演员头像和写真
- graphis.ne.jp：写真集信息

### Emby/Jellyfin 深度集成

**演员信息补全**
- 自动更新演员简介（Wikipedia）
- 更新演员元数据（出生日期、出生地等）
- 批量更新

**演员头像更新**
- 多来源获取（graphis.ne.jp、Gfriends、本地文件夹）
- 自动下载和上传
- 图片格式转换和优化

**其他集成**
- 创建 .actors 文件夹（Kodi/Plex/Jvedio 兼容）
- 生成标准 NFO 文件
- API 调用支持（Emby/Jellyfin 两种服务器）

### 异步并发处理

- asyncio 异步编程
- 渐进式任务调度，支持大量文件处理
- 可配置并发数
- 实时进度显示
- 令牌桶限流器，避免超过 API 限制
- 网站请求限流，避免触发反爬机制
- 间歇抓取模式

### 丰富的工具集

1. **字幕管理** - 自动匹配、复制、重命名
2. **缺失文件检测** - 检查媒体库缺失的文件
3. **海报裁剪工具** - 交互式裁剪海报
4. **演员数据库管理** - Excel 数据库维护
5. **Wiki 工具** - 从维基百科获取信息

### 网络和反爬机制

**HTTP 客户端**
- httpx.AsyncClient - 主要 HTTP 客户端
- curl_cffi.AsyncWebClient - 浏览器指纹伪装
- SOCKS 代理支持
- 连接池管理

**代理配置**
- HTTP/HTTPS 代理
- SOCKS5 代理
- 走代理网站功能（仅指定网站走代理，其余直连，支持网站名如 `javdb` 和完整域名如 `amazon.co.jp`）

**反爬措施**
- 浏览器指纹伪装
- 自定义请求头
- 失败自动重试
- 超时处理

## 文档

- [文档中心](docs/README.md) - 所有文档入口
- [Code Wiki](docs/CODE_WIKI.md) - 完整技术文档
- [功能特色](docs/FEATURES.md)
- [完整功能列表](docs/COMPLETE_FEATURES.md) - 42 个网站爬虫和全部功能
- [使用场景](docs/SCENARIOS.md)
- [开发指南](docs/DEVELOPMENT.md)
- [FAQ](docs/FAQ.md)
- [配置说明](docs/configuration.md)
- [用户使用手册](docs/USER_GUIDE.md)
- [刮削模式详解](docs/SCRAPING_MODES.md)
- [架构设计](docs/architecture.md)
- [API 文档](docs/api-documentation.md)
- [贡献指南](docs/CONTRIBUTING.md)
- [安装指南](docs/INSTALL.md)
- [Amazon 缓存系统](docs/amazon-cache.md)
- [TMDB 缓存系统](docs/tmdb-cache.md)
- [PyQt6 迁移](docs/pyqt6-migration.md)
- [爬虫迁移](docs/crawler-migration.md)
- [代码审查检查清单](docs/CODE_REVIEW_CHECKLIST.md)
- [代码审查指南](docs/CODE_REVIEW_GUIDE.md)
- [代码审查标准](docs/CODE_REVIEW_STANDARDS.md)
- [测试覆盖率摘要](docs/TEST_COVERAGE_SUMMARY.md)
- [变更日志](docs/changelog.md)

## 快速开始

### 安装

#### 方法一：从 Release 下载（推荐）

去 [Release](https://github.com/cdlongbow/mdcx/releases/latest) 页面下载对应系统版本，解压后直接运行。

#### 方法二：从源码运行

```bash
git clone https://github.com/cdlongbow/mdcx.git
cd mdcx

# 安装依赖（推荐使用 uv）
uv sync --locked --all-extras --dev

# 或使用 pip
pip install -e .

# 运行应用
uv run python main.py
```

### 使用示例

#### 基本使用流程

1. **配置媒体路径** - "设置" → "通用"，设置媒体路径和成功输出目录
2. **配置抓取来源** - "设置" → "刮削"，为不同类型视频选择网站
3. **配置下载选项** - "设置" → "下载"，选择需下载的文件类型和图片质量
4. **开始抓取** - 点击扫描 → 选择文件 → 点击开始

#### 翻译配置

1. 进入"设置" → "翻译"
2. 选择翻译服务（Google、百度、DeepL、DeepLX、LLM）
3. 配置 API 密钥（如果需要）
4. 选择需要翻译的字段

#### 命令行使用

```bash
# 命令行抓取
uv run python -m mdcx.cmd.crawl

# 生成枚举
uv run python -m mdcx.cmd.gen_enums
```

### 配置文件

配置文件默认路径：

- Windows: `%APPDATA%\MDCx\`
- macOS: `~/Library/Application Support/MDCx/`
- Linux: `~/.config/MDCx/`

### 系统要求

- Python 3.13+
- Windows 10+ / macOS 10.15+ / Linux
- 网络连接

### 故障排除

#### 网络问题

在"设置" → "网络"中配置代理。参考错误提示排查。

#### NFO 不显示

- 确保已勾选"下载 NFO"
- 检查 NFO 配置
- 确认媒体服务器已刷新媒体库

#### 翻译失败

- 检查翻译服务配置
- 确认 API 密钥有效
- 查看日志了解详细错误

## 交流群

[![Telegram](https://img.shields.io/badge/Telegram-Join_Chat-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://t.me/mdcx_chat)

> [!TIP]
> **使用问题**：配置、使用心得等，建议加入 Telegram 交流群。
> **Bug 反馈**：确认不是已知问题后提交 Issue，附上相关日志和番号。

## 上游项目

* [yoshiko2/Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture): 命令行工具，已不活跃，新版已闭源。
* [moyy996/AVDC](https://github.com/moyy996/AVDC): 上述项目的 PyQt GUI 分支，已停止维护。
* @Hermit/MDCx: AVDC 的分支，曾在 [anyabc/something](https://github.com/anyabc/something/releases) 分发源码和可执行文件。
* 2023-11-3 @anyabc 因未知原因销号删库，最后一个版本号 20231014。
* [@sqzw-x/mdcx](https://github.com/sqzw-x/mdcx) 暂时停止维护。
* 本项目基于 [@sqzw-x/mdcx](https://github.com/sqzw-x/mdcx) 继续维护和优化。

感谢相关开发者。

## 开发指南

### 项目结构

```
mdcx/
├── base/              # 基础功能模块
├── cmd/               # 命令行工具
├── config/            # 配置管理
├── controllers/       # 控制器（业务逻辑）
├── core/              # 核心功能（抓取、NFO 等）
├── crawlers/          # 爬虫实现
├── gen/               # 自动生成的枚举
├── models/            # 数据模型
├── tools/             # 工具模块
├── utils/             # 工具函数
└── views/             # UI 视图
```

### 构建

一般情况不要自己构建，去 [Release](https://github.com/cdlongbow/mdcx/releases) 下载最新版即可。

### 测试

```bash
# 运行所有测试
uv run pytest tests/

# 运行测试并生成覆盖率报告
uv run pytest tests/ --cov=mdcx --cov-report=html
```

### 代码规范

项目用 `ruff` 做代码检查：

```bash
# 代码检查
uv run ruff check .

# 自动修复
uv run ruff check . --fix
```

### 贡献指南

请看 [CONTRIBUTING.md](docs/CONTRIBUTING.md)。

## 授权许可

本项目在 GPLv3 许可下发布。使用本项目代表你接受以下条款：

* 本项目仅供学习和技术交流使用
* 请勿在公共社交平台上宣传此项目
* 使用本软件时请遵守当地法律法规
* 法律及使用后果由使用者自己承担
* 禁止将本软件用于商业用途
