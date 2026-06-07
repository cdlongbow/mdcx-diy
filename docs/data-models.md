# 数据模型

> 本文档从 CODE_WIKI.md 提取,详见完整文档

---

## 主要数据类 ([mdcx/models/types.py](mdcx/models/types.py))

### `FileInfo`

媒体文件基础信息

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

单个爬虫调用输入

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

单个文件刮削任务,继承自 `CrawlerInput`

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

爬虫结果基础类型

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

单一网站爬虫结果

**额外字段**:
- `source`:数据来源(爬虫名称)
- `external_id`:外部 ID

### `CrawlersResult`

整合所有网站的结果

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

其他处理信息(文件移动、水印等)

### `ScrapeResult`

刮削结果封装

### `ShowData`

显示数据

## 数据流转关系

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

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [配置系统](configuration.md) - 配置管理详解
- [爬虫系统](crawler-system.md) - 爬虫框架详解