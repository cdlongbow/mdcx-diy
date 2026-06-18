# 数据模型

> 本文档从 CODE_WIKI.md 提取，详见完整文档

---

## 主要数据类 ([mdcx/models/types.py](../mdcx/models/types.py))

下面列出了程序中使用的核心数据结构。这些类就像"表格模板"，定义了程序内部传递数据的格式。

### `FileInfo`

媒体文件的基础信息。扫描到一个视频文件时，先提取这些基本信息。

**主要字段**:
- `number`:番号
- `mosaic`:马赛克类型
- `file_path`:文件路径
- `has_sub`:是否有字幕
- `definition`:分辨率
- `codec`:编码格式
- `c_word`:C 字
- `cd_part`:CD 部分
- `destroyed`:是否破解
- `leak`:是否流出

**主要方法**:
- `crawler_input()`:转换为爬虫输入
- `crawl_task()`:转换为刮削任务
- `empty()`:创建空实例

### `CrawlerInput`

传给单个爬虫的输入参数。告诉爬虫要查什么番号、用什么语言。

**主要字段**:
- `appoint_number`:指定番号
- `appoint_url`:指定 URL
- `file_path`:文件路径
- `number`:番号
- `mosaic`:马赛克类型
- `short_number`:短番号
- `language`:语言
- `org_language`:原始语言

### `CrawlTask`

单个文件的完整刮削任务。它继承了 `CrawlerInput` 的所有字段，再加上文件相关的额外信息。可以理解为"带更多上下文版本的爬虫输入"。

**额外字段**:
- `c_word`:C 字
- `cd_part`:CD 部分
- `destroyed`:是否破解
- `has_sub`:是否有字幕
- `leak`:是否流出
- `website_name`:网站名称
- `wuma`:是否无码
- `youma`:是否有码

### `BaseCrawlerResult`

爬虫取回数据后的基础结果类型。所有爬虫返回的数据都基于这个结构。

**主要字段**:
- `number`:番号
- `mosaic`:马赛克类型
- `image_download`:是否需要下载图片
- `actors`:演员列表
- `all_actors`:所有演员列表
- `directors`:导演列表
- `extrafanart`:额外剧照 URL 列表
- `originalplot`:原始简介(日文)
- `originaltitle`:原始标题(日文)
- `outline`:简介
- `poster`:海报 URL
- `publisher`:发行商
- `release`:发行日期
- `runtime`:片长(分钟)
- `score`:评分
- `series`:系列
- `studio`:制作商
- `tags`:标签列表
- `thumb`:缩略图 URL
- `title`:标题
- `trailer`:预告片 URL
- `wanted`:想看数
- `year`:发行年份

### `CrawlerResult`

单个爬虫返回的结果。在 `BaseCrawlerResult` 基础上增加了来源标识。

**额外字段**:
- `source`:数据来源(爬虫名称)
- `external_id`:外部 ID

### `CrawlersResult`

整合所有爬虫结果后的最终数据。一个文件可能被多个爬虫查了，这个类负责把结果汇总到一起。

**额外字段**:
- `scraping_type`:刮削类型
- `scraping_type_source`:分类来源
- `actor_amazon`:用于 Amazon 搜索的演员名称
- `thumb_list`:所有来源的缩略图 URL 列表
- `poster_list`:所有来源的海报 URL 列表
- `actor_tmdb_ids`:演员原名→TMDB ID 映射
- `site_log`:网站日志
- `field_log`:字段来源信息
- `field_sources`:字段来源
- `external_ids`:各来源的 externalId

### `OtherInfo`

其他处理信息，比如文件移动后的新路径、水印处理结果等。

### `ScrapeResult`

整个刮削过程的最终结果封装。包含了刮削数据和其它处理信息。

### `ShowData`

最终展示给用户的数据。

## 数据流转关系

数据在程序中的传递路径如下：

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

> 简单说：数据从头到尾经过以下变换：文件信息 → 爬虫输入 → 爬虫任务 → 单个爬虫结果 → 汇总结果 → 最终刮削结果 → 展示数据。每经过一步，数据就更完整、更接近用户最终看到的样子。

---

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [配置系统](configuration.md) - 配置管理详解
- [爬虫系统](crawler-system.md) - 爬虫框架详解
