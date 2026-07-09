# 配置系统

> 本文档从 CODE_WIKI.md 提取，详见完整文档

---

## 配置模型 ([mdcx/config/models.py](../mdcx/config/models.py))

### `Config`

主配置类，基于 Pydantic。

**1. 通用设置**

- `media_path`：媒体文件存放路径
- `softlink_path`：软链接存放路径
- `success_output_folder`：处理成功后的输出目录
- `failed_output_folder`：处理失败后的输出目录
- `media_type`：媒体文件类型列表（如 mp4、mkv）
- `sub_type`：字幕文件类型列表（如 srt、ass）

**2. 清理设置**

- `folders`：需要排除的目录列表
- `string`：要从文件名中删除的字符串列表
- `file_size`：只处理大于此值（MB）的文件
- `clean_*`：各种清理规则

**3. 刮削设置**

- `thread_number`：并发抓取线程数
- `thread_time`：每次抓取之间的延时（秒）
- `main_mode`：主模式
- `read_mode`：读取模式
- `update_mode`：更新模式
- `download_files`：需要下载的文件类型列表
- `scrape_like`：刮削模式

**4. 网站设置**

- `website_youma`：有码影片的网站源列表
- `website_wuma`：无码影片的网站源列表
- `website_suren`：素人影片的网站源列表
- `website_fc2`：FC2 影片的网站源列表
- `website_oumei`：欧美影片的网站源列表
- `website_guochan`：国产影片的网站源列表
- `fixed_scraping_type`：锁定刮削类型

**5. 字段配置**

- `field_configs`：各字段的网站优先级、语言、翻译开关
- `type_field_configs`：按类型区分字段优先级
- `site_configs`：网站配置

**6. 翻译配置**

- `translate_config`：`TranslateConfig` 对象
  - `translate_by`：翻译服务列表（按优先级）
  - `baidu_appid`：百度翻译 APP ID
  - `baidu_key`：百度翻译密钥
  - `deepl_key`：DeepL 密钥
  - `deeplx_url`：DeepLX 服务地址
  - `llm_*`：大语言模型相关配置

**7. 命名和格式化**

- `nfo_include_new`：NFO 文件中包含哪些内容
- `folder_name`：目录名称模板
- `naming_file`：文件命名模板，默认 `{{ number }}`
- `naming_media`：媒体命名模板（NFO 标题），默认 `{% if number %}{{ number }}{% endif %}{% if title and title != number %} {{ title }}{% endif %}`
- `update_titletemplate`：更新模式 Emby 标题模板，默认同上（无括号格式）
- `prevent_char`：禁止出现在文件名中的字符
- `fields_rule`：字段规则列表
- `*_style`：各类样式配置

**8. 服务器设置**

- `server_type`：服务器类型（emby/jellyfin）
- `emby_url`：Emby 服务器地址
- `api_key`：API 密钥
- `user_id`：用户 ID
- `emby_on`：Emby 功能开关列表
- `use_database`：是否使用数据库
- `info_database_path`：信息数据库路径

**9. 水印设置**

- `poster_mark`、`thumb_mark`、`fanart_mark`：不同图片的水印
- `mark_size`：水印大小
- `mark_type`：水印类型列表
- `mark_fixed`、`mark_pos*`：水印位置规则

**10. 网络设置**

- `use_proxy`：代理类型（no/http/socks5）
- `proxy`：代理地址
- `proxy_sites`：走代理的网站列表
- `cf_bypass_*`：Cloudflare Bypass 配置
- `timeout`、`retry`：超时时间和重试次数
- `theporndb_api_token`、`tmdb_api_key`：第三方 API 密钥

**11. 日志设置**

控制程序输出哪些日志。

- `show_web_log`：是否显示网页日志
- `show_from_log`：是否显示来源日志
- `show_data_log`：是否显示数据日志
- `save_log`：是否保存日志到文件

**主要方法**：
- `get_site_config(site)`：获取某个网站的配置
- `get_site_url(site, default)`：获取网站的自定义 URL
- `get_field_config(field)`：获取某个字段的配置
- `get_type_sites(scraping_type)`：获取某类影片使用的网站
- `get_type_field_config(scraping_type, field)`：获取某类型下某字段的配置
- `set_field_sites(field, sites)`：设置字段对应的网站
- `set_field_language(field, language)`：设置字段使用的语言
- `set_field_translate(field, translate)`：开关字段翻译

## 配置枚举 ([mdcx/config/enums.py](../mdcx/config/enums.py))

### `Website`

支持的网站枚举，共 36 个站点。

### `FixedScrapingType`

固定刮削类型的枚举。用来告诉程序"这部片子属于哪一类"。

**类型**：
- `AUTO`：自动识别
- `YOUMA`：有码
- `WUMA`：无码
- `SUREN`：素人
- `FC2`：FC2 系列
- `OUMEI`：欧美
- `GUOCHAN`：国产

### 其他枚举

- `Language`：语言
- `Translator`：翻译服务
- `EmbyAction`：Emby 操作
- `DownloadableFile`：可下载的文件类型
- `KeepableFile`：可保留的文件类型
- `ReadMode`：读取模式
- `Switch`：功能开关
- `NfoInclude`：NFO 包含的内容
- `MarkType`：水印类型
- 等等

## 配置管理器 ([mdcx/config/manager.py](../mdcx/config/manager.py))

### `ConfigManager`

配置管理器负责配置的加载、保存、迁移等。

**主要方法**：
- `__init__()`：初始化
- `load()`：加载配置
- `save()`：保存配置
- `reset()`：重置为默认配置
- `handle_v1()`：处理旧版 V1 配置
- `_replace_config()`：热切换配置（不重启就生效）
- `acquire_computed()`：获取计算属性租约

**配置加载流程**：
1. 检查标记文件，确定配置路径在哪
2. 尝试加载配置文件
3. 如果是旧版 .ini 配置，自动转换为新版 JSON 格式
4. 验证配置是否正确
5. 应用配置

---

## 网络配置详解

### 代理配置

**配置项**

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `use_proxy` | bool | `true` | 是否使用代理 |
| `proxy` | str | `"http://127.0.0.1:7890"` | 代理地址 |

**配置示例**

```json
{
  "use_proxy": "socks5",
  "proxy": "socks5://127.0.0.1:1080"
}
```

### 走代理网站配置

有些网站需要代理才能访问，可以单独设置哪些网站走代理。默认已预填常用的亚马逊域名。

**配置项**

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `proxy_sites` | str | `amazon.co.jp,m.media-amazon.com` | 走代理的网站列表 |

**配置格式**

支持以下三种写法：

1. **写完整域名**
   ```
   amazon.co.jp
   ```

2. **写多个域名**（逗号分隔）
   ```
   amazon.co.jp,javdb,javbus
   ```

3. **写网站值**（推荐，系统自动匹配域名）
   ```
   javdb
   javbus
   ```

**配置项**

**支持的网站值**

系统会自动将网站值映射到对应的域名。以下是常用的网站值：

| 网站值 | 自动匹配的域名 |
|--------|--------------|
| `javdb` | javdb.com, www.javdb.com |
| `javbus` | javbus.com, www.javbus.com |
| `tmdb` | api.tmdb.org |
| `libredmm` | libredmm.com, www.libredmm.com |
| `missav` | missav.com, www.missav.com |
| `jav321` | jav321.com, www.jav321.com |
| `javlibrary` | javlibrary.com, www.javlibrary.com |
| `fc2` | fc2.com, www.fc2.com |
| `dmm` | dmm.co.jp |
| `mgstage` | mgstage.com, www.mgstage.com |
| `prestige` | prestige-av.com |
| `official` | official-av.com |
| `avsox` | avsox.com, www.avsox.com |
| `avsex` | avsex.cc |
| `mmtv` | mmtv.cc |
| `mywife` | mywife-j.com |
| `getchu` | getchu.com |
| `giga` | giga.tv |
| `faleno` | faleno.jp |
| `fantastica` | fantastica.video |
| `dahlia` | dahlia-av.com |
| `xcity` | xcity.jp |
| `kin8` | kin8tengoku.com |
| `love6` | love6.tv |
| `avbase` | avbase.cc |
| `cableav` | cableav.tv |
| `freejavbt` | freejavbt.com |
| `hscangku` | hscangku.com |
| `iqqtv` | iqqtv.com |
| `mdtv` | mdtv.co.jp |
| `cnmdb` | cnmdb.com |
| `guochan` | guochan.cc |
| `madouqu` | madouqu.com |
| `lulubar` | lulubar.cc |
| `hdouban` | hdouban.com |
| `theporndb` | theporndb.com |

**实际使用场景**

**场景 1：只需要亚马逊走代理**

默认已填好 `amazon.co.jp,m.media-amazon.com`，开箱即用。

```json
{
  "use_proxy": true,
  "proxy": "http://127.0.0.1:7890",
  "proxy_sites": "amazon.co.jp,m.media-amazon.com"
}
```

**场景 2：JavDB 和 JavBus 也要走代理**

把 `javdb`、`javbus` 加到走代理列表里。

```json
{
  "use_proxy": true,
  "proxy": "http://127.0.0.1:7890",
  "proxy_sites": "amazon.co.jp,m.media-amazon.com,javdb,javbus"
}
```

**场景 3：多个网站走代理**

用逗号分隔多个网站值。

```json
{
  "use_proxy": true,
  "proxy": "http://127.0.0.1:7890",
  "proxy_sites": "javdb,javbus,dmm"
}
```

**配置方式**

在 MDCx 设置的"使用代理"选项里，直接输入网站列表，逗号分隔即可。

**注意事项**

- 支持完整域名匹配（如 `amazon.co.jp`）
- 支持子域名匹配（`amazon.co.jp` 也会匹配 `www.amazon.co.jp`）
- 网站值不区分大小写（`JavDB` 和 `javdb` 效果一样）
- 列表为空时，即使勾选了使用代理，也没有任何网站走代理
- 只有列表里的网站才会走代理，其他网站全部直连

**常见问题**

- 如果勾了使用代理但抓取网站还是不通，检查域名写没写对
- 可以用浏览器开发者工具看实际请求的是哪个域名
- 有些网站可能需要配多个域名才能完全走代理

**实现原理**

程序在发起请求前会检查目标主机是否在走代理列表中：

```python
def _is_proxy_host(self, host: str) -> bool:
    """检查主机是否应该走代理"""
    if not host or not self.proxy_sites:
        return False

    for proxy_site in self.proxy_sites:
        proxy_site = proxy_site.strip().lower()

        # 直接匹配
        if host == proxy_site:
            return True

        # 网站值匹配域名
        for domain_key, website_enum in WEB_DIC.items():
            if website_enum.value == proxy_site:
                if host == domain_key or host.endswith("." + domain_key):
                    return True
                # 检查常见 TLD
                for tld in [".com", ".net", ".org", ".co", ".jp", ".io"]:
                    if host == domain_key + tld or host.endswith("." + domain_key + tld):
                        return True

    return False

# 使用代理前检查
use_proxy = use_proxy and self._is_proxy_host(host)
```

### Cloudflare Bypass 配置

部分网站用了 Cloudflare 防护，程序直接访问会被拦截。配置 CF Bypass 可以绕过。

**你需要什么**

一个旁路（bypass）服务的地址。可以自己搭建，也可以用社区公开服务。

**配置项**

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `cf_bypass_url` | 空 | 旁路服务地址，如 `http://127.0.0.1:8000` |
| `cf_bypass_proxy` | 空 | 旁路专用代理（可选），与常规代理独立 |

**在 MDCx 设置位置**

打开 **设置 → 网络**，下拉到"CF Bypass"和"CF Bypass代理"两个输入框。

**怎么知道生效了**

主界面点"网络状态"，日志区会显示 `CF Bypass：已配置`。抓取时看到 `🛡️ [CF]` 日志前缀说明它正在工作。

**常见问题**

- **不配能用吗？** 能。大部分网站不会被 CF 拦，只有少数严格站点才需要。
- **怎么搭旁路？** 搜索 `flaresolverr` docker 镜像，一行命令就能跑起来。

---

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [数据模型](data-models.md) - 数据结构定义
- [爬虫系统](crawler-system.md) - 爬虫框架详解
- [命名系统](naming-system.md) - 命名规则详解
