# API 文档

本文档提供 MDCx 核心模块的 API 参考。

## 目录

- [刮削器 API](#刮削器-api)
- [文件爬虫 API](#文件爬虫-api)
- [NFO 生成 API](#nfo-生成-api)
- [TMDB 演员 API](#tmdb-演员-api)
- [配置 API](#配置-api)
- [命名系统 API](#命名系统-api)

---

## 刮削器 API

### `Scraper` 类

主刮削器类，协调整个刮削流程。

#### 方法

##### `__init__(crawler_provider)`

初始化刮削器。

**参数**：
- `crawler_provider`：爬虫提供器实例

##### `run(file_mode, movie_list)`

执行刮削。

**参数**：
- `file_mode`：文件模式
- `movie_list`：电影文件列表

**返回**：None

##### `process_one_file(task)`

处理单个文件的刮削。

**参数**：
- `task`：刮削任务

**返回**：None

##### `_run_tasks_with_limit(movie_list, task_count, thread_number)`

渐进式任务调度，避免一次性创建大量协程。

**参数**：
- `movie_list`：电影文件列表
- `task_count`：任务数量
- `thread_number`：并发数

**返回**：None

---

## 文件爬虫 API

### `FileScraper` 类

文件爬虫类，负责调用各个爬虫获取数据。

#### 方法

##### `__init__(config, crawler_provider)`

初始化文件爬虫。

**参数**：
- `config`：配置实例
- `crawler_provider`：爬虫提供器实例

##### `classify_scrape_task(task_input, config, use_fixed_type)`

识别番号和刮削类型。

**参数**：
- `task_input`：爬虫任务输入
- `config`：配置实例
- `use_fixed_type`：是否使用固定类型

**返回**：`ScrapeClassification` 实例

##### `_call_crawlers(task_input, classification)`

按字段优先级调用多个爬虫。

**参数**：
- `task_input`：爬虫任务输入
- `classification`：刮削分类

**返回**：`CrawlersResult` 实例

##### `run(task_input, file_mode)`

运行文件爬虫。

**参数**：
- `task_input`：爬虫任务输入
- `file_mode`：文件模式

**返回**：`CrawlersResult` 实例

---

## NFO 生成 API

### 函数

#### `write_nfo(file_info, data, nfo_file, output_dir, update)`

生成 NFO 文件。

**参数**：
- `file_info`：`FileInfo` 实例
- `data`：`CrawlersResult` 实例
- `nfo_file`：NFO 文件路径
- `output_dir`：输出目录
- `update`：是否更新模式

**返回**：`bool`，是否成功写入

#### `get_nfo_data(file_path, movie_number)`

读取 NFO 文件并解析。

**参数**：
- `file_path`：文件路径
- `movie_number`：电影番号

**返回**：`(CrawlersResult | None, OtherInfo | None)` 元组

#### `get_external_id_tag_name(site)`

生成外部 ID 的标签名。

**参数**：
- `site`：网站枚举

**返回**：`str`，标签名（如 `javdbid`）

---

## TMDB 演员 API

### 函数

#### `load_actor_db()`

加载演员数据库 xlsx。

**返回**：`dict[str, dict]`，演员数据库

#### `search_actor_db_reverse(query_name)`

反向搜索演员数据库。

**参数**：
- `query_name`：查询名称

**返回**：`dict | None`，演员信息

#### `fetch_actor_tmdb_ids(actors, client)`

批量查询演员的 TMDB ID。

**参数**：
- `actors`：演员名称列表
- `client`：异步 Web 客户端

**返回**：`dict[str, int]`，演员名称到 TMDB ID 的映射

#### `is_japan_place(place)`

判断演员出生地是否为日本地点。

**参数**：
- `place`：出生地字符串

**返回**：`bool`

---

## 配置 API

### `Config` 类

主配置类，包含所有配置项。

#### 方法

##### `get_site_config(site)`

获取指定站点的配置。

**参数**：
- `site`：网站枚举

**返回**：`SiteConfig` 实例

##### `get_site_url(site, default)`

获取指定网站的用户自定义 URL。

**参数**：
- `site`：网站枚举
- `default`：默认 URL

**返回**：`str`，网站 URL

##### `get_field_config(field)`

获取指定字段的配置。

**参数**：
- `field`：字段枚举

**返回**：`FieldConfig` 实例

##### `get_type_sites(scraping_type)`

获取指定刮削类型的网站列表。

**参数**：
- `scraping_type`：刮削类型枚举

**返回**：`list[Website]`

##### `set_field_sites(field, sites)`

设置字段的网站优先级。

**参数**：
- `field`：字段枚举
- `sites`：网站列表或字符串

**返回**：None

##### `set_field_language(field, language)`

设置字段的语言偏好。

**参数**：
- `field`：字段枚举
- `language`：语言枚举

**返回**：None

##### `set_field_translate(field, translate)`

设置字段是否翻译。

**参数**：
- `field`：字段枚举
- `translate`：是否翻译

**返回**：None

### `ConfigManager` 类

配置管理器，管理配置的加载、保存、迁移等。

#### 方法

##### `load()`

加载配置文件。

**返回**：`list[str]`，错误/警告信息列表

##### `save()`

保存配置到文件。

**返回**：None

##### `reset()`

重置为默认配置。

**返回**：None

##### `handle_v1()`

处理旧版配置文件。

**返回**：`list[str]`，错误/警告信息列表

##### `acquire_computed()`

获取计算属性租约。

**返回**：`ComputedLease` 实例

##### `list_configs()`

列出配置文件夹中的所有配置文件名。

**返回**：`list[str]`

---

## 命名系统 API

### 函数

#### `render_name(template, file_info, data, options)`

渲染名称。

**参数**：
- `template`：模板字符串
- `file_info`：`FileInfo` 实例
- `data`：`CrawlersResult` 实例
- `options`：`NameRenderOptions` 实例

**返回**：`NameRenderResult` 实例

#### `sanitize_name(text, allow_path_separator)`

清理名称以适应文件系统。

**参数**：
- `text`：待清理的文本
- `allow_path_separator`：是否允许路径分隔符

**返回**：`str`，清理后的名称

#### `collect_template_fields(template)`

从模板中收集所有使用的字段。

**参数**：
- `template`：模板字符串

**返回**：`set[str]`，字段集合

### `NameRenderOptions` 类

命名渲染选项。

**属性**：
- `target`：`NamingTarget` 枚举，目标类型
- `show_definition_suffix`：`bool`，是否显示清晰度后缀
- `show_cnword_suffix`：`bool`，是否显示字幕后缀
- `show_moword_suffix`：`bool`，是否显示马赛克后缀
- `max_length`：`int | None`，最大长度

### `NameRenderResult` 类

命名渲染结果。

**属性**：
- `text`：`str`，最终渲染文本
- `template`：`str`，使用的模板
- `context`：`NamingContext`，上下文数据
- `truncated_fields`：`list[str]`，被截断的字段

**方法**：
- `value(field)`：获取字段值

---

## 相关文档

- [核心模块](core-modules.md) - 核心模块详细说明
- [数据模型](data-models.md) - 数据模型详细说明
- [配置系统](configuration.md) - 配置系统详细说明
- [命名系统](naming-system.md) - 命名系统详细说明