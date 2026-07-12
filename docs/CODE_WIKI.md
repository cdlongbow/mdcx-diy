# MDCx Code Wiki

> 本文档已拆分为多个独立章节，可在 [文档中心](README.md) 查看详细文档。

## 目录

1. [项目概述](#项目概述)
2. [项目架构](#项目架构)
3. [核心模块](#核心模块)
4. [数据模型](#数据模型)
5. [配置系统](#配置系统)
6. [爬虫系统](#爬虫系统)
7. [工具模块](#工具模块)
8. [命名系统](#命名系统)
9. [项目运行方式](#项目运行方式)
10. [依赖关系](#依赖关系)

独立文档：[架构](architecture.md) | [核心模块](core-modules.md) | [数据模型](data-models.md) | [配置](configuration.md) | [爬虫系统](crawler-system.md) | [工具模块](tools.md) | [命名系统](naming-system.md) | [依赖关系](dependencies.md)

### 附录

A. [PyQt6 迁移指南](pyqt6-migration.md)
B. [爬虫迁移指南](crawler-migration.md)

---

## 快速链接

- [文档中心](README.md)
- [API 文档](api-documentation.md)
- [测试覆盖率](TEST_COVERAGE_SUMMARY.md)

### 代码质量

- [代码审查清单](CODE_REVIEW_CHECKLIST.md)
- [代码审查指南](CODE_REVIEW_GUIDE.md)
- [代码审查标准](CODE_REVIEW_STANDARDS.md)

---

## 项目概述

MDCx（Movie Data Capture X）是一个视频元数据刮削和管理工具，从 40+ 个成人视频网站获取元数据（标题、简介、演员、标签、封面图等），支持与 Emby、Jellyfin 集成（当前已注册 43 个爬虫，下拉框由已注册爬虫动态生成）。

### 核心功能

1. **智能刮削**：43 个数据源网站，自动识别番号和类型
2. **元数据管理**：NFO 文件（30+ 个字段），Kodi/Emby/Jellyfin 通用
3. **图片处理**：自动下载、裁剪、加水印
4. **翻译功能**：Google/Bing/百度/DeepL/DeepLX/LLM 六引擎
5. **命名管理**：Jinja2 模板
6. **Amazon 集成**：扫条码匹配高清封面
7. **异步处理**：多任务并发刮削
8. **演员数据库**：Excel 表管理，支持别名、多语言名、TMDB ID、网址
9. **TMDB 集成**：自动查询演员 TMDB ID
10. **自动补网址**：LibreDMM 补全演员链接
11. **Emby 集成**：自动更新媒体服务器信息

### 项目特色

- 高度模块化设计
- 字段级优先级配置
- 自定义模板系统
- 跨平台支持（Windows、macOS、Linux）
- 网络指纹伪装

---

## 项目架构

### 目录结构

```
./
├── main.py                         # 程序入口
├── pyproject.toml                  # 项目配置和依赖管理
├── mdcx/                           # 主源码目录
│   ├── __init__.py
│   ├── consts.py                   # 常量定义（版本号、平台检测等）
│   ├── crawler.py                  # 爬虫提供器
│   ├── number.py                   # 番号解析和验证
│   ├── signals.py                  # Qt 信号机制
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
│   ├── crawlers/                   # 爬虫实现（43 个已注册站点，下拉框动态生成）
│   ├── gen/                        # 自动生成的枚举
│   ├── models/                     # 数据模型
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
├── scripts/                        # 脚本工具
├── tests/                          # 测试代码
└── docs/                           # 项目文档
```

### 架构分层

MDCx 采用 MVC 分层架构：

```
UI Layer (PyQt6): MainWindow | SettingsUI | ProgressUI
    |
    v
Controller Layer: EventHandler | ConfigMgr | SignalBus
    |
    v
Core Business Logic: Scraper | FileCrawler | NamingSystem | NFO Gen | Amazon OCR | Translator | TMDb Actor | Image Proc
    |
    v
Crawler Framework: GenericBaseCrawler[T] - JAVBus | JavLib | DMM | FC2 | ...
    |
    v
Infrastructure: HTTP Client (httpx) | File System (asyncio) | Image (OpenCV)
```

### 主要模块依赖关系

```
main.py
  -> controllers/main_window/
        -> core/scraper.py
              +-> crawler.py
              |     -> crawlers/
              +-> core/file_crawler.py
              +-> core/nfo.py
              +-> core/media_resource.py
              +-> core/translate.py
              -> config/manager.py
```

### 数据流程

1. **文件扫描**：FileCrawler 扫描媒体目录，识别视频文件
2. **番号识别**：从文件名提取番号，识别马赛克类型
3. **爬虫执行**：根据配置调用相应网站的爬虫
4. **数据整合**：整合多个网站结果，应用字段优先级
5. **翻译处理**：根据配置翻译元数据
6. **命名生成**：应用命名模板生成文件名和目录名
7. **资源下载**：下载海报、缩略图、背景图、预告片
8. **元数据写入**：生成 NFO 文件
9. **文件移动**：移动和重命名文件到目标位置

---

## 核心模块

### 1. 刮削器核心 ([mdcx/core/scraper.py](../mdcx/core/scraper.py))

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

### 2. 文件爬虫 ([mdcx/core/file_crawler.py](../mdcx/core/file_crawler.py))

**功能**：处理单个文件的刮削逻辑

**主要类**：`ScrapeClassification`、`FileScraper`

**番号识别规则**：
- **国产番号**：MD 系列、MKY 系列，马赛克标记为"国产"
- **素人番号**：SIRO 系列、短番号
- **FC2 番号**：包含"FC2"的番号
- **欧美番号**：格式 `XXX.00.00.00`
- **特定网站**：KIN8、Getchu、Mywife 等
- **无码番号**：通过番号格式识别
- **默认**：有码番号

**结果整合逻辑**：
- 字段级优先级：每个字段独立配置优先级
- 缓存机制：已请求的网站数据缓存
- 数据归约：从多个来源归约到单一结果
- 去重处理：演员、标签等去重

### 3. NFO 生成器 ([mdcx/core/nfo.py](../mdcx/core/nfo.py))

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

**主要方法**：`write_nfo()`、`get_nfo_data()`、`get_external_id_tag_name()`

### 4. TMDB 演员 ([mdcx/core/tmdb_actor.py](../mdcx/core/tmdb_actor.py))

**功能**：通过 TMDB API 查询日本成人演员信息

**主要类**：
- `_TmdbRateLimiter`：令牌桶限流器，3.5 个令牌/秒，突发容量 10 个

**主要方法**：
- `load_actor_db()`：加载演员数据库
- `search_actor_db_reverse()`：反向搜索
- `fetch_actor_tmdb_ids()`：批量查询并缓存 TMDB ID
- `_query_single_actor()`：查询单个演员

**速率限制**：
1. 令牌桶算法：3.5 个/秒，突发容量 10 个
2. 并发限制：Semaphore 限制并发数为 3
3. 请求间隔：每个查询后 0.5 秒延迟

**TMDB 数据流**：
```
演员原名 -> 演员数据库 -> TMDB ID -> TMDB API -> 演员详细信息
```

**详细步骤**：
1. 从 Excel 数据库加载演员信息，支持正向和反向搜索
2. 刮削流程调用 `fetch_actor_tmdb_ids()` 查询缺失的 TMDB ID
3. 调用 TMDB Search API 根据原名和别名匹配
4. 使用 TMDB Person API 获取出生日期、出生地、简介、图片等

**数据缓存**：演员数据库启动时加载到内存；TMDB ID 映射缓存后续直接命中

**错误处理**：网络错误自动重试；API 限流等待令牌桶；查询失败记录日志继续处理；数据缺失使用备用信息

### 5. Amazon 集成 ([mdcx/core/amazon.py](../mdcx/core/amazon.py))

**功能**：Amazon ASIN 获取和高清封面匹配。主要方法：`search_asin()`、`get_hd_poster()`

### 6. 图片处理 ([mdcx/core/image.py](../mdcx/core/image.py))

**功能**：图片下载、裁剪、添加水印。主要方法：`download_file_with_filepath()`、`fix_pic_async()`、`cut_pic()`

### 7. 人脸裁剪 ([mdcx/core/face_crop.py](../mdcx/core/face_crop.py))

**功能**：智能人脸检测和裁剪。主要方法：`detect_faces()`、`crop_face()`

### 8. 翻译系统 ([mdcx/core/translate.py](../mdcx/core/translate.py))

支持 Google、Bing、百度、DeepL、DeepLX、LLM（支持自定义 API）

---

## 数据模型

### 主要数据类 ([mdcx/models/types.py](../mdcx/models/types.py))

**`FileInfo`**：媒体文件基础信息。字段：`number`、`mosaic`、`file_path`、`has_sub`、`definition`、`codec`、`c_word`、`cd_part`、`destroyed`、`leak`

**`CrawlerInput`**：单个爬虫调用输入。字段：`appoint_number`、`appoint_url`、`file_path`、`number`、`mosaic`、`short_number`、`language`、`org_language`

**`CrawlTask`**：继承 `CrawlerInput`，额外字段：`c_word`、`cd_part`、`destroyed`、`has_sub`、`leak`、`website_name`、`wuma`、`youma`

**`BaseCrawlerResult`**：爬虫结果基础类型。字段：`number`、`mosaic`、`image_download`、`actors`、`all_actors`、`directors`、`extrafanart`、`originalplot`、`originaltitle`、`outline`、`poster`、`publisher`、`release`、`runtime`、`score`、`series`、`studio`、`tags`、`thumb`、`title`、`trailer`、`wanted`、`year`

**`CrawlerResult`**：单站结果。额外字段：`source`、`external_id`

**`CrawlersResult`**：整合结果。额外字段：`scraping_type`、`scraping_type_source`、`actor_amazon`、`thumb_list`、`poster_list`、`actor_tmdb_ids`、`site_log`、`field_log`、`field_sources`、`external_ids`

**`OtherInfo`、`ScrapeResult`、`ShowData`**：其他处理信息、刮削结果封装、显示数据

### 数据流转关系

```
FileInfo -> CrawlerInput -> CrawlTask
               |
           CrawlerResult <- CrawlerResponse
               |
           CrawlersResult
               |
           ScrapeResult <- OtherInfo
               |
           ShowData
```

---

## 配置系统

### 配置模型 ([mdcx/config/models.py](../mdcx/config/models.py))

**`Config`**：主配置类，基于 Pydantic

**1. 通用设置**：`media_path`、`softlink_path`、`success_output_folder`、`failed_output_folder`、`media_type`、`sub_type`

**2. 清理设置**：`folders`（排除目录）、`string`（删除字符串）、`file_size`（最小文件大小 MB）、`clean_*`

**3. 刮削设置**：`thread_number`、`thread_time`、`main_mode`、`read_mode`、`update_mode`、`download_files`、`scrape_like`

**4. 网站设置**：`website_youma`、`website_wuma`、`website_suren`、`website_fc2`、`website_oumei`、`website_guochan`、`fixed_scraping_type`

**5. 字段配置**：`field_configs`（优先级/语言/翻译）、`type_field_configs`、`site_configs`

**6. 翻译配置**：`translate_config`（`translate_by`、`baidu_appid`、`baidu_key`、`deepl_key`、`deeplx_url`、`llm_*`）

**7. 命名和格式化**：`nfo_include_new`、`folder_name`、`naming_file`、`naming_media`、`prevent_char`、`fields_rule`、`*_style`

**8. 服务器设置**：`server_type`（emby/jellyfin）、`emby_url`、`api_key`、`user_id`、`emby_on`、`use_database`、`info_database_path`

**9. 水印设置**：`poster_mark`、`thumb_mark`、`fanart_mark`、`mark_size`、`mark_type`、`mark_fixed`、`mark_pos*`

**10. 网络设置**：`use_proxy`、`proxy`、`proxy_sites`、`cf_bypass_*`、`timeout`、`retry`、`theporndb_api_token`、`tmdb_api_key`

**11. 日志设置**：`show_web_log`、`show_from_log`、`show_data_log`、`save_log`

**主要方法**：`get_site_config()`、`get_site_url()`、`get_field_config()`、`get_type_sites()`、`get_type_field_config()`、`set_field_sites()`、`set_field_language()`、`set_field_translate()`

### 配置枚举 ([mdcx/config/enums.py](../mdcx/config/enums.py))

- `Website`：47 个站点枚举（下拉框由已注册的 43 个爬虫动态生成）
- `FixedScrapingType`：`AUTO`、`YOUMA`、`WUMA`、`SUREN`、`FC2`、`OUMEI`、`GUOCHAN`
- 其他：`Language`、`Translator`、`EmbyAction`、`DownloadableFile`、`KeepableFile`、`ReadMode`、`Switch`、`NfoInclude`、`MarkType`

### 配置管理器 ([mdcx/config/manager.py](../mdcx/config/manager.py))

**方法**：`load()`、`save()`、`reset()`、`handle_v1()`、`_replace_config()`（热切换）、`acquire_computed()`

**加载流程**：
1. 检查标记文件确定配置路径
2. 尝试加载配置文件
3. 旧版 .ini 配置自动转换为新版
4. 验证配置
5. 应用配置

---

## 爬虫系统

### 爬虫基类 ([mdcx/crawlers/base/base.py](../mdcx/crawlers/base/base.py))

**`GenericBaseCrawler[T]`**：泛型爬虫基类，所有具体爬虫继承此类并实现抽象方法。

**主要特性**：自定义上下文类型、统一生命周期管理、性能监控、健康监测

**主要方法**：
- `__init__(client, base_url)`：初始化
- `close()`：释放资源
- `site()`：返回网站枚举（抽象）
- `base_url_()`：返回默认 URL（抽象）
- `display_name()`：前端显示名称
- `new_context(input)`：创建上下文（抽象）
- `run(input)`：执行爬虫任务
- `_run(ctx)`：内部执行逻辑
- `_generate_search_url(ctx)`：生成搜索 URL（抽象）
- `_search(ctx, search_urls)`：执行搜索
- `_parse_search_page(ctx, selector, search_url)`：解析搜索页（抽象）
- `_detail(ctx, detail_urls)`：获取详情页
- `_parse_detail_page(ctx, selector, detail_url)`：解析详情页（抽象）
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

- 装饰器模式注册爬虫
- 工厂模式获取爬虫实例
- 懒加载优化性能

### 爬虫实现目录 ([mdcx/crawlers/](../mdcx/crawlers/))

每个网站一个爬虫文件，共 43 个已注册站点（下拉框动态生成）

**添加新爬虫的步骤**：
1. 在 `mdcx/crawlers/` 下创建新文件
2. 继承 `BaseCrawler`（或 `GenericBaseCrawler`）
3. 实现抽象方法
4. 使用 `@register_crawler` 装饰器注册
5. 在 `Website` 枚举中添加对应网站

---

## 工具模块

### 演员数据库 ([mdcx/tools/actress_db.py](../mdcx/tools/actress_db.py))
Excel 格式的演员数据库，支持加载、搜索、更新

### Emby 演员 ([mdcx/tools/emby_actor_info.py](../mdcx/tools/emby_actor_info.py))
更新 Emby/Jellyfin 演员信息。数据来源：Wikipedia（简介、出生日期、出生地）、本地数据库（中文名、别名）

### Emby 演员图片 ([mdcx/tools/emby_actor_image.py](../mdcx/tools/emby_actor_image.py))
更新 Emby/Jellyfin 演员图片。图片来源：graphis.ne.jp、Gfriends 本地仓库/GitHub、本地文件夹

### 其他工具
- `missing.py`：缺失文件检测
- `subtitle.py`：字幕管理
- `wiki.py`：Wikipedia 信息查询

---

## Emby 集成

MDCx 提供与 Emby 和 Jellyfin 的深度集成，自动更新演员信息和图片。

### Emby 演员 ([mdcx/tools/emby_actor_info.py](../mdcx/tools/emby_actor_info.py))

```python
from mdcx.tools.emby_actor_info import EmbyActorInfo
emby_info = EmbyActorInfo()
emby_info.update_actor(actor_id, tmdb_id)
```

**数据来源**：Wikipedia（简介、出生日期、出生地）、本地数据库（中文名、别名）

### Emby 演员图片 ([mdcx/tools/emby_actor_image.py](../mdcx/tools/emby_actor_image.py))

```python
from mdcx.tools.emby_actor_image import EmbyActorImage
emby_image = EmbyActorImage()
emby_image.update_image(actor_id, image_url)
```

**图片来源**：graphis.ne.jp > Gfriends 本地仓库/GitHub > 本地文件夹

### 配置说明

```ini
[emby]
server_type = emby
emby_url = http://localhost:8096
api_key = your_api_key_here
emby_on = actor_info,actor_image
```

### 工作流

1. 从 43 个网站刮削视频元数据，提取演员信息
2. 从 TMDB 获取演员详细信息，从 Wikipedia 获取简介，从本地数据库获取中文名
3. 通过 API 更新 Emby/Jellyfin 演员信息和图片
4. 生成 NFO 文件

---

## 命名系统

### 模块结构 ([mdcx/core/naming/](../mdcx/core/naming/))

```
mdcx/core/naming/
+-- fields.py            # 字段定义和上下文构建
+-- template.py          # 模板引擎
+-- renderer.py          # 命名渲染
+-- sanitize.py          # 名称清理
```

### 支持的字段

| 字段名 | 说明 | 字段名 | 说明 |
|--------|------|--------|------|
| `number` | 番号 | `release` | 发行日期 |
| `title` | 标题 | `year` | 年份 |
| `originaltitle` | 原始标题 | `runtime` | 时长 |
| `actor` | 演员列表 | `mosaic` | 有码/无码 |
| `first_actor` | 首位演员 | `definition` | 清晰度 |
| `all_actor` | 全部演员 | `cnword` | 字幕标识 |
| `letters` | 番号前缀 | `moword` | 版本标识 |
| `first_letter` | 番号首字符 | `filename` | 原文件名 |
| `outline` | 简介 | `wanted` | 想看人数 |
| `director` | 导演 | `score` | 评分 |
| `series` | 系列 | `four_k` | 4K 标识 |
| `studio` | 片商 | | |
| `publisher` | 发行商 | | |

### 模板语法

使用 **Jinja2** 模板引擎：

```jinja2
{{ number }}

{% if number %}{{ number }}{% endif %}

[{% if number %}{{ number }}{% endif %}]{% if title and title != number %}{{ title }}{% endif %}

{% for actor in actors %}{{ actor }}{% if not loop.last %}, {% endif %}{% endfor %}
```

### 常用模板

**目录模板**：`{{ actor }}/{{ number }} {{ actor }}`

**文件模板**：`{{ number }}`

**媒体模板**：`[{% if number %}{{ number }}{% endif %}]{% if title and title != number %}{{ title }}{% endif %}`

### 智能截断

按优先级截断字段以适应最大长度限制。列表字段（演员、导演）按分隔符截断，普通文本直接截断，移除末尾标点和空格。

---

## 项目运行方式

### 入口文件 ([main.py](../main.py))

**启动流程**：
1. 显示运行时常量（平台、版本等）
2. 读取配置中的界面缩放比例，若 >0 则设置 `QT_SCALE_FACTOR` 环境变量
3. 根据 `highdpi_passthrough` 标记设置高 DPI 缩放策略
4. 创建 QApplication 实例
5. 设置应用样式（Fusion）
6. 应用主题配色
7. 加载主窗口 (`MyMAinWindow`)
8. 显示窗口
9. 安装事件过滤器
10. 启动事件循环

**关键代码**：
```python
app = QApplication(sys.argv)
app.setStyle("Fusion")
apply_application_palette(False)

ui = MyMAinWindow()
ui.show()

sys.exit(app.exec())
```

### 命令行工具 ([mdcx/cmd/](../mdcx/cmd/))

- `crawl`：命令行刮削
- `gen_enums`：生成枚举

---

## 依赖关系

### 主要依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| PyQt6 | >=6.0 | UI 框架 |
| httpx | >=0.24 | HTTP 客户端 |
| curl-cffi | >=0.5 | 浏览器指纹伪装 |
| parsel | >=1.8 | HTML 解析 |
| lxml | >=4.9 | XML/HTML 解析 |
| beautifulsoup4 | >=4.12 | HTML 解析 |
| pydantic | >=2.0 | 数据验证 |
| asyncio | - | 异步处理 |
| aiofiles | >=23.0 | 异步文件操作 |
| Pillow | >=9.0 | 图片处理 |
| opencv-python | >=4.8 | 人脸裁剪 |
| av | >=10.0 | 视频处理 |
| Jinja2 | >=3.1 | 模板引擎 |
| openpyxl | >=3.1 | Excel 处理 |

### 网络层

- `httpx.AsyncClient`：主要 HTTP 客户端
- `curl_cffi.AsyncWebClient`：浏览器指纹伪装

特性：连接池管理、请求限流、浏览器指纹伪装、支持 SOCKS 代理

### 数据持久层

- 配置：JSON 格式（V2），INI 格式（V1 已废弃）
- 演员数据库：Excel 格式（.xlsx），使用 openpyxl 读写

### 日志系统

Qt 信号机制，线程安全，UI 更新信号

---

## 技术栈总结

### 核心技术

| 类别 | 技术 |
|------|------|
| UI 框架 | PyQt6 |
| 网络请求 | httpx, curl-cffi |
| HTML 解析 | parsel, lxml, BeautifulSoup4 |
| 数据验证 | Pydantic |
| 异步处理 | asyncio, aiofiles |
| 图片处理 | Pillow, opencv |
| 视频处理 | av |
| 模板引擎 | Jinja2 |
| Excel 处理 | openpyxl |
| 依赖管理 | uv |

### 设计模式

- **MVC 模式**：Model-View-Controller 分层
- **爬虫注册模式**：装饰器 + 工厂模式
- **配置管理模式**：单例 + 热重载
- **观察者模式**：Qt 信号槽
- **策略模式**：字段优先级配置
- **模板方法模式**：爬虫基类定义流程

### 代码统计（约）

| 模块 | 行数 |
|------|------|
| 核心模块 | 10,495 |
| 爬虫实现 | 11,222 |
| 基础模块 | 2,529 |
| 配置系统 | 1,017 |
| 控制器 | 3,376 |
| 视图 | 11,602 |

---

## 扩展开发

### 添加新爬虫

1. 在 `mdcx/crawlers/` 下创建新文件
2. 继承 `BaseCrawler` 或 `GenericBaseCrawler`
3. 实现抽象方法：`site()`、`base_url_()`、`new_context()`、`_generate_search_url()`、`_parse_search_page()`、`_parse_detail_page()`
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
在 `_parse_detail_page` 方法中添加 `ctx.debug()` 输出调试信息。

### Q2: 如何配置代理？
设置 `use_proxy` 和 `proxy`，支持 HTTP/SOCKS 代理。

### Q3: 如何添加自定义 URL？
在网站配置中设置 `custom_url`。

### Q4: 如何处理爬虫失效？
1. 检查网站是否有反爬更新
2. 更新爬虫代码
3. 临时禁用该站点

---

## 附录 A：PyQt6 迁移指南

详细方案请参考：[pyqt6-migration.md](pyqt6-migration.md)

**主要差异**：
- `PyQt5` 包名迁移为 `PyQt6`
- Qt 枚举和 Flag 采用标准 Python `Enum`/`Flag`
- `exec_()` 改为 `exec()`
- `QAction` 从 `QtWidgets` 迁移到 `QtGui`
- Qt6 默认启用高 DPI 缩放

**迁移阶段**：
- 第一阶段：完成 PyQt6 基线迁移，更新依赖和 UI 文件
- 后续阶段：增加主题策略、接入系统主题变化监听

---

## 附录 B：爬虫迁移指南

详细方案请参考：[爬虫迁移](crawler-migration.md)

**迁移目标**：
- 所有刮削源统一为 `GenericBaseCrawler` / `BaseCrawler` 子类
- 通过 `register_crawler()` 注册新版类
- 统一返回 `CrawlerResponse` 和 `CrawlerResult`

**已迁移站点**：
dmm, javdb, javdbapi, javdb_app, avbase, missav, faleno, jav321, cableav, madouqu, mmtv, dahlia, fantastica, avsox, cnmdb, hscangku, kin8, lulubar, xcity, giga, mdtv, mgstage, javday, fc2ppvdb, prestige, fc2club, fc2, fc2hub, javbus, freejavbt, hdouban, iqqtv, airav_cc, getchu, getchu_dmm, mywife, javlibrary, official, theporndb

---

## 许可证

GPLv3

---

## 联系方式

- GitHub: https://github.com/cdlongbow/mdcx