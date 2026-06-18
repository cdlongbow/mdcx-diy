# MDCx

![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Crawlers](https://img.shields.io/badge/Crawlers-40%2B-brightgreen.svg)
![Architecture](https://img.shields.io/badge/Architecture-Async%20%2F%20Modular-blue.svg)

## 简介

MDCx（Movie Data Capture X）是一个帮你自动整理视频文件的工具——它从网站抓取影片信息（标题、演员、封面、简介等），然后生成标准的 .nfo 数据文件和命名好的文件夹，方便你在 Emby、Jellyfin、Kodi 这类媒体服务器里直接使用。支持 Windows、macOS、Linux 三个系统。

## 新手入口

### 普通用户

1. 去 GitHub Releases 页面下载你系统对应的版本
2. 第一次打开后，先设置好媒体文件夹、下载选项和想用的网站
3. 先拿 1 到 3 个文件试试，确认效果符合预期，再批量处理

### 遇到问题先看哪里

- 运行日志：程序会自动在日志目录生成日志文件
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

首次运行时会自动配置 Git hooks。之后每次执行 `git push`，都会先自动运行自检，通过后再继续推送。

**新工作区首次使用**

Clone 仓库后，运行一次：

```bash
python3 scripts/install_git_hooks.py
```

或者直接使用 `uv run check` 也会自动配置。

这条命令会依次执行：

- `ruff format --check`
- `ruff check`
- `python -m pytest tests/test_tmdb_actor.py tests/test_mapping_resources.py`

### 核心特色

- **40+ 网站抓取** - 支持有码、无码、FC2、国产、欧美等各种类型
- **智能番号识别** - 自动判断番号类型，分类处理
- **标准 NFO 生成** - 完全符合 KODI/Emby/Jellyfin 规范
- **强大图片处理** - 人脸裁剪、水印、高清封面
- **多语言翻译** - 支持 Google、百度、DeepL、大模型等多种翻译引擎
- **演员数据库管理** - Excel 数据库，TMDB 批量查询
- **Emby/Jellyfin 深度集成** - 自动同步演员信息和图片
- **异步并发架构** - 同时处理多个任务，速度快
- **灵活配置系统** - 字段优先级、命名模板等高级配置
- **丰富的工具集** - 字幕管理、缺失检测、海报裁剪等实用工具

### 技术亮点

- **高度模块化设计** - 爬虫、核心、基础、工具层清晰分开
- **浏览器指纹伪装** - 用 curl-cffi 模拟真实浏览器，降低被网站屏蔽的概率
- **令牌桶限流器** - TMDB API 精确限流（每秒 3.5 次请求），避免被封
- **字段级优先级** - 每个字段可以单独设置从哪个网站优先获取
- **Jinja2 命名模板** - 用模板语法灵活定义文件命名规则
- **渐进式任务调度** - 处理大量文件时不会内存溢出

## 使用场景

### 影视收藏爱好者
- 有大量视频文件需要批量整理
- 希望自动获取元数据、海报和背景图
- 需要统一的命名规则和文件结构
- 想建立完整的多语言影视资料库

### 媒体服务器用户
- 用 Emby、Jellyfin 或 Kodi 搭建家庭影院
- 需要标准 NFO 文件让媒体服务器正常识别
- 要求完整的演员信息和高清封面
- 希望自动同步演员信息和图片

### 多语言环境用户
- 需要中文或日文元数据
- 使用不同语言界面
- 需要翻译功能或映射表
- 要求演员的真实日文名

### 数据库维护者
- 维护 Excel 格式的演员数据库
- 需要从 TMDB 批量查询演员信息
- 管理多语言演员信息（中文、日文、别名）
- 同步演员数据到媒体服务器

### 高级用户
- 自定义字段优先级和网站配置
- 用 Jinja2 模板定义命名规则
- 批量处理和自动化工作流
- 高度可定制的抓取策略

### 核心特性

#### 智能抓取系统

**40+ 网站支持，覆盖各类内容**

| 类型 | 支持网站 |
|-----|---------|
| **有码** | DMM、MGStage、Prestige、Official、JavBus、Jav321、JavDB、JavDBAPI、MissAV、AVSOX、MMTV、MyWife、Getchu 等 |
| **无码** | Kin8、Love6 等 |
| **FC2** | FC2、FC2Club、FC2Hub、FC2PPVDB |
| **国产** | HDOUBAN、CNMDB、GUOCHAN、MADOUQU |
| **欧美** | THEPORNDB |
| **其他** | Giga、Faleno、Fantastica、Dahlia、XCity 等 |

**智能番号识别和分类**
- 国产番号（MD/MKY 系列）自动标记
- 素人番号（SIRO 系列、短番号）识别
- FC2 番号自动分类
- 欧美番号（XXX.00.00.00 格式）识别
- 无码番号通过格式自动识别

**统一爬虫框架**
- 基类 `GenericBaseCrawler` 定义标准流程
- 上下文管理，避免状态混乱
- 支持自定义 URL 和 UI 隐藏
- 多个网站的结果智能合并

#### 完整的 NFO 生成

**30+ 元数据字段，完全符合标准**
- 基本信息：番号、标题、排序标题、剧情简介
- 发行信息：发行日期、年份、分级、国家代码
- 人员信息：演员（多语言）、导演
- 评分信息：公众评分、影评人评分、想看人数
- 分类标签：标签、类型、系列
- 制作信息：制作商、厂牌、发行商
- 媒体资源：海报、缩略图、背景图、预告片 URL
- 外部 ID：javdbid、javlibid 等各网站 ID

#### 强大的图片处理

**智能图片处理**
- 多类型图片下载（海报、缩略图、背景图、预告片）
- 人脸检测和智能裁剪（OpenCV）
- 2:3 比例标准海报
- 自定义水印
- 图片修复功能

**Amazon 高清封面**
- ASIN 条码识别
- Amazon 产品智能搜索（三层策略：条码快路径、标题搜索、演员兜底）
- SL1500 尺寸高清封面获取
- ASIN 数据库缓存（Excel 保存，避免重复搜索）
- 详细文档：[Amazon 缓存系统详解](docs/amazon-cache.md)

#### 多语言翻译系统

**4 个翻译引擎**
1. Google 翻译
2. 百度翻译
3. DeepL 翻译
4. LLM 翻译（支持自定义 API）

**翻译功能**
- 字段级翻译配置
- 多语言支持（简体中文、繁体中文、日语）
- 映射表机制
- 演员真实姓名获取（Av-wiki）
- 降级策略和自动重试

#### 灵活的命名系统

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

#### 演员数据库管理

**Excel 格式数据库**
- 字段：ID、日文名、中文名、繁体名、别名、信息链接、TMDB ID
- 信息链接：相关网站链接（LibreDMM、JavDB、TMDB 链接等）
- 导入导出
- 信息链接管理
- 格式化和清理

**TMDB 集成**
- TMDB API 查询和批量获取（Excel 缓存，避免重复查询）
- 多语言信息获取
- 令牌桶限流器（每秒 3.5 次请求，突发 10）
- 并发查询（并发数 3）
- 基于日文名、中文名、繁体名和别名的反向缓存搜索
- 名字变体归一化匹配
- 演员 TMDB ID 自动写入 NFO 的 `actor/tmdbid`
- 详细文档：[TMDB 缓存系统详解](docs/tmdb-cache.md)

**数据补全来源**
- TMDB API：电影数据库信息
- Wikidata：维基百科数据
- Gfriends：演员头像和写真
- graphis.ne.jp：写真集信息

#### Emby/Jellyfin 深度集成

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
- 完善的错误处理

#### 异步并发处理

**高性能架构**
- asyncio 异步编程，充分利用 I/O
- 渐进式任务调度，支持大量文件处理
- 可配置并发数，用户自定义调整
- 实时进度显示

**智能限流**
- 令牌桶限流器，避免超过 API 限制
- 网站请求限流，避免触发反爬机制
- 间歇抓取模式

#### 丰富的工具集

**内置工具**
1. **字幕管理** - 自动匹配、复制、重命名
2. **缺失文件检测** - 检查媒体库里缺了哪些文件
3. **海报裁剪工具** - 交互式裁剪海报
4. **演员数据库管理** - Excel 数据库维护
5. **Wiki 工具** - 从维基百科获取信息

#### 网络和反爬机制

**HTTP 客户端**
- httpx.AsyncClient - 主要 HTTP 客户端
- curl_cffi.AsyncWebClient - 浏览器指纹伪装
- SOCKS 代理支持
- 连接池管理

**代理配置**
- HTTP/HTTPS 代理
- SOCKS5 代理
- 不走代理网站功能（指定某些网站直连）
- 灵活的代理策略

**不走代理网站功能**
- 指定特定网站不用代理
- 支持网站值（如 `javdb`）和完整域名（如 `api.tmdb.org`）
- 多个网站用逗号隔开
- 适用于 API 服务、本地访问等场景

**反爬措施**
- 浏览器指纹伪装
- 自定义请求头
- 失败自动重试
- 超时处理

### 支持的网站列表

| 类别 | 网站 |
|-----|------|
| 有码 | DMM, MGStage, Prestige, Official, JavBus, Jav321, JavDB, JavDBAPI, MissAV, AVSOX, MMTV, Mywife, etc. |
| 无码 | Kin8, Love6, etc. |
| FC2 | FC2, FC2Club, FC2Hub, FC2PPVDB |
| 国产 | HDOUBAN, CNMDB, GUOCHAN, MADOUQU |
| 欧美 | THEPORNDB |
| 其他 | Getchu, Giga, etc. |

## 文档

### 快速链接

- [文档中心](docs/README.md) - 所有文档的入口
- [Code Wiki](docs/CODE_WIKI.md) - 完整技术文档
- [功能特色](docs/FEATURES.md) - 功能介绍和特色说明
- [完整功能列表](docs/COMPLETE_FEATURES.md) - 全部功能和详细说明
- [使用场景](docs/SCENARIOS.md) - 8 个使用场景和案例
- [开发指南](docs/DEVELOPMENT.md) - 开发者文档
- [FAQ](docs/FAQ.md) - 常见问题

### 详细文档

#### 用户文档

- [用户使用手册](docs/USER_GUIDE.md) - 完整的用户指南，包含安装、配置和使用
- [功能特色](docs/FEATURES.md) - 功能介绍、技术亮点和使用场景
- [完整功能列表](docs/COMPLETE_FEATURES.md) - 全部 42 个网站爬虫和功能
- [刮削模式详解](docs/SCRAPING_MODES.md) - 正常模式、更新模式、读取模式说明
- [使用场景和案例](docs/SCENARIOS.md) - 8 个实际场景的操作指南
- [配置说明](docs/configuration.md) - 详细配置项说明
- [安装指南](docs/INSTALL.md) - 安装步骤和系统要求
- [FAQ](docs/FAQ.md) - 常见问题

#### 开发者文档

- [开发指南](docs/DEVELOPMENT.md) - 开发环境搭建、代码规范
- [架构设计](docs/architecture.md) - 系统架构和设计
- [API 文档](docs/api-documentation.md) - 核心模块 API 参考
- [贡献指南](docs/CONTRIBUTING.md) - 如何贡献代码
- [Code Wiki](docs/CODE_WIKI.md) - 技术文档和代码说明

#### 迁移指南

- [PyQt6 迁移](docs/pyqt6-migration.md) - 从 PyQt5 迁移到 PyQt6
- [爬虫迁移](docs/crawler-migration.md) - 新版爬虫框架迁移

#### 代码质量

- [代码审查检查清单](docs/CODE_REVIEW_CHECKLIST.md) - 审查项
- [代码审查指南](docs/CODE_REVIEW_GUIDE.md) - 流程和规范
- [代码审查标准](docs/CODE_REVIEW_STANDARDS.md) - 质量标准
- [测试覆盖率摘要](docs/TEST_COVERAGE_SUMMARY.md) - 测试覆盖

#### 项目信息

- [变更日志](docs/changelog.md) - 版本更新历史
- [许可证](LICENSE) - GPLv3 许可证

## 快速开始

### 安装

#### 方法一：从 Release 下载（推荐）

去 [Release](https://github.com/cdlongbow/mdcx/releases/latest) 页面下载你系统的版本，解压后直接运行。

#### 方法二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/cdlongbow/mdcx.git
cd mdcx

# 安装依赖（使用 uv）
uv sync --locked --all-extras --dev

# 或使用 pip
pip install -e .

# 运行应用
uv run python main.py
# 或
python main.py
```

### 使用示例

#### 基本使用流程

1. **配置媒体路径**
   - 打开 MDCx
   - 进入"设置" → "通用"
   - 设置"媒体路径"为你的视频文件所在目录
   - 设置"成功输出目录"（可选）

2. **配置抓取来源**
   - 进入"设置" → "刮削"
   - 选择你想用的网站
   - 可以为不同类型（有码/无码/FC2等）设置不同的网站

3. **配置下载选项**
   - 进入"设置" → "下载"
   - 选择需要下载的文件类型（海报、缩略图、背景图、NFO 等）
   - 设置图片质量和尺寸

4. **开始抓取**
   - 返回主界面
   - 点"扫描"按钮扫描媒体目录
   - 选择要处理的文件
   - 点"开始"按钮开始

#### 翻译配置

1. 进入"设置" → "翻译"
2. 选择翻译服务（Google、百度、DeepL、LLM）
3. 配置 API 密钥（如果需要）
4. 选择需要翻译的字段

#### 命令行使用

MDCx 也提供了命令行工具：

```bash
# 命令行抓取
uv run python -m mdcx.cmd.crawl

# 生成枚举
uv run python -m mdcx.cmd.gen_enums
```

### 配置文件

配置文件默认存在用户目录下：

- Windows: `%APPDATA%\MDCx\`
- macOS: `~/Library/Application Support/MDCx/`
- Linux: `~/.config/MDCx/`

### 系统要求

- Python 3.13+
- Windows 10+ / macOS 10.15+ / Linux
- 需要网络连接（用于抓取数据）

### 故障排除

#### 网络问题

- 遇到网络连接问题，可在"设置" → "网络"中配置代理
- 参考错误提示中的详细说明排查

#### NFO 不显示

- 确保已勾选"下载 NFO"选项
- 检查 NFO 配置是否正确
- 确认媒体服务器已刷新媒体库

#### 翻译失败

- 检查翻译服务配置
- 确认 API 密钥有效
- 查看日志了解详细错误

本项目源自 Hazard804 大佬改良的 mdcx 项目，衷心感谢！以下是源项目说明。

## 交流群

[![Telegram](https://img.shields.io/badge/Telegram-Join_Chat-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://t.me/mdcx_chat)

> [!TIP]
> **使用问题**：软件配置、使用心得等非技术问题，建议加入 Telegram 交流群问群友。
> **Bug 反馈**：如果遇到程序异常，请先确认是不是已知问题，然后提交 Issue 并附上相关日志和番号。

## 上游项目

* [yoshiko2/Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture): 命令行工具，已不活跃，新版已闭源。
* [moyy996/AVDC](https://github.com/moyy996/AVDC): 上述项目的早期分支，用 PyQt 做了图形界面，已停止维护。
* @Hermit/MDCx: AVDC 的分支，曾在 [anyabc/something](https://github.com/anyabc/something/releases) 分发源码和可执行文件。
* 2023-11-3 @anyabc 因未知原因销号删库，最后一个版本号是 20231014。
* [@sqzw-x/mdcx](https://github.com/sqzw-x/mdcx) 暂时停止维护。
* 本项目基于 [@sqzw-x/mdcx](https://github.com/sqzw-x/mdcx)，继续维护和优化。

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

> 一般情况不要自己构建，去 [Release](https://github.com/cdlongbow/mdcx/releases) 下载最新版即可。

### 测试

运行测试：

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

欢迎贡献代码！请看 [CONTRIBUTING.md](docs/CONTRIBUTING.md) 了解详细流程。

## 授权许可

本项目在 GPLv3 许可下发布。使用本项目代表你还接受以下条款：

* 本项目仅供学习和技术交流使用
* 请勿在公共社交平台上宣传此项目
* 使用本软件时请遵守当地法律法规
* 法律及使用后果由使用者自己承担
* 禁止将本软件用于商业用途
