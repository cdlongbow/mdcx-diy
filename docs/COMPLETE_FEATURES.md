# 完整功能列表

本文档提供 MDCx 所有功能的完整列表，确保每个功能都有详细说明。

## 📋 目录

1. [智能刮削系统](#智能刮削系统)
2. [完整网站列表](#完整网站列表)
3. [元数据管理](#元数据管理)
4. [图片处理](#图片处理)
5. [多语言翻译](#多语言翻译)
6. [文件和命名系统](#文件和命名系统)
7. [演员数据库管理](#演员数据库管理)
8. [Emby/Jellyfin 集成](#embyjellyfin-集成)
9. [Amazon 集成](#amazon-集成)
10. [网络功能](#网络功能)
11. [工具函数](#工具函数)
12. [实用工具](#实用工具)
13. [高级功能](#高级功能)

---

## 智能刮削系统

### 核心功能

#### 1. 番号自动识别

**支持识别的番号类型**

| 番号类型 | 格式示例 | 标记 |
|---------|---------|------|
| **有码** | ABP-123, SSIS-456 | 有码 |
| **国产** | MD-0123, MKY-0045 | 国产 |
| **素人** | SIRO-1234, 300MAAN-001 | 素人 |
| **FC2** | FC2-PPV-1234567 | FC2 |
| **欧美** | 123.45.67.89 | 欧美 |
| **KIN8** | KIN8-123 | 无码 |
| **Getchu** | getchu-12345 | 其他 |
| **MyWife** | mywife-123 | 其他 |
| **无码** | HEYZO-123, Carib-123 | 无码 |

#### 2. 马赛克类型判断

使用 `mosaic.py` 中的 `normalize_mosaic()` 函数将马赛克标签归一化为稳定值：`有码`、`无码`、`无码破解`、`流出`、`无码流出`、`国产`。额外提供 `is_censored_mosaic()`、`is_plain_uncensored_mosaic()`、`is_guochan_mosaic()` 等谓词函数供调用方分类。

#### 3. 标签优先级系统

从 `info_database.xlsx` 提取优先级标签名称，范围从 `M女`（优先级起始标记）到指定终止标记。`prioritize_nfo_tags()` 将标签重排为：优先级标签（随机打乱）→ 系列标签 → 其他标签。

#### 4. 网络检查功能

检查项包括网络连接、DNS 解析、HTTP/HTTPS 连接、代理连接、网站可达性。实现在 `mdcx/core/network_check.py`。

---

## 完整网站列表

### 有码类 (21 个)

| 网站爬虫 | 网站名称 | 说明 |
|---------|---------|------|
| `dmm_new` | DMM | 日本最大成人视频网站 |
| `mgstage` | MGStage | MGStage 官方网站 |
| `prestige` | Prestige | Prestige 官方网站 |
| `official` | Official | 官方网站 |
| `javbus` | JavBus | JavBus 番号搜索 |
| `jav321` | Jav321 | Jav321 番号搜索 |
| `javdb_new` | JavDB | JavDB 番号数据库 |
| `javdbapi` | JavDB API | JavDB API 接口 |
| `javlibrary` | JavLibrary | JavLibrary 番号搜索 |
| `javday` | JavDay | JavDay 信息站 |
| `missav` | MissAV | MissAV 番号搜索 |
| `mmtv` | MMTV | MMTV 媒体 |
| `mywife` | MyWife | MyWife 官方网站 |
| `getchu` | Getchu | Getchu 官方网站 |
| `getchu_dmm` | Getchu DMM | Getchu DMM 分站 |
| `giga` | Giga | Giga 官方网站 |
| `faleno` | Faleno | Faleno 官方网站 |
| `fantastica` | Fantastica | Fantastica 官方网站 |
| `dahlia` | Dahlia | Dahlia 官方网站 |
| `xcity` | XCity | XCity 信息站 |
| `libredmm` | LibreDMM | LibreDMM 开源项目 |

### 无码类 (3 个)

| 网站爬虫 | 网站名称 | 说明 |
|---------|---------|------|
| `avsox` | AVSoX | AVSoX 信息站 |
| `kin8` | KIN8 | KIN8 无码 |
| `javdb_app` | JavDB APP | JavDB 移动端 API |

### FC2 类 (5 个)

| 网站爬虫 | 网站名称 | 说明 |
|---------|---------|------|
| `fc2` | FC2 | FC2 官方网站 |
| `fc2club` | FC2Club | FC2Club 信息站 |
| `fc2hub` | FC2Hub | FC2Hub 信息站 |
| `fc2ppvdb` | FC2PPVDB | FC2 PPV 数据库 |
| `javdb_app` | JavDB APP | JavDB 移动端 API |

### 国产类 (4 个)

| 网站爬虫 | 网站名称 | 说明 |
|---------|---------|------|
| `hdouban` | HDOUBAN | 豆瓣 HD |
| `cnmdb` | CNMDB | 中国番号库 |
| `madouqu` | 码豆区 | 码豆区 |
| `lulubar` | 咕噜吧 | 咕噜吧 |

### 欧美类 (2 个)

| 网站爬虫 | 网站名称 | 说明 |
|---------|---------|------|
| `theporndb` | ThePornDB | 欧美数据库 |
| `javdb_app` | JavDB APP | JavDB 移动端 API |

### 其他类 (7 个)

| 网站爬虫 | 网站名称 | 说明 |
|---------|---------|------|
| `airav_cc` | AIRAV | Airav 信息站 |
| `cableav` | CableAV | CableAV 信息站 |
| `freejavbt` | FreejavBT | FreejavBT 磁力站 |
| `hscangku` | HS仓库 | HS仓库 |
| `iqqtv` | IQQTV | IQQTV |
| `mdtv` | MDTV | MDTV |
| `avbase_new` | AVBase | AVBase |

**总计：40 个网站爬虫**

---

## 元数据管理

### NFO 生成器

**支持的所有字段**

#### 基本信息字段

| 字段名 | NFO 标签 | 说明 | 示例 |
|--------|---------|------|------|
| 番号 | `id` | 唯一标识符 | ABP-123 |
| 标题 | `title` | 标题 | 标题名称 |
| 原始标题 | `originaltitle` | 原始标题 | Original Title |
| 排序标题 | `sorttitle` | 排序标题 | Sort Title |
| 剧情简介 | `plot` | 剧情简介 | 剧情简介内容 |
| 标语 | `tagline` | 标语 | 标语文本 |

#### 发行信息字段

| 字段名 | NFO 标签 | 说明 | 示例 |
|--------|---------|------|------|
| 首播日期 | `premiered` | 首播日期 | 2024-01-01 |
| 发行日期 | `releasedate` | 发行日期 | 2024-01-15 |
| 年份 | `year` | 年份 | 2024 |
| 家长分级 | `mpaa` | 家长分级 | R-18+ |
| 自定义分级 | `customrating` | 自定义分级 | 18+ |
| 国家代码 | `country` | 国家代码 | JP |

#### 人员信息字段

| 字段名 | NFO 标签 | 说明 | 多语言 |
|--------|---------|------|--------|
| 演员 | `actor` | 演员 | ✅ |
| 导演 | `director` | 导演 | ✅ |

**演员信息结构**
```xml
<actor>
  <name>演员名称</name>
  <type>Actor</type>
  <thumb>图片URL</thumb>
  <profile>个人资料URL</profile>
</actor>
```

#### 评分信息字段

| 字段名 | NFO 标签 | 说明 | 示例 |
|--------|---------|------|------|
| 公众评分 | `rating` | 公众评分 | 8.5 |
| 影评人评分 | `criticsrating` | 影评人评分 | 9.0 |
| 想看人数 | `votes` | 想看人数 | 1000 |

#### 分类标签字段

| 字段名 | NFO 标签 | 说明 | 示例 |
|--------|---------|------|------|
| 标签 | `tag` | 标签 | 标签1,标签2 |
| 类型 | `genre` | 类型 | 类型1,类型2 |
| 系列 | `set` | 系列 | 系列名称 |

#### 制作信息字段

| 字段名 | NFO 标签 | 说明 | 示例 |
|--------|---------|------|------|
| 制作商 | `studio` | 制作商 | 制作商名称 |
| 厂牌 | `label` | 厂牌 | 厂牌名称 |
| 发行商 | `publisher` | 发行商 | 发行商名称 |
| 标签 | `tag` | 标签 | 标签1,标签2 |

#### 媒体资源字段

| 字段名 | NFO 标签 | 说明 | 示例 |
|--------|---------|------|------|
| 海报 | `thumb` | 海报URL | http://.../poster.jpg |
| 缩略图 | `fanart` | 缩略图URL | http://.../thumb.jpg |
| 背景图 | `fanart` | 背景图URL | http://.../fanart.jpg |
| 预告片 | `trailer` | 预告片URL | http://.../trailer.mp4 |

#### 外部 ID 字段

| 字段名 | NFO 标签 | 说明 | 示例 |
|--------|---------|------|------|
| javdbid | `uniqueid type="javdb"` | JavDB ID | javdb123 |
| javlibid | `uniqueid type="javlib"` | JavLibrary ID | javlib456 |
| tmdbid | `actor/tmdbid` | 演员 TMDB ID | 789 |

---

## 图片处理

### 图片下载功能

**支持的图片类型**

| 图片类型 | 说明 | 用途 | 尺寸 |
|---------|------|------|------|
| 海报 (poster) | 主封面 | 列表显示 | 可配置 |
| 缩略图 (thumb) | 缩略图 | 快速预览 | 可配置 |
| 背景图 (fanart) | 背景图 | 详情页背景 | 可配置 |
| 预告片 (trailer) | 预告片 | 预览视频 | - |

### 人脸检测和裁剪

**功能说明**
- 使用 OpenCV 进行人脸检测
- 智能识别人脸位置
- 自动调整裁剪区域
- 保持人脸在中心位置

**裁剪选项**
- 📐 2:3 比例标准海报
- 👤 人脸居中
- 🎯 自定义裁剪区域
- 💧 保留水印选项

**代码实现** (face_crop.py)
```python
def detect_and_crop(image_path: str, output_path: str) -> str:
    """使用 OpenCV YuNet 模型检测人脸并裁剪为 2:3 比例海报。"""
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    scale = min(YUNET_DETECT_MAX_SIDE / max(h, w), 1.0)
    if scale < 1:
        img = cv2.resize(img, None, fx=scale, fy=scale)

    model = cv2.FaceDetectorYN.create(YUNET_MODEL_PATH, "", (img.shape[1], img.shape[0]))
    _, faces = model.detect(img)
    if faces is not None:
        face = faces[0]
        # 放大包围盒、扩展到 2:3 比例、裁剪
        ...
```

### 水印添加功能

**水印选项**
- ✏️ 自定义水印文本
- 📍 自定义水印位置（9宫格）
- 🎨 字体配置（字体、大小、颜色）
- 💧 透明度设置
- 🔄 旋转角度

**水印位置**
```
[左上]   [上]   [右上]
[左]    [中心]  [右]
[左下]   [下]   [右下]
```

---

## 多语言翻译

### 翻译引擎详解

#### 1. Google 翻译

**配置要求**
- 无需 API Key
- 或配置 Google Cloud Translation API Key

**支持语言**
- 中文（简体/繁体）
- 日语
- 英语
- 100+ 种语言

**配置示例**
```json
{
  "engine": "google",
  "api_key": "",
  "target_lang": "zh-CN"
}
```

#### 2. 百度翻译

**配置要求**
- 需要 API Key
- 需要应用 ID

**配置示例**
```json
{
  "engine": "baidu",
  "app_id": "your_app_id",
  "secret_key": "your_secret_key"
}
```

#### 3. DeepL 翻译

**配置要求**
- 需要 API Key
- 推荐 DeepL API Pro

**支持语言**
- 中文（简体/繁体）
- 日语
- 英语
- 30+ 种语言

**配置示例**
```json
{
  "engine": "deepl",
  "api_key": "your_api_key"
}
```

#### 4. DeepLX 翻译

**特点**
- 开源的 DeepL 翻译接口
- 免费（需要自建服务）

**配置示例**
```json
{
  "engine": "deeplx",
  "api_url": "http://localhost:1188/translate"
}
```

#### 5. LLM 翻译

**支持的 LLM 服务**
- OpenAI (GPT-3.5/GPT-4)
- 通义千问
- 文心一言
- Claude
- 自定义 LLM API

**配置示例**
```json
{
  "engine": "llm",
  "provider": "openai",
  "api_key": "your_api_key",
  "model": "gpt-3.5-turbo",
  "base_url": "https://api.openai.com/v1"
}
```

### 翻译字段配置

**可翻译的字段**

| 字段 | 默认翻译 | 说明 |
|------|---------|------|
| 标题 | ✅ | 视频标题 |
| 原始标题 | ✅ | 原始标题 |
| 剧情简介 | ✅ | 详细简介 |
| 标签 | ✅ | 标签列表 |
| 类型 | ✅ | 类型列表 |
| 演员 | ❌ | 演员名称（通过映射表） |
| 制作商 | ❌ | 制作商名称（通过映射表） |
| 厂牌 | ❌ | 厂牌名称（通过映射表） |

### 映射表机制

**演员映射表**
```json
{
  "松下紗栄子": "松下纱荣子",
  "JULIA": "京香JULIA",
  "三上悠亜": "三上悠亚"
}
```

**制作商映射表**
```json
{
  "S1 NO.1 STYLE": "S1",
  "PRESTIGE": "プレステージ",
  "MOODYZ": "ムーディーズ"
}
```

**标签映射表**
```json
{
  "巨乳": "大胸",
  "单体作品": "个人作品",
  "中文字幕": "字幕"
}
```

---

## 文件和命名系统

### Jinja2 模板引擎

**支持的变量**

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `number` | 番号 | ABP-123 |
| `title` | 标题 | 标题名称 |
| `originaltitle` | 原始标题 | Original Title |
| `actor` | 演员（逗号分隔） | 演员1,演员2 |
| `first_actor` | 首位演员 | 演员1 |
| `all_actor` | 全部演员 | 演员1,演员2,演员3 |
| `letters` | 番号前缀 | ABP |
| `first_letter` | 番号首字符 | A |
| `outline` | 简介 | 剧情简介 |
| `director` | 导演 | 导演名称 |
| `series` | 系列 | 系列名称 |
| `studio` | 制作商 | 制作商名称 |
| `publisher` | 发行商 | 发行商名称 |
| `release` | 发行日期 | 2024-01-01 |
| `year` | 年份 | 2024 |
| `runtime` | 时长（分钟） | 120 |
| `mosaic` | 马赛克类型 | 有码 |
| `definition` | 清晰度 | 1080p |
| `cnword` | 字幕标识 | [中字] |
| `moword` | 版本标识 | [版本] |
| `filename` | 原文件名（不含扩展名） | 原文件名 |
| `ext` | 文件扩展名 | mp4 |
| `wanted` | 想看人数 | 1000 |
| `score` | 评分 | 8.5 |
| `four_k` | 4K 标识 | [4K] |

**模板示例**

```jinja2
# 简单模板
{{ number }}.{{ ext }}

# 包含标题
[{{ number }}] {{ title }}.{{ ext }}

# 包含演员
[{{ number }}] {{ title }} - {{ first_actor }}.{{ ext }}

# 条件渲染
[{% if number %}{{ number }}{% endif %}]{{ title }}.{{ ext }}

# 复杂模板
[{% if number %}{{ number }}{% endif %}][{{ studio }}]{{ title }}-{{ first_actor }}.{{ ext }}
```

### 文件处理功能

**批量重命名**
- 📁 批量重命名文件
- 📁 批量重命名文件夹
- 🔗 支持软链接和硬链接
- 🔄 支持预览和撤销

**文件移动**
- 🔄 移动文件到新位置
- 🔗 创建软链接
- 🔗 创建硬链接
- 📝 更新 NFO 文件路径

**清理功能**
- 🗑️ 删除旧文件
- 🗑️ 删除空文件夹
- 📋 生成清理报告

---

## 演员数据库管理

### Excel 数据库字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ID | int | ✅ | 唯一标识符 |
| 日文名 | str | ✅ | 演员日文原名 |
| 中文名 | str | ❌ | 中文姓名 |
| 繁体名 | str | ❌ | 繁体中文姓名 |
| 别名 | str | ❌ | 其他名称（逗号分隔） |
| 信息链接 | str | ❌ | 相关网站链接（LibreDMM、JavDB、TMDB 链接等） |
| TMDB ID | int | ❌ | TMDB 数据库 ID |

### TMDB 集成功能

#### TMDB API 查询

**能干这些事**
- 🔍 按名字搜演员
- 🎬 拿 TMDB ID 和基本信息
- 🌐 拿多语言名字（中文、日文等）
- 🏷️ **日文名自动填**：TMDB 返回的 `original_name`（通常是日文原名）优先填到 Excel 的"日文原名列"
- 🔗 **自动补网址**：查完 TMDB 后统一检查缺网址的演员，用日文名去 LibreDMM 搜个人主页补上
- 🔄 查到的东西写回本地 Excel 缓存

**匹配特性**
- 支持日文名、中文名、繁体名、别名联合命中
- 支持常见异体字归一化和名字变体展开
- 使用候选排序提升命中率

#### 令牌桶限流器

**参数配置**
- `rate`: 速率（令牌/秒），默认 3.5
- `burst`: 突发容量，默认 10

**限流逻辑**
```
1. 请求到达
   ↓
2. 检查令牌桶
   ↓
3. 有令牌 → 允许请求，消耗令牌
   ↓
4. 无令牌 → 等待令牌补充
```

**实现说明**
- 使用项目内的 `_TmdbRateLimiter`
- 结合异步并发控制，避免请求突刺

#### 并发查询

**并发配置**
- 默认并发数：3
- 查询前优先反查本地 Excel 缓存
- 对候选进行排序匹配

**查询流程**
```
1. 读演员列表
   ↓
2. 创建任务
   ↓
3. 并发查 TMDB
   ↓
4. 收到结果（日文名用 TMDB 的原名）
   ↓
5. 写回 Excel
   ↓
6. 统一扫一遍：缺网址的演员用日文名去 LibreDMM 补上
```

### 数据从哪补

| 数据源 | 拿来干啥 | 优先级 |
|--------|---------|--------|
| TMDB API | TMDB ID、基本信息、图片 | 1 |
| LibreDMM | 演员主页链接（查完 TMDB 统一补） | 1 |
| Wikidata | 维基百科资料、简介 | 2 |
| Av-wiki | 演员真实日文名 | 2 |
| Gfriends | 演员头像和写真 | 3 |
| graphis.ne.jp | 写真集信息 | 3 |

---

## Emby/Jellyfin 集成

### 演员信息补全

**功能模块** (emby_actor_info.py)

**数据来源**
- Wikipedia：获取简介、出生日期、出生地等
- 本地数据库：获取中文名、别名等

**补全字段**
- 📝 演员简介（biography）
- 📅 出生日期（birthday）
- 📍 出生地（place_of_birth）
- 🔗 个人资料链接（profile_url）

**API 调用**
```python
async def update_emby_actor_info():
    """从 Wikipedia 获取信息，更新 Emby 演员。"""
    ...
```

### 演员图片更新

**功能模块** (emby_actor_image.py)

**图片来源优先级**
1. graphis.ne.jp
2. Gfriends GitHub
3. 本地文件夹

**图片处理**
- 📸 下载图片
- 🖼️ 格式转换（JPEG/PNG）
- 📐 尺寸调整
- 🚀 上传到 Emby/Jellyfin

**API 调用**
```python
async def upload_actor_image(
    actor_id: str,
    image_path: str,
    emby_url: str,
    api_key: str
):
    """上传演员图片到 Emby"""
    with open(image_path, 'rb') as f:
        image_data = f.read()

    url = f"{emby_url}/Items/{actor_id}/Images/Primary"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=image_data,
            headers={"X-Emby-Token": api_key}
        )
```

### 配置说明

**Emby/Jellyfin 配置项**
```json
{
  "server_type": "emby",  // emby 或 jellyfin
  "emby_url": "http://localhost:8096",
  "api_key": "your_api_key",
  "emby_on": [
    "actor_info",  // 同步演员信息
    "actor_image", // 同步演员图片
    "create_actors_folder" // 创建 .actors 文件夹
  ],
  "concurrent": 3
}
```

---

## Amazon 集成

### ASIN 条码识别

**识别方式**
- 📸 从封面图片中检测 EAN/JAN 条码
- 🏷️ 从元数据中提取 ASIN
- 🔍 从标签详情中提取 ASIN

**识别流程**
```
1. 扫描视频文件
   ↓
2. 尝试提取 ASIN
   ↓
3. 验证 ASIN 格式
   ↓
4. 返回识别结果
```

### Amazon 产品搜索

**搜索功能**
- 🔍 按 ASIN 搜索
- 🔍 按番号搜索
- 🔍 按标题搜索

**搜索参数**
- `asin`: ASIN 条码
- `keywords`: 搜索关键词

**返回信息**
```json
{
  "asin": "B00XXXXXXX",
  "title": "商品标题",
  "product_url": "https://www.amazon.com/dp/B00XXXXXXX",
  "images": {
    "SL1500": "https://.../SL1500.jpg",
    "SL500": "https://.../SL500.jpg"
  }
}
```

### Amazon 数据库

**数据库功能**
- 💾 缓存 ASIN 数据到 Excel
- 🔍 快速查询已缓存的 ASIN
- 🔄 更新已有记录的 poster_url

**数据库结构**
```python
# 使用 amazon_database.py 中的函数
from mdcx.core.amazon_database import (
    save_asin_to_excel,
    query_asin_database,
    update_asin_record,
)

AsinRecord = {
    "number": str,      # 影片番号
    "asin": str,         # 亚马逊 ASIN
    "product_url": str,  # 商品详情页链接
    "title": str,        # 商品标题
    "poster_url": str,   # 封面图片 URL
}
```

### 高清封面获取

**封面尺寸**

| 尺寸标识 | 分辨率 | 用途 |
|---------|--------|------|
| SL1500 | 1500x1500 | 高清封面 |
| SL500 | 500x500 | 中等封面 |
| SL300 | 300x300 | 缩略图 |
| SL75 | 75x75 | 小图标 |

**获取流程**
```
1. 获取封面候选图
   ↓
2. 扫描封面条码（EAN/JAN）
   ↓
3. 按条码精确匹配 Amazon 商品
   ↓
4. 条码未命中时按标题/关键词搜索
   ↓
5. 结果排序：条码硬匹配 → 标题置信度 → 关键词
   ↓
6. 下载 SL1500 封面
```

---

## 网络功能

### 代理配置

**代理类型**

MDCx 支持多种代理配置：

| 代理类型 | 说明 | 配置示例 |
|---------|------|---------|
| **使用代理** | 仅对列表中的网站走代理 | 勾选 + 填写走代理网站 |
| **不使用代理** | 直连网络 | 无需配置 |
| **HTTP 代理** | HTTP/HTTPS 代理 | `http://proxy.example.com:8080` |
| **SOCKS5 代理** | SOCKS5 代理 | `socks5://proxy.example.com:1080` |

**代理设置**

在"设置" → "网络"中配置：
- **使用代理**：勾选后通过代理访问填写的网站
- **代理地址**：输入代理服务器地址和端口
- **走代理网站**：填写需要走代理的域名，逗号分隔

### 走代理网站功能

**功能说明**

"走代理网站"功能允许您指定哪些网站需要走代理，其他网站全部直连。这样就不怕代理影响国内网站的访问了。默认已预填了亚马逊的两个域名。

**配置方式**

在"设置" → "网络" → "使用代理"中配置：

```
默认值：amazon.co.jp,m.media-amazon.com
```

支持以下格式：

1. **网站值**（推荐）
   ```
   javdb
   javbus
   ```

2. **完整域名**
   ```
   amazon.co.jp
   www.javdb.com
   ```

3. **多个网站**（逗号分隔）
   ```
   amazon.co.jp,m.media-amazon.com,javdb,javbus
   ```

**支持的网站值**

| 网站值 | 对应域名 | 说明 |
|--------|---------|------|
| `javdb` | javdb.com, www.javdb.com | JavDB 网站 |
| `javbus` | javbus.com, www.javbus.com | JavBus 网站 |
| `tmdb` | api.tmdb.org | TMDB API |
| `libredmm` | libredmm.com | LibreDMM 网站 |
| `missav` | missav.com, www.missav.com | MissAV 网站 |
| `jav321` | jav321.com, www.jav321.com | Jav321 网站 |
| `javlibrary` | javlibrary.com, www.javlibrary.com | JavLibrary 网站 |
| `fc2` | fc2.com, www.fc2.com | FC2 官方网站 |
| `dmm` | dmm.co.jp | DMM 官方网站 |
| ... | ... | 其他支持的网站 |

**使用场景**

**场景 1：默认只让亚马逊走代理**
```
配置：amazon.co.jp,m.media-amazon.com
说明：只有亚马逊走代理，其他网站全部直连
```

**场景 2：JavDB 也需要走代理**
```
配置：amazon.co.jp,m.media-amazon.com,javdb
说明：亚马逊和 JavDB 走代理，其他直连
```

**场景 3：多个网站走代理**
```
配置：javdb,javbus,dmm
说明：这三个网站走代理，其余全直连
```

**实现原理** (web_async.py)

系统在发起请求前会检查目标主机是否在"走代理网站"列表中：

```python
def _is_proxy_host(self, host: str) -> bool:
    """检查主机是否应该走代理"""
    if not host or not self.proxy_sites:
        return False

    for proxy_site in self.proxy_sites:
        # 直接匹配
        if host == proxy_site:
            return True

        # 匹配网站值对应的域名
        for domain_key, website_enum in WEB_DIC.items():
            if website_enum.value == proxy_site:
                if host == domain_key or host.endswith("." + domain_key):
                    return True

    return False

# 使用代理前检查
use_proxy = use_proxy and self._is_proxy_host(host)
```

**注意事项**

⚠️ **只走列表**：只有填在列表里的网站才会走代理，其他网站全部直连

⚠️ **列表为空**：如果列表为空，即使勾了使用代理，也没有任何网站走代理

⚠️ **大小写不敏感**：配置中的网站值不区分大小写

⚠️ **域名匹配**：支持子域名匹配（如 `amazon.co.jp` 会匹配 `www.amazon.co.jp`）

⚠️ **常见问题**：
- 如果勾了使用代理但网站还是不通，先检查域名写没写对
- 某些网站可能需要同时配置多个域名
- 可以使用开发者工具查看实际请求的域名

### 网络检查功能

**功能模块** (network_check.py)

**检查项**

| 检查项 | 说明 | 超时 |
|--------|------|------|
| 网络连接 | 检查是否联网 | 5s |
| DNS 解析 | 测试 DNS 解析 | 5s |
| HTTP 连接 | 测试 HTTP 连接 | 10s |
| HTTPS 连接 | 测试 HTTPS 连接 | 10s |
| 代理连接 | 测试代理连接 | 10s |
| 网站可达性 | 测试目标网站 | 30s |

**使用示例**
```python
from mdcx.core.network_check import check_network_status

# 检查网络连接
result = await check_network_status()
print(result)  # {'online': True, 'latency': 50}
```

### 反爬机制

**浏览器指纹伪装**
- 🎭 模拟真实浏览器 User-Agent
- 🌐 模拟浏览器 TLS 指纹
- 📋 自定义请求头
- 🍪 Cookie 管理

**限流策略**
- ⏱️ 请求间隔控制
- 🔒 并发数限制
- 🔄 失败重试机制
- ⏰ 随机延时

**代理支持**
- 🔗 HTTP 代理
- 🔗 SOCKS5 代理
- ⚠️ 不走代理网站配置

---

## 工具函数

### 文件工具 (file.py)

**功能列表**
- 📁 文件路径处理
- 📝 文件名处理
- 🔍 文件查找
- 📊 文件统计
- 🧹 文件清理

**常用函数**
```python
from mdcx.utils.file import move_file_sync, copy_file_sync, delete_file_sync

# 同步文件操作
move_file_sync("/path/to/src", "/path/to/dst")
copy_file_sync("/path/to/src", "/path/to/dst")
delete_file_sync("/path/to/file")
```

### 语言工具 (language.py)

**功能列表**
- 🌐 日语检测
- 🌐 英语检测
- 🌐 翻译前英语判断

**使用示例**
```python
from mdcx.utils.language import is_japanese, is_english

# 检测是否为日语
lang = is_japanese("こんにちは")  # True

# 检测是否为英语
is_en = is_english("Hello")  # True
```

### 路径工具 (path.py)

**功能列表**
- 📁 路径规范化
- 🔗 路径拼接
- 📂 路径检查
- 🔄 路径转换

### 视频工具 (video.py)

**功能列表**
- 🎬 视频高度/编码检测（pyav 或 ffprobe 后端）

---

## 实用工具

### 字幕管理工具 (subtitle.py)

**功能列表**
- 🔍 自动匹配字幕
- 📁 字幕文件复制
- 🏷️ 字幕重命名
- 📄 .chs 后缀管理

**使用示例**
```python
from mdcx.tools.subtitle import add_sub_for_all_video

# 对所有视频执行字幕添加
await add_sub_for_all_video()
```

### Wiki 工具 (wiki.py)

**功能列表**
- 🌐 查询 Wikipedia
- 📝 提取演员信息
- 🔗 获取链接

---

## 高级功能

### 异步并发处理

**并发架构**
- ⚡ asyncio 异步编程
- 📊 渐进式任务调度
- ⚙️ 可配置并发数
- 📈 实时进度监控

**并发配置**
```python
# 配置并发数
concurrent = 3

# 创建异步任务
tasks = [crawl_file(file) for file in files]

# 并发执行
results = await asyncio.gather(*tasks)
```

### 缓存机制

**缓存类型**
- 💾 爬虫结果缓存
- 💾 图片缓存
- 💾 ASIN 数据库
- 💾 TMDB 数据缓存

**缓存策略**
- ⏰ 过期时间配置
- 🔄 自动刷新
- 🗑️ 手动清理

### 数据导出

**导出格式**
- 📄 Excel 导出
- 📄 CSV 导出
- 📄 JSON 导出

**导出内容**
- 📊 演员数据库
- 📊 刮削结果
- 📊 统计数据

---

**功能统计**
- 🌐 43 个网站爬虫
- 📝 30+ NFO 字段
- 🌐 5 大翻译引擎
- 🎭 8 大功能模块
- ⚡ 异步并发架构
