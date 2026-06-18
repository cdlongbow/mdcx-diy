# 核心模块

> 本文档从 CODE_WIKI.md 提取，详见完整文档

---

## 1. 刮削器核心 ([mdcx/core/scraper.py](../mdcx/core/scraper.py))

**功能**:主刮削器，负责统筹整个刮削流程。用户点"开始"后，所有工作都由它调度。

**主要类**:
- `Scraper`:刮削器主类
  - `run()`:启动刮削
  - `process_one_file()`:处理单个文件
  - `_run_tasks_with_limit()`:渐进式任务调度

**刮削流程**:
1. 获取文件信息
2. 调用爬虫获取数据
3. 翻译元数据
4. 下载图片和预告片
5. 添加水印
6. 生成 NFO
7. 移动和重命名文件
8. 创建软链接(可选)

**关键特性**:
- 渐进式任务调度，支持大量文件
- 并发控制，可配置线程数
- 间歇刮削支持
- 停止/恢复支持

> 简单说：这是整个程序的"总指挥"。你给一批文件，它安排谁先谁后、调爬虫取数据、翻译、下载图片、写 NFO、改名移动，一条龙搞定。

## 2. 文件爬虫 ([mdcx/core/file_crawler.py](../mdcx/core/file_crawler.py))

**功能**:处理单个文件的刮削逻辑。Scraper 把文件交给它，它负责搞定单个文件的所有细节。

**主要类**:
- `ScrapeClassification`:刮削分类结果
- `FileScraper`:文件爬虫

**番号识别规则**:
- **国产番号**:MD 系列、MKY 系列，马赛克标记为"国产"
- **素人番号**:SIRO 系列、短番号
- **FC2 番号**:包含"FC2"的番号
- **欧美番号**:格式 `XXX.00.00.00`
- **特定网站**:KIN8、Getchu、Mywife 等
- **无码番号**:通过番号格式识别
- **默认**:有码番号

**结果整合逻辑**:
- 字段级优先级:每个字段独立配置优先级
- 缓存机制:已请求的网站数据缓存
- 数据归约:从多个来源归约到单一结果
- 去重处理:演员、标签等去重

> 简单说：面对一个视频文件，它先猜出番号类型（国产、素人、FC2 等），然后拿着番号去各个网站抓数据，最后把多个来源的结果合并成一份干净的信息。

## 3. NFO 生成器 ([mdcx/core/nfo.py](../mdcx/core/nfo.py))

**功能**:生成符合 Kodi/Emby 规范的 NFO 文件。NFO 文件就是视频的"身份证"，里面写着标题、简介、演员、封面等信息。

**支持的字段**:
- 基本信息:番号、标题、原始标题、排序标题、剧情简介
- 发行信息:首播日期、发行日期、年份、标语
- 分类信息:家长分级、自定义分级、国家代码
- 人员信息:演员、导演
- 评分信息:公众评分、影评人评分、想看人数
- 分类标签:标签、类型、系列
- 制作信息:制作商、厂牌、发行商、标签
- 媒体资源:海报、封面、预告片 URL
- 外部 ID:各网站的外部 ID(如 javdbid、javlibid 等)

**主要方法**:
- `write_nfo()`:生成 NFO 文件
- `get_nfo_data()`:读取 NFO 文件
- `get_external_id_tag_name()`:生成外部 ID 标签名

> 简单说：刮削完数据后，把信息写成 XML 格式的 NFO 文件。Emby、Kodi 这些媒体服务器靠它来识别视频信息，就像电影附带的说明书。

## 4. TMDB 演员 ([mdcx/core/tmdb_actor.py](../mdcx/core/tmdb_actor.py))

**功能**:通过 TMDB API 查询日本成人演员信息。TMDB（The Movie Database）是一个开放的影视数据库。

**主要类**:
- `_TmdbRateLimiter`:令牌桶限流器
  - 令牌生成速率:3.5 个/秒
  - 突发容量:10 个令牌
  - 请求前先获取令牌

**主要方法**:
- `load_actor_db()`:加载演员数据库
- `search_actor_db_reverse()`:反向搜索演员数据库
- `fetch_actor_tmdb_ids()`:为一组演员查询并缓存 TMDB ID
- `_query_single_actor()`:查询单个演员的 TMDB 信息

**速率限制机制**:
1. **令牌桶算法**:控制 API 请求速率
2. **并发限制**:Semaphore 限制并发数为 3
3. **请求间隔**:每个查询后 sleep 0.5 秒

> 简单说：去 TMDB 网站查演员的资料。因为 API 有访问频率限制，所以用了限流措施，避免请求太快被封。

## 5. Amazon 集成 ([mdcx/core/amazon.py](../mdcx/core/amazon.py))

**功能**:通过 Amazon 查找商品的 ASIN 编号，匹配高清封面图。

**主要方法**:
- `search_asin()`:搜索 ASIN
- `get_hd_poster()`:获取高清海报

> 简单说：去 Amazon 上找同款商品的高清封面图。ASIN 就是 Amazon 的商品编号。

## 6. 图片处理 ([mdcx/core/image.py](../mdcx/core/image.py))

**功能**:图片下载、裁剪、添加水印。

**主要方法**:
- `download_file_with_filepath()`:下载图片到指定路径
- `fix_pic_async()`:异步修复图片
- `cut_pic()`:裁剪图片为 2:3 比例

## 7. 人脸裁剪 ([mdcx/core/face_crop.py](../mdcx/core/face_crop.py))

**功能**:智能检测图片中的人脸并裁剪出来，用于制作演员头像。

**主要方法**:
- `detect_faces()`:检测人脸
- `crop_face()`:裁剪人脸区域

## 8. 翻译系统 ([mdcx/core/translate.py](../mdcx/core/translate.py))

**功能**:支持多种翻译服务，把日文标题和简介翻译成中文等目标语言。

**支持的翻译服务**:
- Google 翻译
- 百度翻译
- DeepL 翻译
- DeepLX 翻译
- LLM 翻译（支持自定义 API）

---

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [数据模型](data-models.md) - 数据结构定义
- [配置系统](configuration.md) - 配置管理详解
- [爬虫系统](crawler-system.md) - 爬虫框架详解
- [工具模块](tools.md) - 工具模块详解
