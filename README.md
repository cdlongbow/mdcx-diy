# MDCx

![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)

## 简介

MDCx（Movie Data Capture X）是一个现代化的视频元数据刮削和管理工具，支持从 34+ 个网站自动获取视频信息，生成符合 KODI/Emby/Jellyfin 规范的 NFO 文件，并提供完整的图片处理、翻译功能和媒体服务器集成。专为影视收藏爱好者和媒体服务器用户打造。

## 使用场景

MDCx 适用于以下场景：

- 🎬 **个人媒体库整理**：自动为您的视频文件添加元数据、封面图和背景图
- 🖥️ **Emby/Jellyfin/Kodi 集成**：生成标准 NFO 文件，完美适配主流媒体服务器
- 🌍 **多语言环境**：支持多种翻译服务，让元数据显示为您熟悉的语言
- 🎭 **批量处理**：高效的异步并发处理，快速整理大量视频文件

### 核心特性

- 🤖 **智能刮削**：支持 34+ 个数据源，自动识别番号和马赛克类型
  - 有码、无码、素人、FC2、欧美、国产等多种类型
  - 支持 JavBus、JavDB、DMM、MGStage、MissAV 等主流网站
  - 智能番号识别和类型分类

- 📄 **NFO 生成**：生成符合 KODI/Emby 规范的元数据文件
  - 完整的 XML 结构，包含所有必要字段
  - 支持多语言显示
  - 与主流媒体服务器完美兼容

- 🖼️ **图片处理**：自动下载、裁剪、添加水印
  - 支持海报、缩略图、背景图下载
  - 智能人脸裁剪
  - 自定义水印设置
  - 图片质量和尺寸优化

- 🌐 **多语言翻译**：支持 Google/百度/DeepL/LLM 翻译
  - 多种翻译服务可选
  - 字段级翻译配置
  - 支持中文简繁转换

- 📁 **灵活命名**：Jinja2 模板系统，支持自定义命名规则
  - 文件和文件夹命名模板
  - 丰富的变量支持
  - 智能字符清理

- 🔍 **Amazon 集成**：条码识别，自动匹配高清封面

- ⚡ **异步处理**：高效的并发刮削能力
  - 可配置的线程数
  - 性能监控系统
  - 爬虫健康状态监控

- 🛠️ **丰富的工具集**
  - 演员数据库管理（Excel 格式）
  - Emby/Jellyfin 演员图片和信息同步
  - 字幕管理
  - 缺失文件检测
  - 海报裁剪工具

- 🧪 **TMDB 集成**：演员 TMDB ID 获取和翻译
  - 令牌桶限流器，避免触发 API 限流
  - 并发查询，提高效率
  - 支持批量查询

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
- 🔧 [开发指南](DEVELOPMENT.md) - 开发者文档
- ❓ [FAQ](FAQ.md) - 常见问题解答

### 详细文档

#### 用户文档

- 📗 [用户使用手册](USER_GUIDE.md) - 完整的用户指南，包含安装、配置和使用说明
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