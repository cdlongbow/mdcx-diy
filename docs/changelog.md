# Changelog

## Unreleased

### 新增功能

- **Minnano-av 演员信息刮削源**
  - 新增 `minnano_crawler.py` 模块，支持从 みんなのAV 网站抓取演员信息
  - 支持中文→日文演员名映射（通过 `actor_database.xlsx` 查找日文原名后再搜索）
  - 实现模糊搜索匹配策略：精确匹配优先，其次多字符公共子串匹配，最后五十音回退搜索
  - 中文汉字→假名映射：当中文名含汉字、目标名主要为假名时，匹配共同汉字

- **Emby 演员信息增强**
  - 在 Wikipedia 之前优先查询 Minnano-av 数据源，补充 Emby 演员元数据
  - Minnano-av 缓存文件 `minnano_cache.xlsx` 集成，避免重复请求
  - 缓存表头冻结、数据行全边框、URL 超链接，便于用户手动审查

- **CI/CD 工程质量**
  - CI 流水线增加 ruff format + ruff check 自动校验
  - 提交前必须通过 lint 和格式化检查

## v1.0.0 (2026-06-11)

MDCx-DIY 首个正式发布版，基于Hazard804改良的mdcx项目制作，对前辈表示衷心感谢！！！

### 刮削引擎

- 40+ 网站爬虫（有码/无码/FC2/国产/欧美）
- 新增 libredmm 刮削源
- GenericBaseCrawler 统一框架 + 上下文隔离
- 智能番号识别与自动分类（用户预定义）
- 异步并发架构（asyncio + 渐进式任务调度）
- curl-cffi 浏览器指纹伪装

### TMDB 演员

- 新增 NFO 女优 TMDB ID 功能
- NFO 女优 TMDB ID 写入（需在 NFO 设置勾选 + 填入 API Key）
- 日文原名搜索，日本出生地 + 女性/未指定性别 + 精确名匹配过滤
- 多候选按 popularity 排序取最优，失败不阻塞刮削
- 令牌桶限流器（3.5 req/s，突发 10），并发 3 查询
- TMDB adult 候选自动跳过，搜索候选数优化为 5
- actor_database.xlsx用于nfo增加tmdbid和演员映射功能，反向搜索 + 增量写入，已预置 3985 条女优数据，后续随软件使用动态更新（新演员若TMDB有数据就在表中追加数据，表中演员若TMDB数据更新，表中相关数据会追加）
- 超链接一致性校验与自动修复

### Amazon 高清封面

- ASIN 条码识别 + 三层搜索策略
- 封面 poster 固定 1500 尺寸（平衡质量和大小）
- 新增Amazon ASIN 缓存功能，通过Excel 缓存（amazon_asin_database.xlsx）
- 缓存去重逻辑，保护高置信度数据
- ASIN 缓存Excel随软件使用动态追加（同个影片二次刮削时不用再去Amazon查找，直接用表中数据下载高清封面）

### 数据源迁移

- actor_mapping XML + TMDB 缓存合并为 actor_database.xlsx
- mapping_info.xml 迁移为 info_database.xlsx
- 内置 xlsx 数据库，支持表头冻结，筛选、超链接等，用户可自行编辑或通过超链接审查数据

### 代理与网络

- HTTP/SOCKS5 代理配置
- 新增"不使用代理"网站选择器：40+ 刮削源下拉快速选择，智能域名匹配
- 默认 api.tmdb.org 不走代理

### 元数据与媒体

- NFO 生成器，30+ 字段，兼容 Kodi/Emby/Jellyfin
- 多语言翻译（Google/百度/DeepL/DeepLX/LLM 五引擎）
- Jinja2 命名模板引擎
- OpenCV 人脸检测智能裁剪
- 海报/背景图/预告片自动获取
- 字幕管理与缺失检测
- Emby/Jellyfin 演员信息补全 + 头像同步

### 界面与工具

- PyQt6 桌面图形界面
- 命令行工具（crawl、gen_enums）
- 构建工具链（build、bump、changelog、check）

### 修复

### 工程质量

- 70+ 个测试文件覆盖核心模块
- CI：ruff format + ruff check
- Release：macOS DMG + Windows EXE
- 新增29 篇技术文档（架构、模块、API、迁移指南等）
