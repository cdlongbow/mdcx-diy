# MDCx Code Wiki

> 💡 **提示**：本文档已拆分为多个独立章节，可在 [docs/](docs/) 目录查看更详细的文档。

## 目录

1. [项目概述](#项目概述)
2. [项目架构](#项目架构) → [独立文档](architecture.md)
3. [核心模块](#核心模块) → [独立文档](core-modules.md)
4. [数据模型](#数据模型) → [独立文档](data-models.md)
5. [配置系统](#配置系统) → [独立文档](configuration.md)
6. [爬虫系统](#爬虫系统) → [独立文档](crawler-system.md)
7. [工具模块](#工具模块) → [独立文档](tools.md)
8. [命名系统](#命名系统) → [独立文档](naming-system.md)
9. [项目运行方式](#项目运行方式)
10. [依赖关系](#依赖关系) → [独立文档](dependencies.md)

### 附录

A. [PyQt6 迁移指南](#pyqt6-迁移指南) → [独立文档](pyqt6-migration.md)
B. [爬虫迁移指南](#爬虫迁移指南) → [独立文档](crawler-migration.md)

---

## 快速链接

- [docs/README.md](README.md) - 文档中心入口
- [docs/architecture.md](architecture.md) - 项目架构详解
- [docs/core-modules.md](core-modules.md) - 核心模块详解
- [docs/data-models.md](data-models.md) - 数据模型详解
- [docs/configuration.md](configuration.md) - 配置系统详解
- [docs/crawler-system.md](crawler-system.md) - 爬虫系统详解
- [docs/tools.md](tools.md) - 工具模块详解
- [docs/naming-system.md](naming-system.md) - 命名系统详解
- [docs/dependencies.md](dependencies.md) - 依赖关系详解
- [docs/api-documentation.md](api-documentation.md) - API 文档参考
- [docs/TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md) - 测试覆盖率

### 迁移指南

- [docs/pyqt6-migration.md](pyqt6-migration.md) - PyQt6 迁移方案
- [docs/crawler-migration.md](crawler-migration.md) - 爬虫新版框架迁移指南

### 代码质量

- [docs/CODE_REVIEW_CHECKLIST.md](CODE_REVIEW_CHECKLIST.md) - 代码审查检查清单
- [docs/CODE_REVIEW_GUIDE.md](CODE_REVIEW_GUIDE.md) - 代码审查指南
- [docs/CODE_REVIEW_STANDARDS.md](CODE_REVIEW_STANDARDS.md) - 代码审查标准

---

## 项目概述

### 项目简介

MDCx（Movie Data Capture X）是一个现代化的视频元数据刮削和管理工具，主要用于从 34+ 个成人视频网站获取元数据信息，包括标题、简介、演员、标签、封面图等，并支持与 Emby、Jellyfin 等媒体服务器集成。

### 核心功能

1. **智能刮削**：支持 34+ 个数据源网站，自动识别番号和马赛克类型
2. **元数据管理**：生成符合 Kodi/Emby 规范的 NFO 文件
3. **图片处理**：自动下载、裁剪、添加水印
4. **翻译功能**：支持 Google/百度/DeepL/LLM 翻译
5. **命名管理**：灵活的 Jinja2 模板系统，支持自定义命名规则
6. **Amazon 集成**：条码识别，自动匹配高清封面
7. **异步处理**：高效的并发刮削能力
8. **演员数据库**：Excel 格式的演员信息管理
9. **TMDB 集成**：演员 TMDB ID 获取和翻译
10. **Emby 集成**：自动更新 Emby/Jellyfin 媒体服务器

### 项目特色

- 高度模块化设计，易于维护和扩展
- 完善的配置系统，支持字段级优先级配置
- 强大的自定义模板系统
- 完善的错误处理和降级策略
- 跨平台支持（Windows、macOS、Linux）
- 网络指纹伪装，避免反爬检测

---

## 项目架构

### 目录结构

```
/workspace/
├── main.py                         # 程序入口
├── pyproject.toml                  # 项目配置和依赖管理
├── mdcx/                           # 主源码目录
│   ├── __init__.py
│   ├── consts.py                   # 常量定义（版本号、平台检测等）
│   ├── crawler.py                  # 爬虫提供器
│   ├── number.py                   # 番号解析和验证
│   ├── signals.py                  # 信号机制（Qt 信号）
│   ├── web_async.py                # 异步网络客户端
│   ├── base/                       # 基础功能模块
│   │   ├── file.py                 # 文件操作
│   │   ├── image.py                # 图片处理
│   │   ├── number.py               # 番号解析
│   │   ├── translate.py            # 翻译功能
│   │   ├── video.py                # 视频处理
│   │   ├── web.py                  # 网络请求
│   │   └── web_sync.py             # Web 同步操作
│   ├── config/                     # 配置管理
│   │   ├── computed.py             # 计算属性
│   │   ├── enums.py                # 配置枚举
│   │   ├── extend.py               # 扩展配置
│   │   ├── manager.py              # 配置管理器
│   │   ├── migrations.py           # 配置迁移
│   │   ├── models.py               # 配置模型
│   │   ├── resource_policy.py      # 资源策略
│   │   ├── resources.py            # 资源管理
│   │   └── v1.py                   # V1 配置兼容
│   ├── controllers/                # 控制器（业务逻辑）
│   │   ├── cut_window.py           # 裁剪窗口控制器
│   │   └── main_window/            # 主窗口控制器
│   │       ├── init.py             # 初始化
│   │       ├── main_window.py      # 主窗口逻辑
│   │       ├── handlers.py         # 事件处理
│   │       ├── bind_utils.py       # 绑定工具
│   │       ├── load_config.py      # 加载配置
│   │       ├── save_config.py      # 保存配置
│   │       ├── site_priority_dialog.py  # 站点优先级对话框
│   │       └── style.py            # 样式设置
│   ├── core/                       # 核心功能
│   │   ├── amazon.py               # Amazon 集成
│   │   ├── amazon_database.py      # Amazon 数据库缓存
│   │   ├── face_crop.py            # 人脸裁剪
│   │   ├── file.py                 # 文件处理
│   │   ├── file_crawler.py         # 文件刮削
│   │   ├── image.py                # 图片处理
│   │   ├── media_resource.py       # 媒体资源
│   │   ├── mosaic.py               # 马赛克处理
│   │   ├── naming/                 # 命名系统
│   │   │   ├── fields.py           # 命名字段
│   │   │   ├── renderer.py         # 渲染器
│   │   │   ├── sanitize.py         # 清理
│   │   │   └── template.py         # 模板
│   │   ├── network_check.py        # 网络检查
│   │   ├── nfo.py                  # NFO 生成
│   │   ├── scraper.py              # 刮削器
│   │   ├── tag_priority.py         # 标签优先级
│   │   ├── tmdb_actor.py           # TMDB 演员
│   │   ├── translate.py            # 翻译
│   │   ├── utils.py                # 工具函数
│   │   └── web.py                  # Web 操作
│   ├── crawlers/                   # 爬虫实现
│   │   ├── base/                   # 爬虫基类
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # 基础爬虫类
│   │   │   ├── parser.py           # 解析器
│   │   │   └── types.py            # 类型定义
│   │   ├── airav_cc.py             # Airav.cc 爬虫
│   │   ├── avbase_new.py           # AVBase 爬虫
│   │   ├── avsox.py                # AVSoX 爬虫
│   │   ├── cableav.py              # CableAV 爬虫
│   │   ├── cnmdb.py                # CNMDB 爬虫
│   │   ├── dahlia.py               # Dahlia 爬虫
│   │   ├── dmm_new/                # DMM 爬虫
│   │   ├── faleno.py               # Faleno 爬虫
│   │   ├── fantastica.py           # Fantastica 爬虫
│   │   ├── fc2.py                  # FC2 爬虫
│   │   ├── fc2club.py              # FC2Club 爬虫
│   │   ├── fc2hub.py               # FC2Hub 爬虫
│   │   ├── fc2ppvdb.py             # FC2PPVDB 爬虫
│   │   ├── freejavbt.py            # FreeJAVBT 爬虫
│   │   ├── getchu.py               # Getchu 爬虫
│   │   ├── getchu_dmm.py           # Getchu DMM 爬虫
│   │   ├── giga.py                 # Giga 爬虫
│   │   ├── guochan.py              # 国产爬虫
│   │   ├── hdouban.py              # 豆瓣爬虫
│   │   ├── hscangku.py             # 红色仓库爬虫
│   │   ├── iqqtv.py                # IQQTV 爬虫
│   │   ├── jav321.py               # Jav321 爬虫
│   │   ├── javbus.py               # JavBus 爬虫
│   │   ├── javday.py               # JavDay 爬虫
│   │   ├── javdb_new.py            # JavDB 爬虫
│   │   ├── javdbapi.py             # JavDB API 爬虫
│   │   ├── javlibrary.py           # JavLibrary 爬虫
│   │   ├── kin8.py                 # Kin8 爬虫
│   │   ├── libredmm.py             # LibreDMM 爬虫
│   │   ├── lulubar.py              # 芦芦吧爬虫
│   │   ├── madouqu.py              # 马豆区爬虫
│   │   ├── mdtv.py                 # MDTV 爬虫
│   │   ├── mgstage.py              # MGStage 爬虫
│   │   ├── missav.py               # MissAV 爬虫
│   │   ├── mmtv.py                 # MMTV 爬虫
│   │   ├── mywife.py               # MyWife 爬虫
│   │   ├── official.py             # 官方站点爬虫
│   │   ├── prestige.py             # Prestige 爬虫
│   │   ├── theporndb.py            # ThePornDB 爬虫
│   │   └── xcity.py                # X-City 爬虫
│   ├── gen/                        # 自动生成的枚举
│   ├── models/                     # 数据模型
│   │   ├── emby.py                 # Emby 模型
│   │   ├── enums.py                # 枚举
│   │   ├── flags.py                # 标志
│   │   ├── log_buffer.py           # 日志缓冲
│   │   └── types.py                # 类型定义
│   ├── tools/                      # 工具模块
│   │   ├── actress_db.py           # 演员数据库
│   │   ├── emby_actor_image.py     # Emby 演员图片
│   │   ├── emby_actor_info.py      # Emby 演员信息
│   │   ├── missing.py              # 缺失文件检测
│   │   ├── subtitle.py             # 字幕管理
│   │   └── wiki.py                 # Wiki 工具
│   ├── utils/                      # 工具函数
│   │   ├── dataclass.py            # 数据类工具
│   │   ├── file.py                 # 文件工具
│   │   ├── gather_group.py         # 分组工具
│   │   ├── language.py             # 语言工具
│   │   ├── path.py                 # 路径工具
│   │   └── video.py                # 视频工具
│   └── views/                      # UI 视图
│       ├── CustomClass.py          # 自定义类
│       ├── MDCx.py                 # 主视图
│       └── posterCutTool.py        # 海报裁剪工具
├── resources/                      # 资源文件
│   ├── config/                     # 默认配置
│   ├── c_number/                   # C 番号数据
│   ├── fonts/                      # 字体
│   ├── mapping_table/              # 映射表
│   └── userdata/                   # 用户数据
│       └── actor_database.xlsx     # 演员数据库
├── scripts/                        # 脚本工具
├── tests/                          # 测试代码
└── docs/                           # 项目文档
```

### 架构分层

MDCx 采用经典的 MVC 分层架构：

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (PyQt6)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ MainWindow   │  │ SettingsUI   │  │ ProgressUI   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Controller Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ EventHandler │  │ ConfigMgr    │  │ SignalBus   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Business Logic                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Scraper     │  │ FileCrawler  │  │ NamingSystem │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   NFO Gen    │  │  Amazon OCR  │  │  Translator  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ TMDb Actor   │  │ Image Proc   │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Crawler Framework                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │              GenericBaseCrawler[T]                │      │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐│      │
│  │  │ JAVBus │  │JavLib  │  │  DMM   │  │  FC2   ││      │
│  │  └────────┘  └────────┘  └────────┘  └────────┘│      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ HTTP Client  │  │ File System  │  │ Image Proc   │     │
│  │ (httpx)      │  │ (asyncio)    │  │ (OpenCV)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 主要模块依赖关系

```
main.py
  └─> controllers/main_window/
        └─> core/scraper.py
              ├─> crawler.py
              │     └─> crawlers/
              ├─> core/file_crawler.py
              ├─> core/nfo.py
              ├─> core/media_resource.py
              ├─> core/translate.py
              └─> config/manager.py
```

### 数据流程

1. **文件扫描**：FileCrawler 扫描媒体目录，识别视频文件
2. **番号识别**：从文件名中提取番号，识别马赛克类型
3. **爬虫执行**：根据配置调用相应网站的爬虫
4. **数据整合**：整合多个网站的结果，应用字段优先级
5. **翻译处理**：根据配置翻译元数据
6. **命名生成**：应用命名模板生成新的文件名和目录名
7. **资源下载**：下载海报、缩略图、背景图、预告片等
8. **元数据写入**：生成 NFO 文件
9. **文件移动**：移动和重命名文件到目标位置

---

## 核心模块

### 1. 刮削器核心 ([mdcx/core/scraper.py](mdcx/core/scraper.py))

**功能**：主刮削器，协调整个刮削流程

**主要类**：
- `Scraper`：刮削器主类
  - `run()`：执行刮削
  - `process_one_file()`：处理单个文件
  - `_run_tasks_with_limit()`：渐进式任务调度

**刮削流程**：
1. 获取文件信息
2. 调用爬虫获取数据
3. 翻译元数据
4. 下载图片和预告片
5. 添加水印
6. 生成 NFO
7. 移动和重命名文件
8. 创建软链接（可选）

**关键特性**：
- 渐进式任务调度，支持大量文件
- 并发控制，可配置线程数
- 间歇刮削支持
- 停止/恢复支持

### 2. 文件爬虫 ([mdcx/core/file_crawler.py](mdcx/core/file_crawler.py))

**功能**：处理单个文件的刮削逻辑

**主要类**：
- `ScrapeClassification`：刮削分类结果
- `FileScraper`：文件爬虫

**番号识别规则**：
- **国产番号**：MD系列、MKY系列、马赛克标记为"国产"
- **素人番号**：SIRO系列、短番号
- **FC2番号**：包含"FC2"的番号
- **欧美番号**：格式 `XXX.00.00.00`
- **特定网站**：KIN8、Getchu、Mywife 等
- **无码番号**：通过番号格式识别
- **默认**：有码番号

**结果整合逻辑**：
- 字段级优先级：每个字段独立配置优先级
- 缓存机制：已请求的网站数据缓存
- 数据归约：从多个来源归约到单一结果
- 去重处理：演员、标签等去重

### 3. NFO 生成器 ([mdcx/core/nfo.py](mdcx/core/nfo.py))

**功能**：生成符合 Kodi/Emby 规范的 NFO 文件

**支持的字段**：
- 基本信息：番号、标题、原始标题、排序标题、剧情简介
- 发行信息：首播日期、发行日期、年份、标语
- 分类信息：家长分级、自定义分级、国家代码
- 人员信息：演员、导演
- 评分信息：公众评分、影评人评分、想看人数
- 分类标签：标签、类型、系列
- 制作信息：制作商、厂牌、发行商、标签
- 媒体资源：海报、封面、预告片 URL
- 外部 ID：各网站的外部 ID（如 javdbid、javlibid 等）

**主要方法**：
- `write_nfo()`：生成 NFO 文件
- `get_nfo_data()`：读取 NFO 文件
- `get_external_id_tag_name()`：生成外部 ID 标签名

### 4. TMDB 演员 ([mdcx/core/tmdb_actor.py](mdcx/core/tmdb_actor.py))

**功能**：通过 TMDB API 查询日本成人演员信息

**主要类**：
- `_TmdbRateLimiter`：令牌桶限流器
  - 令牌生成速率：3.5 个/秒
  - 突发容量：10 个令牌
  - 请求前先获取令牌

**主要方法**：
- `load_actor_db()`：加载演员数据库
- `search_actor_db_reverse()`：反向搜索演员数据库
- `fetch_actor_tmdb_ids()`：批量查询演员的 TMDB ID
- `_query_single_actor()`：查询单个演员的 TMDB 信息

**速率限制机制**：
1. **令牌桶算法**：控制 API 请求速率
2. **并发限制**：Semaphore 限制并发数为 3
3. **请求间隔**：每个查询后 sleep 0.5 秒

#### TMDB 数据流

**数据获取流程**：

```
演员原名 → 演员数据库 → TMDB ID → TMDB API → 演员详细信息
```

**详细步骤**：

1. **查询演员数据库**
   - 从 Excel 数据库加载演员信息
   - 支持正向和反向搜索
   - 数据库包含：日文名、中文名、繁体名、别名、TMDB ID 等

2. **批量获取 TMDB ID**
   - 调用 `fetch_actor_tmdb_ids()` 批量查询
   - 使用令牌桶限流器控制请求速率
   - Semaphore 限制并发数为 3

3. **查询单个演员**
   - 调用 TMDB Search API 搜索演员
   - 根据演员原名和别名匹配
   - 返回 TMDB ID 和详细信息

4. **获取演员详细信息**
   - 使用 TMDB Person API 获取完整信息
   - 包括：出生日期、出生地、生平简介、图片等
   - 支持多语言查询（日语、英语等）

**速率限制**：

- **令牌桶算法**：3.5 个令牌/秒，突发容量 10 个
- **并发限制**：最大 3 个并发请求
- **请求间隔**：每个查询后 0.5 秒延迟

**数据缓存**：

- **演员数据库缓存**：程序启动时加载到内存
- **TMDB API 响应缓存**：避免重复查询同一演员
- **错误重试机制**：失败自动重试，最多 3 次

**错误处理**：

1. **网络错误**：自动重试，增加延迟
2. **API 限流**：等待令牌桶补充令牌
3. **查询失败**：记录日志，继续处理其他演员
4. **数据缺失**：使用数据库中的备用信息

**最佳实践**：

1. **批量查询**：尽量一次性查询多个演员，提高效率
2. **错误容忍**：单个演员查询失败不影响整体流程
3. **速率控制**：严格遵守 TMDB API 速率限制，避免被封禁
4. **数据备份**：定期备份演员数据库，防止数据丢失

### 5. Amazon 集成 ([mdcx/core/amazon.py](mdcx/core/amazon.py))

**功能**：Amazon ASIN 获取和高清封面匹配

**主要方法**：
- `search_asin()`：搜索 ASIN
- `get_hd_poster()`：获取高清海报

### 6. 图片处理 ([mdcx/core/image.py](mdcx/core/image.py))

**功能**：图片下载、裁剪、添加水印

**主要方法**：
- `download_file_with_filepath()`：下载图片到指定路径
- `fix_pic_async()`：异步修复图片
- `cut_pic()`：裁剪图片为 2:3 比例

### 7. 人脸裁剪 ([mdcx/core/face_crop.py](mdcx/core/face_crop.py))

**功能**：智能人脸检测和裁剪

**主要方法**：
- `detect_faces()`：检测人脸
- `crop_face()`：裁剪人脸区域

### 8. 翻译系统 ([mdcx/core/translate.py](mdcx/core/translate.py))

**功能**：支持多种翻译服务

**支持的翻译服务**：
- Google 翻译
- 百度翻译
- DeepL 翻译
- DeepLX 翻译
- LLM 翻译（支持自定义 API）

---

## 数据模型

### 主要数据类 ([mdcx/models/types.py](mdcx/models/types.py))

#### `FileInfo`

媒体文件基础信息

**主要字段**：
- `number`：番号
- `mosaic`：马赛克类型
- `file_path`：文件路径
- `has_sub`：是否有字幕
- `definition`：分辨率
- `codec`：编码格式
- `c_word`：C 字
- `cd_part`：CD 部分
- `destroyed`：是否破解
- `leak`：是否流出

**主要方法**：
- `crawler_input()`：转换为爬虫输入
- `crawl_task()`：转换为刮削任务
- `empty()`：创建空实例

#### `CrawlerInput`

单个爬虫调用输入

**主要字段**：
- `appoint_number`：指定番号
- `appoint_url`：指定 URL
- `file_path`：文件路径
- `number`：番号
- `mosaic`：马赛克类型
- `short_number`：短番号
- `language`：语言
- `org_language`：原始语言

#### `CrawlTask`

单个文件刮削任务，继承自 `CrawlerInput`

**额外字段**：
- `c_word`：C 字
- `cd_part`：CD 部分
- `destroyed`：是否破解
- `has_sub`：是否有字幕
- `leak`：是否流出
- `website_name`：网站名称
- `wuma`：是否无码
- `youma`：是否有码

#### `BaseCrawlerResult`

爬虫结果基础类型

**主要字段**：
- `number`：番号
- `mosaic`：马赛克类型
- `image_download`：是否需要下载图片
- `actors`：演员列表
- `all_actors`：所有演员列表
- `directors`：导演列表
- `extrafanart`：额外剧照 URL 列表
- `originalplot`：原始简介（日文）
- `originaltitle`：原始标题（日文）
- `outline`：简介
- `poster`：海报 URL
- `publisher`：发行商
- `release`：发行日期
- `runtime`：片长（分钟）
- `score`：评分
- `series`：系列
- `studio`：制作商
- `tags`：标签列表
- `thumb`：缩略图 URL
- `title`：标题
- `trailer`：预告片 URL
- `wanted`：想看数
- `year`：发行年份

#### `CrawlerResult`

单一网站爬虫结果

**额外字段**：
- `source`：数据来源（爬虫名称）
- `external_id`：外部 ID

#### `CrawlersResult`

整合所有网站的结果

**额外字段**：
- `scraping_type`：刮削类型
- `scraping_type_source`：分类来源
- `actor_amazon`：用于 Amazon 搜索的演员名称
- `thumb_list`：所有来源的缩略图 URL 列表
- `poster_list`：所有来源的海报 URL 列表
- `actor_tmdb_ids`：演员原名→TMDB ID 映射
- `site_log`：网站日志
- `field_log`：字段来源信息
- `field_sources`：字段来源
- `external_ids`：各来源的 externalId

#### `OtherInfo`

其他处理信息（文件移动、水印等）

#### `ScrapeResult`

刮削结果封装

#### `ShowData`

显示数据

### 数据流转关系

```
FileInfo → CrawlerInput → CrawlTask
             ↓
         CrawlerResult ← CrawlerResponse
             ↓
         CrawlersResult
             ↓
         ScrapeResult ← OtherInfo
             ↓
         ShowData
```

---

## 配置系统

### 配置模型 ([mdcx/config/models.py](mdcx/config/models.py))

#### `Config`

主配置类，基于 Pydantic

**主要配置区域**：

1. **通用设置**
   - `media_path`：媒体路径
   - `softlink_path`：软链接路径
   - `success_output_folder`：成功输出目录
   - `failed_output_folder`：失败输出目录
   - `media_type`：媒体文件类型列表
   - `sub_type`：字幕文件类型列表

2. **清理设置**
   - `folders`：排除目录列表
   - `string`：要从文件名删除的字符串列表
   - `file_size`：要处理的最小文件大小（MB）
   - `clean_*`：各种清理规则

3. **刮削设置**
   - `thread_number`：并发数
   - `thread_time`：线程延时
   - `main_mode`：主模式
   - `read_mode`：读取模式
   - `update_mode`：更新模式
   - `download_files`：下载文件类型列表
   - `scrape_like`：刮削模式

4. **网站设置**
   - `website_youma`：有码网站源列表
   - `website_wuma`：无码网站源列表
   - `website_suren`：素人网站源列表
   - `website_fc2`：FC2 网站源列表
   - `website_oumei`：欧美网站源列表
   - `website_guochan`：国产网站源列表
   - `fixed_scraping_type`：锁定刮削类型

5. **字段配置**
   - `field_configs`：各字段的网站优先级、语言、翻译开关
   - `type_field_configs`：按类型字段优先级
   - `site_configs`：网站配置

6. **翻译配置**
   - `translate_config`：`TranslateConfig` 对象
     - `translate_by`：翻译服务列表
     - `baidu_appid`：百度 APP ID
     - `baidu_key`：百度密钥
     - `deepl_key`：DeepL 密钥
     - `deeplx_url`：DeepLX URL
     - `llm_*`：LLM 相关配置

7. **命名和格式化**
   - `nfo_include_new`：NFO 包含内容列表
   - `folder_name`：目录名称模板
   - `naming_file`：文件命名模板
   - `naming_media`：媒体命名模板
   - `prevent_char`：禁止字符
   - `fields_rule`：字段规则列表
   - `*_style`：各类样式

8. **服务器设置**
   - `server_type`：服务器类型（emby/jellyfin）
   - `emby_url`：Emby 地址
   - `api_key`：API 密钥
   - `user_id`：用户 ID
   - `emby_on`：Emby 功能开关列表
   - `use_database`：使用数据库
   - `info_database_path`：信息数据库路径

9. **水印设置**
   - `poster_mark`、`thumb_mark`、`fanart_mark`：各图片水印
   - `mark_size`：水印大小
   - `mark_type`：水印类型列表
   - `mark_fixed`、`mark_pos*`：水印位置规则

10. **网络设置**
    - `use_proxy`：代理类型
    - `proxy`：代理地址
    - `no_proxy_sites`：不使用代理网站
    - `cf_bypass_*`：Cloudflare Bypass 配置
    - `timeout`、`retry`：超时和重试
    - `theporndb_api_token`、`tmdb_api_key`：API 密钥

11. **日志设置**
    - `show_web_log`：显示网页日志
    - `show_from_log`：显示来源日志
    - `show_data_log`：显示数据日志
    - `save_log`：保存日志

**主要方法**：
- `get_site_config(site)`：获取网站配置
- `get_site_url(site, default)`：获取网站自定义 URL
- `get_field_config(field)`：获取字段配置
- `get_type_sites(scraping_type)`：获取类型网站
- `get_type_field_config(scraping_type, field)`：获取类型字段配置
- `set_field_sites(field, sites)`：设置字段网站
- `set_field_language(field, language)`：设置字段语言
- `set_field_translate(field, translate)`：设置字段翻译

### 配置枚举 ([mdcx/config/enums.py](mdcx/config/enums.py))

#### `Website`

支持的网站枚举（34个站点）

#### `FixedScrapingType`

刮削类型枚举

**类型**：
- `AUTO`：自动
- `YOUMA`：有码
- `WUMA`：无码
- `SUREN`：素人
- `FC2`：FC2
- `OUMEI`：欧美
- `GUOCHAN`：国产

#### 其他枚举

- `Language`：语言
- `Translator`：翻译服务
- `EmbyAction`：Emby 操作
- `DownloadableFile`：可下载文件类型
- `KeepableFile`：可保留文件类型
- `ReadMode`：读取模式
- `Switch`：功能开关
- `NfoInclude`：NFO 包含内容
- `MarkType`：水印类型
- 等等...

### 配置管理器 ([mdcx/config/manager.py](mdcx/config/manager.py))

#### `ConfigManager`

管理配置的加载、保存、迁移等

**主要方法**：
- `__init__()`：初始化
- `load()`：加载配置
- `save()`：保存配置
- `reset()`：重置为默认配置
- `handle_v1()`：处理 V1 配置
- `_replace_config()`：热切换配置
- `acquire_computed()`：获取计算属性租约

**配置加载流程**：
1. 检查标记文件确定配置路径
2. 尝试加载配置文件
3. 如果是旧版 .ini 配置，自动转换为新版
4. 验证配置
5. 应用配置

---

## 爬虫系统

### 爬虫基类 ([mdcx/crawlers/base/base.py](mdcx/crawlers/base/base.py))

#### `GenericBaseCrawler[T]`

泛型爬虫基类，所有具体爬虫均应继承此类并实现其抽象方法

**主要特性**：
- 支持自定义上下文类型
- 统一的爬虫生命周期管理
- 性能监控集成
- 爬虫健康监测集成
- 完善的错误处理

**主要方法**：
- `__init__(client, base_url)`：初始化爬虫
- `close()`：释放资源
- `site()`：返回此爬虫对应的网站枚举（抽象方法）
- `base_url_()`：返回默认 URL（抽象方法）
- `display_name()`：返回前端显示名称
- `new_context(input)`：创建新上下文（抽象方法）
- `run(input)`：执行爬虫任务
- `_run(ctx)`：内部执行逻辑
- `_generate_search_url(ctx)`：生成搜索 URL（抽象方法）
- `_search(ctx, search_urls)`：执行搜索
- `_parse_search_page(ctx, selector, search_url)`：解析搜索页（抽象方法）
- `_detail(ctx, detail_urls)`：获取详情页
- `_parse_detail_page(ctx, selector, detail_url)`：解析详情页（抽象方法）
- `post_process(ctx, data)`：后处理

**爬虫生命周期**：
1. 初始化爬虫实例
2. 创建上下文
3. 生成搜索 URL（或使用指定 URL）
4. 请求搜索页
5. 解析搜索页，获取详情页 URL
6. 请求详情页
7. 解析详情页，获取数据
8. 后处理
9. 返回结果

### 爬虫注册与获取

**主要机制**：
- 装饰器模式注册爬虫
- 工厂模式获取爬虫实例
- 懒加载优化性能

### 爬虫实现目录 ([mdcx/crawlers/](mdcx/crawlers/))

每个网站一个爬虫文件，共 39 个站点

**添加新爬虫的步骤**：
1. 在 `mdcx/crawlers/` 下创建新文件
2. 继承 `BaseCrawler`（或 `GenericBaseCrawler`）
3. 实现抽象方法
4. 使用 `@register_crawler` 装饰器注册
5. 在 `Website` 枚举中添加对应网站

---

## 工具模块

### 演员数据库 ([mdcx/tools/actress_db.py](mdcx/tools/actress_db.py))

**功能**：管理 Excel 格式的演员数据库

**主要功能**：
- 加载演员数据库
- 搜索演员信息
- 更新演员数据

### Emby 演员 ([mdcx/tools/emby_actor_info.py](mdcx/tools/emby_actor_info.py))

**功能**：更新 Emby/Jellyfin 演员信息

**数据来源**：
- Wikipedia：获取简介、出生日期、出生地等
- 本地数据库：获取中文名、别名等

### Emby 演员图片 ([mdcx/tools/emby_actor_image.py](mdcx/tools/emby_actor_image.py))

**功能**：更新 Emby/Jellyfin 演员图片

**图片来源**：
- graphis.ne.jp：日本写真网站
- Gfriends GitHub：头像库
- 本地文件夹

### 缺失文件检测 ([mdcx/tools/missing.py](mdcx/tools/missing.py))

**功能**：检测缺失的文件

### 字幕管理 ([mdcx/tools/subtitle.py](mdcx/tools/subtitle.py))

**功能**：批量字幕处理

### Wiki 工具 ([mdcx/tools/wiki.py](mdcx/tools/wiki.py))

**功能**：查询 Wikipedia 信息

---

## Emby 集成

### 概述

MDCx 提供与 Emby 和 Jellyfin 媒体服务器的深度集成功能，可以自动更新演员信息和图片，提升媒体库的管理体验。

### 集成模块

#### Emby 演员 ([mdcx/tools/emby_actor_info.py](mdcx/tools/emby_actor_info.py))

**功能**：更新 Emby/Jellyfin 演员信息

**数据来源**：
- Wikipedia：获取简介、出生日期、出生地等
- 本地数据库：获取中文名、别名等

**主要功能**：
- 自动获取演员的详细简介
- 更新演员的出生日期、出生地等元数据
- 支持批量更新多个演员

**使用方式**：
```python
from mdcx.tools.emby_actor_info import EmbyActorInfo

# 创建实例
emby_info = EmbyActorInfo()

# 更新演员信息
emby_info.update_actor(actor_id, tmdb_id)
```

#### Emby 演员图片 ([mdcx/tools/emby_actor_image.py](mdcx/tools/emby_actor_image.py))

**功能**：更新 Emby/Jellyfin 演员图片

**图片来源**：
- graphis.ne.jp：日本写真网站
- Gfriends GitHub：头像库
- 本地文件夹

**主要功能**：
- 从多个来源获取演员图片
- 自动下载和上传图片到 Emby/Jellyfin
- 支持图片格式转换和优化

**使用方式**：
```python
from mdcx.tools.emby_actor_image import EmbyActorImage

# 创建实例
emby_image = EmbyActorImage()

# 更新演员图片
emby_image.update_image(actor_id, image_url)
```

### 配置说明

在配置文件中添加以下配置项：

```ini
[emby]
# 服务器类型（emby 或 jellyfin）
server_type = emby

# 服务器地址
emby_url = http://localhost:8096

# API 密钥
api_key = your_api_key_here

# 功能开关列表
emby_on = actor_info,actor_image
```

### Emby 演员信息补全流程

#### 数据流

```
1. Wikipedia API
   ↓
2. 提取演员信息（简介、出生日期、出生地）
   ↓
3. Emby/Jellyfin API
   ↓
4. 更新演员元数据
```

#### 配置 Emby/Jellyfin

1. **获取 API Key**
   - 登录 Emby/Jellyfin 管理界面
   - 进入设置 > API Keys
   - 创建新的 API Key

2. **配置服务器信息**
   - 在 MDCx 配置中填写服务器地址
   - 填入 API Key
   - 选择服务器类型

3. **启用自动同步**
   - 在配置中启用 `emby_on` 选项
   - 选择需要同步的功能

### Emby 演员图片补全流程

#### 数据源优先级

```
1. graphis.ne.jp（优先）
   ↓
2. Gfriends GitHub（备选）
   ↓
3. 本地文件夹（兜底）
```

#### 配置图片来源

```python
# 在代码中配置图片来源
IMAGE_SOURCES = [
    'graphis.ne.jp',
    'github.com/Gfriends',
    'local'
]
```

### 完整的 Emby 集成工作流

1. **刮削视频元数据**
   - 从 34+ 个成人视频网站获取元数据
   - 提取演员信息

2. **补全演员信息**
   - 从 TMDB 获取演员详细信息
   - 从 Wikipedia 获取演员简介
   - 从本地数据库获取中文名和别名

3. **更新 Emby/Jellyfin**
   - 通过 API 更新演员信息
   - 下载并上传演员图片

4. **生成 NFO 文件**
   - 生成符合 Kodi/Emby 规范的 NFO 文件

### API 参考

#### Emby 演员 API

```python
class EmbyActorInfo:
    def __init__(self, config):
        """初始化 Emby 演员 API"""
        pass

    def update_actor(self, actor_id, tmdb_id):
        """
        更新演员信息

        Args:
            actor_id: 演员 ID
            tmdb_id: TMDB ID
        """
        pass

    def get_actor_from_wikipedia(self, name):
        """
        从 Wikipedia 获取演员信息

        Args:
            name: 演员名称

        Returns:
            dict: 演员信息
        """
        pass
```

#### Emby 演员图片 API

```python
class EmbyActorImage:
    def __init__(self, config):
        """初始化 Emby 演员 API"""
        pass

    def update_image(self, actor_id, image_url):
        """
        更新演员图片

        Args:
            actor_id: 演员 ID
            image_url: 图片 URL
        """
        pass

    def download_image(self, url):
        """
        下载图片

        Args:
            url: 图片 URL

        Returns:
            bytes: 图片数据
        """
        pass

    def upload_to_emby(self, actor_id, image_data):
        """
        上传图片到 Emby

        Args:
            actor_id: 演员 ID
            image_data: 图片数据
        """
        pass
```

### 故障排除

#### 问题 1：无法连接到 Emby/Jellyfin

**解决方案**：
- 检查服务器地址是否正确
- 确认 API Key 是否有效
- 检查网络连接
- 确认 Emby/Jellyfin 服务是否正在运行

#### 问题 2：演员信息不更新

**解决方案**：
- 检查演员是否有对应的 TMDB ID
- 确认 Wikipedia 上是否有该演员的信息
- 查看日志文件了解详细错误信息

#### 问题 3：图片无法显示

**解决方案**：
- 检查图片 URL 是否有效
- 确认图片格式是否支持
- 检查 Emby/Jellyfin 的媒体路径配置
- 尝试手动刷新媒体库

### 最佳实践

1. **定期同步**
   - 设置定时任务定期同步演员信息
   - 避免手动操作遗漏

2. **批量处理**
   - 使用批量更新功能提高效率
   - 注意 API 速率限制

3. **备份数据**
   - 定期备份 Emby/Jellyfin 数据库
   - 防止数据丢失

4. **监控日志**
   - 定期查看日志文件
   - 及时发现和解决问题

### 相关文档

- [用户使用手册 - Emby 集成](USER_GUIDE.md#embyjellyfin-集成)
- [FAQ - Emby 问题](FAQ.md#embyjellyfin-集成)
- [Emby 集成](#emby-集成)

---

## 命名系统

### 模块结构 ([mdcx/core/naming/](mdcx/core/naming/))

```
mdcx/core/naming/
├── fields.py            # 字段定义和上下文构建
├── template.py          # 模板引擎
├── renderer.py          # 命名渲染
└── sanitize.py          # 名称清理
```

### 支持的字段

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

### 模板语法

使用 **Jinja2** 模板引擎：

```jinja2
# 简单变量
{{ number }}

# 条件渲染
{% if number %}{{ number }}{% endif %}

# 条件嵌套
[{% if number %}{{ number }}{% endif %}]{% if title and title != number %}{{ title }}{% endif %}

# 循环（高级用法）
{% for actor in actors %}{{ actor }}{% if not loop.last %}, {% endif %}{% endfor %}
```

### 常用模板

**目录模板**：
```jinja2
{{ actor }}/{{ number }} {{ actor }}
```

**文件模板**：
```jinja2
{{ number }}
```

**媒体模板**：
```jinja2
[{% if number %}{{ number }}{% endif %}]{% if title and title != number %}{{ title }}{% endif %}
```

### 智能截断

支持按优先级截断字段以适应最大长度限制：

1. 按优先级截断字段
2. 列表字段（演员、导演）按分隔符截断
3. 普通文本直接截断
4. 移除末尾标点和空格

---

## 项目运行方式

### 入口文件 ([main.py](main.py))

**启动流程**：

1. 显示运行时常量（平台、版本等）
2. 设置高 DPI 缩放策略
3. 创建 QApplication 实例
4. 设置应用样式（Fusion）
5. 应用主题配色
6. 加载主窗口 (`MyMAinWindow`)
7. 显示窗口
8. 安装事件过滤器
9. 启动事件循环

**关键代码**：
```python
app = QApplication(sys.argv)
app.setStyle("Fusion")
apply_application_palette(False)

ui = MyMAinWindow()
ui.show()

sys.exit(app.exec())
```

### 命令行工具 ([mdcx/cmd/](mdcx/cmd/))

**可用命令**：
- `crawl`：命令行刮削
- `gen_enums`：生成枚举

---

## 依赖关系

### 主要依赖

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

### 网络层

**异步 HTTP 客户端**：
- `httpx.AsyncClient`：主要 HTTP 客户端
- `curl_cffi.AsyncWebClient`：浏览器指纹伪装

**特性**：
- 连接池管理
- 请求限流
- 浏览器指纹伪装
- 支持 SOCKS 代理

### 数据持久层

**配置存储**：
- JSON 格式（V2）
- INI 格式（V1，已废弃）

**演员数据库**：
- Excel 格式（`.xlsx`）
- 使用 `openpyxl` 读写

### 日志系统

**信号机制** ([mdcx/signals.py](mdcx/signals.py))：
- Qt 信号机制
- 线程安全的日志系统
- UI 更新信号

---

## 技术栈总结

### 核心技术

- **UI 框架**：PyQt6
- **网络请求**：httpx, curl-cffi
- **HTML 解析**：parsel, lxml, BeautifulSoup4
- **数据验证**：Pydantic
- **异步处理**：asyncio, aiofiles
- **图片处理**：Pillow, opencv
- **视频处理**：av
- **模板引擎**：Jinja2
- **Excel 处理**：openpyxl
- **依赖管理**：uv

### 设计模式

- **MVC 模式**：Model-View-Controller 分层
- **爬虫注册模式**：装饰器 + 工厂模式
- **配置管理模式**：单例 + 热重载
- **观察者模式**：Qt 信号槽
- **策略模式**：字段优先级配置
- **模板方法模式**：爬虫基类定义流程

### 代码统计

- **核心模块**：~10,495 行
- **爬虫实现**：~11,222 行
- **基础模块**：~2,529 行
- **配置系统**：~1,017 行
- **控制器**：~3,376 行
- **视图**：~11,602 行

---

## 扩展开发

### 添加新爬虫

1. 在 `mdcx/crawlers/` 下创建新文件
2. 继承 `BaseCrawler` 或 `GenericBaseCrawler`
3. 实现抽象方法：
   - `site()`：返回网站枚举
   - `base_url_()`：返回默认 URL
   - `new_context()`：创建上下文
   - `_generate_search_url()`：生成搜索 URL
   - `_parse_search_page()`：解析搜索页
   - `_parse_detail_page()`：解析详情页
4. 使用 `@register_crawler` 装饰器注册
5. 在 `Website` 枚举中添加对应网站

### 添加新配置项

1. 在 `Config` 类中添加字段
2. 在 `models.py` 中添加验证器（如需要）
3. 在 `enums.py` 中添加枚举（如需要）
4. 更新 `migrations.py` 添加迁移逻辑
5. 在 UI 中添加对应控件

### 添加新命名字段

1. 在 `naming/fields.py` 中添加字段描述
2. 在 `build_naming_context()` 中添加字段值提取逻辑
3. 在 UI 中更新字段列表

---

## 常见问题

### Q1: 如何调试爬虫？

在爬虫的 `_parse_detail_page` 方法中添加 `ctx.debug()` 输出调试信息。

### Q2: 如何配置代理？

在设置中配置 `use_proxy` 和 `proxy`，支持 HTTP/SOCKS 代理。

### Q3: 如何添加自定义 URL？

在网站配置中设置 `custom_url`。

### Q4: 如何处理爬虫失效？

爬虫失效时，日志会显示错误信息。可以：
1. 检查网站是否有反爬更新
2. 更新爬虫代码
3. 临时禁用该站点

---

## 附录 A：PyQt6 迁移指南

详细的 PyQt6 迁移方案请参考：[docs/pyqt6-migration.md](pyqt6-migration.md)

### 主要差异

- `PyQt5` 包名迁移为 `PyQt6`
- Qt 枚举和 Flag 采用标准 Python `Enum`/`Flag`
- `exec_()` 已移除，统一改为 `exec()`
- `QAction` 从 `QtWidgets` 迁移到 `QtGui`
- Qt6 默认启用高 DPI 缩放

### 迁移阶段

- **第一阶段**：完成 PyQt6 基线迁移，更新依赖和 UI 文件
- **后续阶段**：增加主题策略、接入系统主题变化监听

---

## 附录 B：爬虫迁移指南

详细的刮削器新版框架迁移指南请参考：[docs/crawler-migration.md](crawler-migration.md)

### 迁移目标

- 所有刮削源统一为 `GenericBaseCrawler` / `BaseCrawler` 子类
- 通过 `register_crawler()` 注册新版类
- 统一返回 `CrawlerResponse` 和 `CrawlerResult`

### 已迁移站点

`dmm`, `javdb`, `javdbapi`, `avbase`, `missav`, `faleno`, `jav321`, `cableav`, `madouqu`, `mmtv`, `dahlia`, `fantastica`, `avsox`, `cnmdb`, `hscangku`, `kin8`, `love6`, `lulubar`, `xcity`, `giga`, `avsex`, `mdtv`, `mgstage`, `javday`, `fc2ppvdb`, `prestige`, `fc2club`, `fc2`, `fc2hub`, `javbus`, `freejavbt`, `hdouban`, `iqqtv`, `airav_cc`, `getchu`, `getchu_dmm`, `mywife`, `javlibrary`, `official`, `theporndb`

---

## 许可证

GPLv3

---

## 联系方式

- GitHub: https://github.com/cdlongbow/mdcx