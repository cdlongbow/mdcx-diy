# Requirements Document

## Introduction

基于 javdbapi Go SDK 的核心逻辑，为 MDCx 新增一个名为 `JavdbApiCrawler` 的 Python 刮削源。该刮削源通过直接抓取 JAVDB 网站 HTML 页面获取影片元数据，复用 javdbapi 的 URL 构建、演员名规范化、限流重试和页面解析架构，但使用 Python 技术栈（parsel/lxml）实现。

## Glossary

- **JavdbApiCrawler**: 新增的刮削源类，对应 Website.JAVDB_API
- **演员名规范化**: 将简体/繁体/日文异体字的演员名统一为 JAVDB 可识别的搜索关键字
- **三级匹配**: 精确匹配 > 包含匹配 > 字符重叠匹配的逐级降级策略
- **令牌桶限流器**: 基于 `asyncio.Semaphore` 或 `time.monotonic` 实现请求间隔控制
- **指数退避重试**: 429/502/503/504 等可重试状态码下的自动重试机制

## Requirements

### R1: 搜索影片

**User Story:** AS 用户, I want 通过番号在 JAVDB 搜索影片, so that 能定位到对应的详情页

#### Acceptance Criteria

1. WHEN 用户输入番号（如 `DLDSS-271`）, JavdbApiCrawler SHALL 构造 `{base_url}/search?q={number}&f=all&locale=zh` 搜索 URL
2. WHEN 搜索页返回结果列表, JavdbApiCrawler SHALL 解析列表中的每个影片项，提取详情页链接
3. WHEN 搜索结果中存在番号精确匹配项, JavdbApiCrawler SHALL 选择该匹配项进入详情页
4. IF 无精确匹配, JavdbApiCrawler SHALL 执行模糊匹配（去除分隔符后比较）
5. IF 搜索页被 Cloudflare 拦截, JavdbApiCrawler SHALL 抛出 CrawlerException 并提示用户更换 cookie
6. IF 搜索页因版权限制禁止访问, JavdbApiCrawler SHALL 提示用户更换代理

### R2: 解析详情页

**User Story:** AS 用户, I want 从 JAVDB 详情页获取完整的影片元数据, so that 能填入 NFO 文件

#### Acceptance Criteria

1. WHEN 访问详情页成功, JavdbApiCrawler SHALL 解析以下字段：
   - 番号（`number`）：从 `data-clipboard-text` 属性或面板文本中提取
   - 标题（`title`）：`.current-title` 元素文本
   - 原标题（`originaltitle`）：`.origin-title` 元素文本
   - 演员列表（`actors`）：女性演员名列表
   - 全演员列表（`all_actors`）：所有演员名列表
   - 片商（`studio`）："片商:" / "Maker:" 标签后的值
   - 发行商（`publisher`）："發行:" / "Publisher:" 标签后的值
   - 时长（`runtime`）："時長:" / "Duration:" 标签后的数值（不含单位）
   - 系列（`series`）："系列:" / "Series:" 标签后的值
   - 发行日期（`release`）："日期:" / "Released Date:" 标签后的值
   - 年份（`year`）：从发行日期中提取的 4 位年份
   - 类别标签（`tags`）："類別:" / "Tags:" 标签后的所有标签
   - 封面图（`thumb`）：`.video-cover` 的 `src` 属性
   - 海报图（`poster`）：thumb 的 `/covers/` 替换为 `/thumbs/`
   - 预览图列表（`extrafanart`）：`.preview-images .tile-item` 的 `href` 属性
   - 预告片（`trailer`）：`#preview-video source` 的 `src` 属性
   - 导演（`directors`）："導演:" / "Director:" 标签后的值
   - 评分（`score`）：评分文本中的数值
   - 想看人数（`wanted`）："人想看" / "want to watch" 前的数值
2. IF 详情页被 Cloudflare 拦截, JavdbApiCrawler SHALL 抛出明确异常
3. IF 详情页缺少番号或标题, JavdbApiCrawler SHALL 抛出解析异常

### R3: 演员名规范化

**User Story:** AS 用户, I want 输入中文演员名自动匹配到 JAVDB 演员 ID, so that 不需要手动查找演员 ID

#### Acceptance Criteria

1. WHEN 用户输入简体中文演员名, JavdbApiCrawler SHALL 将其转换为繁体中文后再搜索
2. WHEN 演员名包含日文异体字（如筱/篠、穗/穂、户/戸）, JavdbApiCrawler SHALL 进行异体字修正
3. WHEN 搜索结果返回演员列表, JavdbApiCrawler SHALL 按三级优先级匹配：
   - 第一级：演员名精确匹配
   - 第二级：演员名包含匹配
   - 第三级：字符重叠匹配
4. WHEN 演员详情页包含别名, JavdbApiCrawler SHALL 提取 `title` 属性中的别名列表
5. IF 演员搜索页面为空, JavdbApiCrawler SHALL 返回空结果而非抛出异常

### R4: 限流与重试

**User Story:** AS 系统, I want 控制请求频率并自动重试失败请求, so that 避免被封禁

#### Acceptance Criteria

1. WHEN 每次请求前, JavdbApiCrawler SHALL 等待令牌桶限流器放行（默认每秒 1 个请求）
2. WHEN 收到 HTTP 429 状态码, JavdbApiCrawler SHALL 等待 `Retry-After` 头指定时间后重试
3. WHEN 收到 HTTP 502/503/504 状态码, JavdbApiCrawler SHALL 以指数退避策略重试（默认 3 次）
4. WHEN 重试次数耗尽, JavdbApiCrawler SHALL 抛出 CrawlerException 并包含最后一次错误信息
5. IF 请求超时或网络错误, JavdbApiCrawler SHALL 按重试策略自动重试

### R5: 番号解析

**User Story:** AS 用户, I want 输入番号自动解析到 JAVDB 内部视频 ID, so that 能直接访问详情页

#### Acceptance Criteria

1. WHEN 番号符合 `字母+数字` 格式且是已知的内部 ID, JavdbApiCrawler SHALL 直接构造详情页 URL
2. WHEN 番号不是内部 ID（如 `DLDSS-271`）, JavdbApiCrawler SHALL 通过搜索解析到内部 ID
3. WHEN 番号包含日期格式（如 `XXX-21.06.11`）, JavdbApiCrawler SHALL 自动转换为 `XXX-20210611`

### R6: 后处理

**User Story:** AS 用户, I want 刮削结果经过自动修正, so that 数据更准确

#### Acceptance Criteria

1. WHEN 原标题为空, JavdbApiCrawler SHALL 使用标题作为原标题
2. WHEN 封面图 URL 以 `//` 开头, JavdbApiCrawler SHALL 补全 `https:` 前缀
3. WHEN 标题包含"無碼"、"無修正"、"Uncensored"等关键词, JavdbApiCrawler SHALL 设置马赛克类型为"无码"
4. WHEN 标题不包含无码关键词, JavdbApiCrawler SHALL 设置马赛克类型为"有码"

### R7: 注册与配置

**User Story:** AS 系统, I want 将新刮削源注册到爬虫工厂, so that 可在 UI 中选择使用

#### Acceptance Criteria

1. WHEN 系统启动, JavdbApiCrawler SHALL 通过 `register_crawler` 注册到爬虫工厂
2. WHEN 用户查看刮削源列表, JavdbApiCrawler SHALL 在 Website 枚举中显示为 `JAVDB_API = "javdb_api"`
3. WHEN 用户配置刮削源, JavdbApiCrawler SHALL 支持通过 `get_site_url` 配置 base URL
4. WHEN 用户配置 cookie, JavdbApiCrawler SHALL 从 `manager.config.javdb` 读取并注入请求头