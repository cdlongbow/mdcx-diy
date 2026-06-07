# MDCx

![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Crawlers](https://img.shields.io/badge/Crawlers-40%2B-brightgreen.svg)
![Architecture](https://img.shields.io/badge/Architecture-Async%20%2F%20Modular-blue.svg)

## ✨ 简介

MDCx（Movie Data Capture X）是一款**功能强大、设计精良**的视频元数据刮削和管理工具，专为影视收藏爱好者和媒体服务器用户打造。项目基于 Python 3.13+ 开发，使用 PyQt6 构建现代化图形界面，支持跨平台运行（Windows、macOS、Linux）。

### 核心特色

- 🌐 **40+ 网站刮削支持** - 覆盖有码、无码、FC2、国产、欧美等各类内容
- 🎬 **智能番号识别** - 自动识别番号类型，智能分类处理
- 📄 **标准 NFO 生成** - 完全符合 KODI/Emby/Jellyfin 规范
- 🖼️ **强大图片处理** - 人脸裁剪、水印添加、高清封面获取
- 🌍 **多语言翻译** - 支持 Google/百度/DeepL/LLM 等多种翻译引擎
- 🎭 **演员数据库管理** - Excel 格式数据库，TMDB 批量查询
- 🖥️ **Emby/Jellyfin 深度集成** - 自动同步演员信息和图片
- ⚡ **异步并发架构** - 高效的异步 I/O 和并发处理
- 🔧 **灵活配置系统** - 字段级优先级、命名模板等高级配置
- 🛠️ **丰富的工具集** - 字幕管理、缺失检测、海报裁剪等实用工具

### 技术亮点

- 📦 **高度模块化设计** - 爬虫、核心、基础、工具层清晰分离
- 🎭 **浏览器指纹伪装** - curl-cffi 反爬机制，有效规避检测
- 🔒 **令牌桶限流器** - TMDB API 精确限流（3.5 req/s），避免触发限流
- 🎯 **字段级优先级** - 每个字段可独立配置网站优先级
- 📝 **Jinja2 命名模板** - 强大的模板引擎，灵活的命名规则
- 🔄 **渐进式任务调度** - 支持大量文件处理，避免内存溢出

## 🎯 使用场景

MDCx 专为以下用户和场景打造：

### 🎬 影视收藏爱好者
- 拥有大量视频文件，需要批量整理媒体库
- 希望自动获取元数据、封面图和背景图
- 需要统一的命名规则和文件组织结构
- 想要建立完整的多语言影视资料库

### 🖥️ 媒体服务器用户
- 使用 Emby、Jellyfin 或 Kodi 搭建家庭媒体中心
- 需要标准 NFO 文件以完美适配媒体服务器
- 要求完整的演员信息和高清封面
- 希望自动同步演员信息和图片

### 🌍 多语言环境用户
- 需要中文或日文元数据
- 使用不同语言界面
- 需要翻译功能或映射表机制
- 要求演员的真实日文名

### 📚 数据库维护者
- 维护 Excel 格式的演员数据库
- 需要从 TMDB 批量查询演员信息
- 管理多语言演员信息（中文、日文、别名）
- 同步演员数据到媒体服务器

### 🔧 高级用户
- 需要自定义字段优先级和网站配置
- 使用 Jinja2 模板定义命名规则
- 需要批量处理和自动化工作流
- 要求高度可定制的刮削策略

### 核心特性

#### 🤖 智能刮削系统

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
- 🇨🇳 国产番号（MD/MKY 系列）自动标记
- 👤 素人番号（SIRO 系列、短番号）识别
- 🎥 FC2 番号自动分类
- 🌍 欧美番号（XXX.00.00.00 格式）识别
- 🔞 无码番号通过格式自动识别

**统一爬虫框架**
- 基类 `GenericBaseCrawler` 定义标准流程
- 上下文管理机制，避免状态污染
- 支持自定义 URL 和 UI 隐藏
- 多网站结果智能整合

#### 📄 完整的 NFO 生成

**30+ 元数据字段，完全符合标准**
- 基本信息：番号、标题、排序标题、剧情简介
- 发行信息：发行日期、年份、分级、国家代码
- 人员信息：演员（多语言）、导演
- 评分信息：公众评分、影评人评分、想看人数
- 分类标签：标签、类型、系列
- 制作信息：制作商、厂牌、发行商
- 媒体资源：海报、缩略图、背景图、预告片 URL
- 外部 ID：javdbid、javlibid 等各网站 ID

#### 🖼️ 强大的图片处理

**智能图片处理能力**
- 🖼️ 多类型图片下载（海报、缩略图、背景图、预告片）
- 👤 人脸检测和智能裁剪（OpenCV）
- 📐 2:3 比例标准海报
- ✏️ 自定义水印添加
- 🔧 图片修复功能

**Amazon 高清封面**
- 📸 ASIN 条码识别
- 🎯 Amazon 产品智能搜索
- 📷 SL1500 尺寸高清封面获取
- 💾 ASIN 数据库缓存

#### 🌐 多语言翻译系统

**4 大翻译引擎**
1. Google 翻译
2. 百度翻译
3. DeepL 翻译
4. LLM 翻译（支持自定义 API）

**翻译特性**
- 📝 字段级翻译配置
- 🌐 多语言支持（中文简繁、日语）
- 📋 映射表机制
- 👤 演员真实姓名获取（Av-wiki）
- 🔄 降级策略和自动重试

#### 📁 灵活的命名系统

**Jinja2 模板引擎**
- 📝 强大的模板语法
- 🔄 丰富的变量支持（番号、标题、演员、标签、系列等）
- 🧹 智能字符清理
- 📐 三种命名目标（文件夹、文件、媒体库）

**文件处理**
- 📁 批量重命名
- 🔗 软链接和硬链接支持
- 📄 字幕自动匹配和管理
- 🗑️ 旧文件和空文件夹清理

#### 🎭 演员数据库管理

**Excel 格式数据库**
- 字段：ID、日文名、中文名、繁体名、别名、信息链接、TMDB ID
- 信息链接：相关网站链接（LibreDMM、JavDB、TMDB 链接等）
- 导入导出支持
- 信息链接管理
- 格式化和清理

**TMDB 集成**
- 🎬 TMDB API 查询和批量获取
- 🌐 多语言信息获取
- 🔒 令牌桶限流器（3.5 req/s）
- 🚀 并发查询（并发数 3）
- 🔄 反向搜索功能

**数据补全来源**
- TMDB API：电影数据库信息
- Wikidata：维基百科数据
- Gfriends：演员头像和写真
- graphis.ne.jp：写真集信息

#### 🖥️ Emby/Jellyfin 深度集成

**演员信息补全**
- 📝 自动更新演员简介（Wikipedia）
- 📅 更新演员元数据（出生日期、出生地等）
- 🔄 批量更新支持

**演员头像更新**
- 📸 多来源获取（graphis.ne.jp、Gfriends、本地文件夹）
- 🚀 自动下载和上传
- 🖼️ 图片格式转换和优化

**其他集成**
- 📁 创建 .actors 文件夹（Kodi/Plex/Jvedio 兼容）
- 📄 生成标准 NFO 文件
- ⚙️ API 调用支持（Emby/Jellyfin 两种服务器）
- 🛡️ 完善的错误处理和容错机制

#### ⚡ 异步并发处理

**高性能架构**
- ⚡ asyncio 异步编程，充分利用 I/O
- 📊 渐进式任务调度，支持大量文件处理
- ⚙️ 可配置并发数，用户自定义调整
- 📈 实时进度显示和性能监控

**智能限流**
- 🔒 令牌桶限流器，避免 API 超限
- 🌐 网站请求限流，避免触发反爬
- ⏳ 间歇刮削模式支持

#### 🛠️ 丰富的工具集

**内置实用工具**
1. **字幕管理** - 自动匹配、复制、重命名
2. **缺失文件检测** - 检测媒体库缺失文件
3. **海报裁剪工具** - 交互式海报裁剪界面
4. **演员数据库管理** - Excel 数据库维护
5. **Wiki 工具** - 从维基百科获取信息

#### 🌐 网络和反爬机制

**HTTP 客户端**
- 🌐 httpx.AsyncClient - 主要 HTTP 客户端
- 🎭 curl_cffi.AsyncWebClient - 浏览器指纹伪装
- 🔗 SOCKS 代理支持
- 🔄 连接池管理

**反爬措施**
- 🎭 浏览器指纹伪装
- 📋 请求头自定义
- 🔄 失败自动重试
- ⏱️ 超时处理

### 支持的网站列表

| 类别 | 网站 |
|-----|------|
| 有码 | DMM, MGStage, Prestige, Official, JavBus, Jav321, JavDB, JavDBAPI, MissAV, AVSOX, MMTV, Mywife, etc. |
| 无码 | Kin8, Love6, etc. |
| FC2 | FC2, FC2Club, FC2Hub, FC2PPVDB |
| 国产 | HDOUBAN, CNMDB, GUOCHAN, MADOUQU |
| 欧美 | THEPORNDB |
| 其他 | Getchu, Giga, etc. |

## 📚 文档

### 快速链接

- 📖 [文档中心](docs/README.md) - 所有文档的入口
- 📗 [Code Wiki](CODE_WIKI.md) - 完整的技术文档
- ⭐ [功能特色](FEATURES.md) - 详细的功能介绍和特色说明
- 📋 [完整功能列表](COMPLETE_FEATURES.md) - 所有功能的完整列表和详细说明
- 🎬 [使用场景](SCENARIOS.md) - 8 个详细的使用场景和案例
- 🔧 [开发指南](DEVELOPMENT.md) - 开发者文档
- ❓ [FAQ](FAQ.md) - 常见问题解答

### 详细文档

#### 用户文档

- 📗 [用户使用手册](USER_GUIDE.md) - 完整的用户指南，包含安装、配置和使用说明
- ⭐ [功能特色](FEATURES.md) - 详细的功能介绍、技术亮点和使用场景
- 📋 [完整功能列表](COMPLETE_FEATURES.md) - 所有 42 个网站爬虫和功能的完整列表
- 🎬 [使用场景和案例](SCENARIOS.md) - 8 个实际使用场景的详细操作指南
- 📋 [配置说明](docs/configuration.md) - 详细的配置项说明
- 📦 [安装指南](INSTALL.md) - 安装步骤和系统要求
- ❓ [FAQ](FAQ.md) - 常见问题解答

#### 开发者文档

- 🔧 [开发指南](DEVELOPMENT.md) - 开发环境搭建、代码规范和最佳实践
- 🏗️ [架构设计](docs/architecture.md) - 系统架构和设计模式
- 📖 [API 文档](docs/api-documentation.md) - 核心模块 API 参考
- 🤝 [贡献指南](CONTRIBUTING.md) - 如何为项目做贡献
- 📚 [Code Wiki](CODE_WIKI.md) - 技术文档和代码说明

#### 迁移指南

- 🔄 [PyQt6 迁移](docs/pyqt6-migration.md) - 从 PyQt5 迁移到 PyQt6 的方案
- 🔄 [爬虫迁移](docs/crawler-migration.md) - 刮削器新版框架迁移指南

#### 代码质量

- ✅ [代码审查检查清单](docs/CODE_REVIEW_CHECKLIST.md) - 代码审查检查项
- 📖 [代码审查指南](docs/CODE_REVIEW_GUIDE.md) - 代码审查流程和规范
- 📋 [代码审查标准](docs/CODE_REVIEW_STANDARDS.md) - 代码质量标准
- 🧪 [测试覆盖率摘要](docs/TEST_COVERAGE_SUMMARY.md) - 测试覆盖率

#### 项目信息

- 📝 [变更日志](changelog.md) - 版本更新历史
- 📜 [许可证](LICENSE) - GPLv3 许可证

## 快速开始

### 安装

#### 方法一：从 Release 下载（推荐）

预编译版本可在 [Release](https://github.com/cdlongbow/mdcx/releases/latest) 页面下载，解压后直接运行即可。

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
   - 设置"媒体路径"为您存放视频文件的目录
   - 设置"成功输出目录"（可选）

2. **配置刮削源**
   - 进入"设置" → "刮削"
   - 选择您想要使用的刮削网站
   - 可配置不同类型（有码/无码/FC2等）使用不同的网站

3. **配置下载选项**
   - 进入"设置" → "下载"
   - 选择需要下载的文件类型（海报/缩略图/背景图/NFO等）
   - 配置图片质量和尺寸

4. **开始刮削**
   - 返回主界面
   - 点击"扫描"按钮扫描媒体目录
   - 选择要刮削的文件
   - 点击"开始"按钮开始刮削

#### 翻译配置

1. 进入"设置" → "翻译"
2. 选择翻译服务（Google/Baidu/DeepL/LLM）
3. 配置相应的 API 密钥（如需要）
4. 选择需要翻译的字段

#### 命令行使用

MDCx 也提供命令行工具：

```bash
# 命令行刮削
uv run python -m mdcx.cmd.crawl

# 生成枚举
uv run python -m mdcx.cmd.gen_enums
```

### 配置文件

配置文件默认存储在用户目录下：

- Windows: `%APPDATA%\MDCx\`
- macOS: `~/Library/Application Support/MDCx/`
- Linux: `~/.config/MDCx/`

### 系统要求

- Python 3.13+
- Windows 10+ / macOS 10.15+ / Linux
- 网络连接（用于刮削数据）

### 故障排除

#### 网络问题

- 如遇到网络连接问题，可在"设置" → "网络"中配置代理
- 参考错误提示中的详细说明进行排查

#### NFO 不显示

- 确保已勾选"下载 NFO"选项
- 检查 NFO 配置是否正确
- 确认媒体服务器已刷新媒体库

#### 翻译失败

- 检查翻译服务配置
- 确认 API 密钥有效
- 查看日志了解详细错误信息

## 交流群

[![Telegram](https://img.shields.io/badge/Telegram-Join_Chat-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://t.me/mdcx_chat)

> [!TIP]
> **使用问题**：有关软件配置、使用心得等非技术性问题，建议优先加入 **Telegram 交流群**与群友交流。  
> **Bug 反馈**：如遇程序异常或功能缺陷，请先确认是否为已知问题，再提交 **Issue** 并附上相关日志、问题番号等内容。

## 上游项目

* [yoshiko2/Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture): CLI 工具,
  开源版本现已不活跃, 新版本已闭源商业化.
* [moyy996/AVDC](https://github.com/moyy996/AVDC): 上述项目早期的一个 Fork, 使用 PyQt 实现了图形界面, 已停止维护
* @Hermit/MDCx: AVDC 的 Fork, 一度在 [anyabc/something](https://github.com/anyabc/something/releases) 分发源代码及可执行文件.
* 2023-11-3 @anyabc 因未知原因销号删库, 其分发的最后一个版本号为 20231014.
* [@sqzw-x/mdcx](https://github.com/sqzw-x/mdcx)当前暂时停止维护.
* 本项目基于 [@sqzw-x/mdcx](https://github.com/sqzw-x/mdcx), 继续进行维护及优化.

向相关开发者表示敬意.

## 开发指南

### 项目结构

```
mdcx/
├── base/              # 基础功能模块
├── cmd/               # 命令行工具
├── config/            # 配置管理
├── controllers/       # 控制器（业务逻辑）
├── core/              # 核心功能（刮削、NFO等）
├── crawlers/          # 爬虫实现
├── gen/               # 自动生成的枚举
├── models/            # 数据模型
├── tools/             # 工具模块
├── utils/             # 工具函数
└── views/             # UI 视图
```

### 构建

> 一般情况请勿自行构建，至 [Release](https://github.com/cdlongbow/mdcx/releases) 下载最新版

### 测试

运行测试：

```bash
# 运行所有测试
uv run pytest tests/

# 运行测试并生成覆盖率报告
uv run pytest tests/ --cov=mdcx --cov-report=html
```

### 代码规范

项目使用 `ruff` 进行代码检查：

```bash
# 代码检查
uv run ruff check .

# 自动修复
uv run ruff check . --fix
```

### 贡献指南

欢迎贡献代码！请参考 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献流程。

## 授权许可

本插件项目在 GPLv3 许可授权下发行。此外，如果使用本项目表明还额外接受以下条款：

* 本项目仅供学习以及技术交流使用
* 请勿在公共社交平台上宣传此项目
* 使用本软件时请遵守当地法律法规
* 法律及使用后果由使用者自己承担
* 禁止将本软件用于任何的商业用途