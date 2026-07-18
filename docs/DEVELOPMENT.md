# 开发者专区

给想改代码、加功能的人看的文档。合并了原仓库中所有技术文档（架构、核心模块、数据模型、爬虫系统、命名系统、缓存、测试、代码规范、迁移指南等）。

## 项目结构

```
mdcx/
├── base/              # 基础功能（文件、图片、翻译、网络请求）
├── cmd/               # 命令行工具（crawl 调试爬虫、gen_enums）
├── config/            # 配置管理（Pydantic 模型、枚举、管理器）
├── controllers/       # 控制器（主窗口、海报裁剪）
│   └── main_window/   # 主窗口逻辑（~3400 行）
├── core/              # 核心业务（刮削器、NFO、命名、图片、翻译等）
├── crawlers/          # 45 个网站爬虫 + 基类框架
├── gen/               # 自动生成的枚举
├── models/            # 数据模型（FileInfo、CrawlerResult 等）
├── tools/             # 工具（演员数据库、Emby 同步、字幕等）
├── utils/             # 工具函数（限流、日志、文件操作）
└── views/             # UI 视图（Qt Designer 生成的 .ui 和 .py）
```

## 架构

采用 MVC 分层：

```
UI 层 (PyQt6)         → 界面展示、用户操作
控制器层               → 事件处理、配置管理、信号调度
核心业务层             → 刮削器、NFO 生成、翻译、图片处理
爬虫框架               → 45 个爬虫，统一基类
基础设施层             → HTTP 客户端、文件系统、OpenCV
```

**数据流程**：

1. 文件扫描 → 番号识别 → 爬虫执行 → 数据整合 → 翻译
2. → 命名生成 → 资源下载 → NFO 生成 → 文件移动

## 数据模型

完整数据流转链路：

```
FileInfo → CrawlerInput → CrawlTask
              ↓
          CrawlerResult ← 单个爬虫返回
              ↓
          CrawlersResult ← 多站聚合
              ↓
          ScrapeResult ← 最终刮削结果
              ↓
          ShowData ← 界面展示
```

关键数据类在 `mdcx/models/types.py`：

- **FileInfo**：视频文件信息（番号、路径、分辨率等）
- **CrawlerInput**：爬虫输入参数（番号、语言、指定 URL）
- **CrawlTask**：完整刮削任务，继承 CrawlerInput
- **BaseCrawlerResult**：23 个字段（标题、演员、海报、评分等）
- **CrawlerResult**：单站结果，增加 source 和 external_id
- **CrawlersResult**：多站聚合结果，含字段来源追踪
- **ScrapeResult**：最终结果 = file_info + data + other_info

## 核心模块

### 主刮削器（mdcx/core/scraper.py）

`Scraper` 类统筹整个刮削流程：扫描文件 → 调度爬虫 → 聚合结果 → 翻译 → 下载 → 生成 NFO → 移动文件。使用渐进式任务调度，支持大量文件不溢出。

### 文件爬虫（mdcx/core/file_crawler.py）

`FileScraper` 处理单个文件，负责番号识别、多站并发请求、字段级优先级合并。

### NFO 生成（mdcx/core/nfo.py）

生成 Emby/Jellyfin/Kodi 兼容的 XML NFO 文件，30+ 字段，含外部 ID（javdbid、javlibid 等）。

### TMDB 演员（mdcx/core/tmdb_actor.py）

通过 TMDB API 查询演员信息，日文名/中文名/繁体名多语言搜索。令牌桶限流（3.5 req/s），双层缓存（Excel + 内存）。

### Amazon 集成（mdcx/core/amazon.py）

从 Amazon 搜索高清封面，EAN-13 条码检测 → ASIN 映射。三层搜索策略：条码快路径 → 标题搜索 → 演员兜底。

### 人脸裁剪（mdcx/core/face_crop.py）

基于 OpenCV YuNet ONNX 模型，自动检测人脸并裁剪为 2:3 海报。

### 图片处理（mdcx/core/image.py）

图片下载、多尺寸修复、水印添加（9 宫格位置，支持文字水印）。

### 翻译（mdcx/core/translate.py）

6 个翻译引擎（Google/Bing/Baidu/DeepL/DeepLX/LLM），字段级翻译配置，多引擎降级。

### 命名系统（mdcx/core/naming/）

Jinja2 模板引擎，支持条件渲染、智能截断。三类命名目标：文件夹、文件名、NFO 标题。

命名变量：number、title、actor、all_actor、studio、series、year、release 等 24 个字段。

### 马赛克标准化（mdcx/core/mosaic.py）

`normalize_mosaic()` 将各类标签归一化为：有码、无码、无码破解、流出、无码流出、国产。

## 爬虫框架

### 基类

`GenericBaseCrawler[T]` 在 `mdcx/crawlers/base/base.py` 中定义，泛型抽象基类，所有爬虫继承。

**爬虫生命周期**：
1. `_generate_search_url()` — 生成搜索 URL
2. `_search()` — 请求搜索页
3. `_parse_search_page()` — 解析搜索页，拿详情页 URL
4. `_detail()` — 请求详情页
5. `_parse_detail_page()` — 解析详情页，返回 CrawlerData
6. `post_process()` — 后处理，返回 CrawlerResult

### CrawlerData

爬虫解析的中间数据，所有字段默认 `NOT_SUPPORT`（表示本站不支持此字段）。可选字段包括 title、actors、poster、outline、score、tags、series 等 76 个。

### 注册机制

爬虫通过 `register_crawler()` 注册到 `crawler_registry`，站点下拉框由注册表动态生成。需要在 `mdcx/crawlers/__init__.py` 中导入，并在 `Website` 枚举中添加。

### 添加新爬虫的步骤

1. 在 `mdcx/crawlers/` 下新建 .py 文件
2. 继承 `BaseCrawler` 或 `GenericBaseCrawler`
3. 实现抽象方法：`site()`、`base_url_()`、`new_context()`、`_generate_search_url()`、`_parse_search_page()`、`_parse_detail_page()`
4. 可选重写 `post_process()` 做后处理
5. 在 `mdcx/config/enums.py` 的 `Website` 枚举中加新值
6. 在 `mdcx/crawlers/__init__.py` 中导入并注册

## 缓存系统

### TMDB 缓存

双层缓存：Excel 文件（持久化）+ 内存 dict（加速）。查询策略：先查内存→再查 Excel→再调 TMDB API。限流 3.5 req/s，并发数 3。

### Amazon 缓存

ASIN 数据库（Excel），搜索到的 ASIN 与番号对应关系持久化，避免重复搜索。

## 网络层

- **异步 HTTP**：httpx（默认）+ curl-cffi（指纹伪装）
- **浏览器指纹**：6 种 TLS 指纹（Chrome 124/131/136、Firefox 133/135），按请求类型动态调整，定期轮换
- **限流**：每个域名独立令牌桶，默认 8 req/s，失败自动退避重试
- **Cloudflare Bypass**：内置 cloakbrowser 隐身 Chromium，自动绕过 CF 防护页，无需 license key
- **代理**：HTTP/HTTPS/SOCKS5，可按站点路由

## 配置系统

基于 Pydantic 的 `Config` 模型（200+ 配置项），JSON 格式存储。旧版 INI 格式自动迁移。

`ConfigManager` 单例管理加载/保存/热切换。`Computed` 派生对象（HTTP 客户端、LLM 客户端等）在配置变更时自动重建。

敏感字段（API Key）导出时自动脱敏为 `***`。

## 依赖

从 `pyproject.toml` 读取，核心依赖：
- PyQt6 6.11.0（UI 框架）
- httpx（HTTP 客户端）
- curl-cffi 0.11.4（TLS 指纹模拟）
- lxml + parsel + beautifulsoup4（HTML/XML 解析）
- Pillow + opencv-contrib-python-headless（图片处理）
- Jinja2（命名模板）
- openpyxl（Excel 读写）
- cloakbrowser + CloudflareBypassForScraping（CF 绕过）

## 测试

- **框架**：pytest + pytest-asyncio
- **标记**：`network`（需要联网的测试，默认跳过）、`integration`（集成测试，默认跳过）
- **运行**：
  ```bash
  uv run pytest tests/                          # 全部测试
  uv run pytest tests/ --tb=short -m "not network" -x  # 仅不联网测试
  ```
- **覆盖**：tests/crawlers/ 爬虫测试、tests/core/ 核心测试、NFO 测试、配置测试等
- **推送前自检**：`uv run check --skip-hook-install`（ruff format + ruff check + pytest）

## 代码规范

- **格式化**：ruff（行宽 120，启用 isort/pyupgrade/flake8）
- **类型检查**：pyright（部分文件豁免）、mypy
- **Git 钩子**：pre-commit 安装 ruff check + ruff format
- **检查和修复**：
  ```bash
  uv run ruff check .          # 代码检查
  uv run ruff check . --fix    # 自动修复
  uv run ruff format .         # 格式化
  ```

## 构建

使用 PyInstaller 打包，入口文件 main.py。不推荐自己构建，去 GitHub Releases 下载即可。

## 迁移指南

### 旧版爬虫 → GenericBaseCrawler

旧版函数式刮削器迁移步骤：
1. 创建新文件继承 BaseCrawler
2. 将搜索逻辑移入 `_search()` + `_parse_search_page()`
3. 将详情逻辑移入 `_detail()` + `_parse_detail_page()`
4. 使用 `CrawlerData` 代替手动构造字典
5. 注册到 `crawlers/__init__.py`

### PyQt5 → PyQt6

主要变更：QtCore.pyqtSignal → QtCore.pyqtSignal（相同），枚举使用 Enum 风格，QRegExp → QRegularExpression。

### 配置 v1 (INI) → v2 (JSON)

通过 `migrations.py` 自动转换，旧版 INI 配置在加载时自动迁移为 JSON。

## 支持的命令行

```bash
uv run crawl           # 命令行爬虫调试
uv run gen_enums       # 生成枚举
uv run build           # PyInstaller 打包
uv run bump            # 版本号更新
uv run changelog       # 生成变更日志
```