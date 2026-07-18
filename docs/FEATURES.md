# 功能总览

MDCx 支持的功能全景。只想快速上手的话，先看 [QUICKSTART.md](QUICKSTART.md)。

## 一、刮削系统

### 自动识别番号

从文件名提取番号（如 `ABP-123.mp4` → `ABP-123`），并自动判断类型：

| 类型 | 番号格式 | 例子 |
|------|---------|------|
| 有码 | 英文-数字 | ABP-123、SSIS-456 |
| 无码 | HEYZO-/Carib- 等 | HEYZO-123、Carib-123 |
| FC2 | FC2-PPV-数字 | FC2-PPV-1234567 |
| 国产 | MD-/MKY- 等 | MD-0123 |
| 欧美 | 数字.数字.数字.数字 | 123.45.67.89 |
| 素人 | SIRO- 等 | SIRO-1234 |

### 全部 45 个爬虫

| 爬虫名 | 数据源 | 说明 |
|--------|-------|------|
| dmm | dmm.co.jp | 日本最大成人平台 FANZA |
| dmm_api | JavDB v1 API | DMM 数据走 API |
| javdb | javdb.com | JavDB 综合信息站 |
| javdb_api | JavDB 镜像站 | 镜像站 HTML 直连，带简繁转换和异体字修正 |
| javdb_app | JavDB 移动端 API | APK 逆向签名直连 |
| javbus | javbus.com | 有码/无码分类搜索 |
| jav321 | jav321.com | 综合信息 |
| javlibrary | javlibrary.com | 老牌信息站 |
| missav | missav.ai | 综合搜索 |
| missav_api | Recombee API | 免墙直连，演员字段留空 |
| mgstage | mgstage.com | 有码/素人官网 |
| prestige | prestige-av.com | Prestige 官网 JSON API |
| r18dev | r18.dev | JSON API 直连，番号自动补零 |
| faleno | faleno.jp | Faleno 官网 |
| fantastica | fantastica-av.com | VR 内容 |
| giga | giga.co.jp | Giga 官网 |
| dahlia | dahlia.co.jp | Dahlia 官网（不在前端显示） |
| official | 各官网 | 按番号前缀路由到子爬虫 |
| avbase | av-base.net | 有码信息站 |
| cableav | cableav.video | 综合信息 |
| freejavbt | freejavbt.com | 磁力信息站 |
| hscangku | hsck.net | 综合信息 |
| mmtv | 7mmtv.tv | 无码 |
| mywife | mywife.cc | 综合 |
| getchu | getchu.com | 游戏/视频综合 |
| getchu_dmm | getchu.com | 委托 getchu 执行（不在前端显示） |
| libredmm | libredmm.com | 开源信息站 |
| xcity | xcity.jp | 综合 |
| love6 | love6.net | FC2 类 |
| kin8 | kin8.info | 无码 |
| avsox | avsox.com | 无码 |
| airav_cc | airav.cc | 无码 |
| avsex | avsex.com | 无码 |
| fc2 | fc2.com | FC2 官网 |
| fc2club | fc2club.top | FC2 信息站 |
| fc2hub | fc2hub.com | FC2 信息站 |
| fc2ppvdb | fc2cmadb.com | FC2 PPV 数据库 |
| hdouban | hdouban.com | 国产 |
| cnmdb | cnmdb.tv | 国产 |
| madouqu | madouqu.com | 国产 |
| lulubar | lulubar.net | 国产 |
| iqqtv | iqqtv.com | 国产 |
| mdtv | mdtv.tv | 国产 |
| javday | javday.tv | 国产 |
| theporndb | api.theporndb.net | 欧美 |

> 注意：missav_api、r18dev、javdb_api 这三条是免墙通道，默认没启用，需要去「设置→站点」手动加。

### 多网站结果合并

多个爬虫返回的数据会按字段优先级合并。比如标题优先取 JavBus 的数据，简介优先取 DMM 的数据——每个字段都可以独立配置优先级。

## 二、四种刮削模式

### 1. 正常模式（全新刮削）

从头到尾走一遍：扫描文件 → 刮数据 → 下图片 → 生成 NFO → 重命名 → 移动文件。

适合新下载的视频。

### 2. 整理模式（仅整理文件）

也叫视频模式。只刮番号用于命名，然后重命名和移动视频文件。**不下图片、不生成 NFO**。

适合不想弄海报墙、只想把文件按番号归类的人。

### 3. 更新模式

重新整理已有 NFO 的文件结构，按新的命名规则移动文件。

适合已经刮过、但想调整目录结构的情况。

### 4. 读取模式

四个独立选项自由组合：

| 选项 | 作用 |
|------|------|
| 有 NFO 时更新 | 按更新模式规则整理已有文件 |
| 无 NFO 时刮削 | 对没 NFO 的文件重新联网刮 |
| 重新下载 | 重新下载图片 |
| 更新 NFO | 更新 NFO 内容（如补演员 TMDB ID） |

## 三、NFO 文件生成

生成 Emby/Jellyfin/Kodi 通用的 .nfo 文件，包含 30+ 字段：

- **基本信息**：番号、标题、原始标题、简介、标语
- **发行信息**：发行日期、年份、分级、国家
- **人员**：演员（多语言名称）、导演、演员 TMDB ID
- **评分**：公众评分、影评人评分、想看数
- **分类**：标签、类型、系列
- **制作**：制作商、厂牌、发行商
- **媒体**：海报 URL、缩略图 URL、背景图 URL、预告片 URL
- **外部 ID**：各网站 ID（javdbid、javlibid 等）

## 四、图片处理

### 下载

自动下载海报、缩略图、背景图、额外剧照、预告片视频。

### 人脸裁剪

使用 OpenCV 人脸检测模型，自动检测海报中的人脸位置并裁剪为 2:3 标准比例的海报。

### 水印

支持在图片上添加文字水印，可配置：
- 水印内容（支持多行文本）
- 位置（九宫格任意位置）
- 字体、大小、颜色
- 透明度、旋转角度

### Amazon 高清封面

从 Amazon 搜索高清封面图（1500px 尺寸），支持：
- EAN-13 条码识别 → ASIN 映射
- 三层搜索策略：条码快路径 → 标题搜索 → 演员名称兜底
- ASIN 数据库缓存（Excel 保存，避免重复搜索）

## 五、翻译系统

6 个翻译引擎：

| 引擎 | 是否需要配置 | 说明 |
|------|-------------|------|
| Google | 不需要 | 免费，自动爬取接口 |
| Bing | 不需要 | 免费，国内网络友好 |
| 百度 | 需要 API Key | 需去百度翻译开放平台申请 |
| DeepL | 需要 API Key | 需去 DeepL 官网申请 |
| DeepLX | 需要自建 URL | 自建 DeepL 免费代理 |
| LLM | 需要 API Key/Base URL | 大模型翻译，可自定义 Prompt |

可以配置哪些字段需要翻译（标题、简介、标签等），以及多引擎降级策略（第一个不行就换下一个）。

## 六、演员数据库

以 Excel 文件（`userdata/actor_database.xlsx`）存储演员信息：

- **字段**：ID、日文名、中文名、繁体名、别名、信息链接、TMDB ID
- **自动补全**：通过 TMDB API 查询演员 ID 和多语言名称
- **数据来源**：TMDB、Wikidata、Gfriends、graphis.ne.jp
- **反向查询**：已知中文名找日文名，或反过来

## 七、文件命名系统

使用 Jinja2 模板引擎自定义命名规则，支持条件渲染。

**支持的变量**：番号、标题、演员（第一名/全部）、标签、系列、制作商、发行商、导演、分辨率、编码格式、发行年份、发行日期、片长、评分、CD 序号等。

**三种命名目标**：
1. 文件夹命名（如 `[ABP-123] 标题`）
2. 文件命名（如 `ABP-123.标题.mp4`）
3. NFO 标题（用于 Emby 展示）

## 八、Emby/Jellyfin 集成

- 向 Emby 服务器同步演员信息（简介、头像、元数据）
- 生成 Kodi 兼容的演员 NFO 文件
- 从 Gfriends / graphis.ne.jp / 本地文件夹同步演员头像
- 自动更新演员出生日期、出生地、简介（Wikipedia）

## 九、网络与反爬

- **HTTP 客户端**：curl-cffi 模拟浏览器 TLS 指纹，6 种浏览器画像自动轮换
- **代理**：支持 HTTP/HTTPS/SOCKS5 代理，可指定特定网站走代理
- **Cloudflare 绕过**：内置隐身 Chromium（cloakbrowser）自动绕过 CF 防护页，无需 license key
- **限流**：每个网站独立令牌桶限流，自适应退避重试
- **指纹伪装**：完整 sec-ch-ua、Accept-Language 等请求头，按请求类型动态调整

## 十、实用工具

- **字幕管理**：自动匹配、复制、重命名字幕文件
- **缺失文件检测**：检查媒体库中缺失的文件
- **海报裁剪工具**：图形化裁剪海报，可拖拽选择区域
- **网络连通性检查**：一键测试各网站可不可达
- **命令行刮削**：`uv run crawl` 在终端中调试爬虫