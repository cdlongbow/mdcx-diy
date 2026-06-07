# 配置系统

> 本文档从 CODE_WIKI.md 提取,详见完整文档

---

## 配置模型 ([mdcx/config/models.py](mdcx/config/models.py))

### `Config`

主配置类,基于 Pydantic

**主要配置区域**:

1. **通用设置**
   - `media_path`:媒体路径
   - `softlink_path`:软链接路径
   - `success_output_folder`:成功输出目录
   - `failed_output_folder`:失败输出目录
   - `media_type`:媒体文件类型列表
   - `sub_type`:字幕文件类型列表

2. **清理设置**
   - `folders`:排除目录列表
   - `string`:要从文件名删除的字符串列表
   - `file_size`:要处理的最小文件大小(MB)
   - `clean_*`:各种清理规则

3. **刮削设置**
   - `thread_number`:并发数
   - `thread_time`:线程延时
   - `main_mode`:主模式
   - `read_mode`:读取模式
   - `update_mode`:更新模式
   - `download_files`:下载文件类型列表
   - `scrape_like`:刮削模式

4. **网站设置**
   - `website_youma`:有码网站源列表
   - `website_wuma`:无码网站源列表
   - `website_suren`:素人网站源列表
   - `website_fc2`:FC2 网站源列表
   - `website_oumei`:欧美网站源列表
   - `website_guochan`:国产网站源列表
   - `fixed_scraping_type`:锁定刮削类型

5. **字段配置**
   - `field_configs`:各字段的网站优先级、语言、翻译开关
   - `type_field_configs`:按类型字段优先级
   - `site_configs`:网站配置

6. **翻译配置**
   - `translate_config`:`TranslateConfig` 对象
     - `translate_by`:翻译服务列表
     - `baidu_appid`:百度 APP ID
     - `baidu_key`:百度密钥
     - `deepl_key`:DeepL 密钥
     - `deeplx_url`:DeepLX URL
     - `llm_*`:LLM 相关配置

7. **命名和格式化**
   - `nfo_include_new`:NFO 包含内容列表
   - `folder_name`:目录名称模板
   - `naming_file`:文件命名模板
   - `naming_media`:媒体命名模板
   - `prevent_char`:禁止字符
   - `fields_rule`:字段规则列表
   - `*_style`:各类样式

8. **服务器设置**
   - `server_type`:服务器类型(emby/jellyfin)
   - `emby_url`:Emby 地址
   - `api_key`:API 密钥
   - `user_id`:用户 ID
   - `emby_on`:Emby 功能开关列表
   - `use_database`:使用数据库
   - `info_database_path`:信息数据库路径

9. **水印设置**
   - `poster_mark`、`thumb_mark`、`fanart_mark`:各图片水印
   - `mark_size`:水印大小
   - `mark_type`:水印类型列表
   - `mark_fixed`、`mark_pos*`:水印位置规则

10. **网络设置**
    - `use_proxy`:代理类型
    - `proxy`:代理地址
    - `no_proxy_sites`:不使用代理网站
    - `cf_bypass_*`:Cloudflare Bypass 配置
    - `timeout`、`retry`:超时和重试
    - `theporndb_api_token`、`tmdb_api_key`:API 密钥

11. **日志设置**
    - `show_web_log`:显示网页日志
    - `show_from_log`:显示来源日志
    - `show_data_log`:显示数据日志
    - `save_log`:保存日志

**主要方法**:
- `get_site_config(site)`:获取网站配置
- `get_site_url(site, default)`:获取网站自定义 URL
- `get_field_config(field)`:获取字段配置
- `get_type_sites(scraping_type)`:获取类型网站
- `get_type_field_config(scraping_type, field)`:获取类型字段配置
- `set_field_sites(field, sites)`:设置字段网站
- `set_field_language(field, language)`:设置字段语言
- `set_field_translate(field, translate)`:设置字段翻译

## 配置枚举 ([mdcx/config/enums.py](mdcx/config/enums.py))

### `Website`

支持的网站枚举(34个站点)

### `FixedScrapingType`

刮削类型枚举

**类型**:
- `AUTO`:自动
- `YOUMA`:有码
- `WUMA`:无码
- `SUREN`:素人
- `FC2`:FC2
- `OUMEI`:欧美
- `GUOCHAN`:国产

### 其他枚举

- `Language`:语言
- `Translator`:翻译服务
- `EmbyAction`:Emby 操作
- `DownloadableFile`:可下载文件类型
- `KeepableFile`:可保留文件类型
- `ReadMode`:读取模式
- `Switch`:功能开关
- `NfoInclude`:NFO 包含内容
- `MarkType`:水印类型
- 等等...

## 配置管理器 ([mdcx/config/manager.py](mdcx/config/manager.py))

### `ConfigManager`

管理配置的加载、保存、迁移等

**主要方法**:
- `__init__()`:初始化
- `load()`:加载配置
- `save()`:保存配置
- `reset()`:重置为默认配置
- `handle_v1()`:处理 V1 配置
- `_replace_config()`:热切换配置
- `acquire_computed()`:获取计算属性租约

**配置加载流程**:
1. 检查标记文件确定配置路径
2. 尝试加载配置文件
3. 如果是旧版 .ini 配置,自动转换为新版
4. 验证配置
5. 应用配置

---

## 网络配置详解

### 代理配置

**配置项**

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `use_proxy` | str | `no` | 代理类型（no/http/socks5） |
| `proxy` | str | `""` | 代理地址（如 `http://proxy.com:8080`） |

**代理类型**

- `no`: 不使用代理
- `http`: HTTP/HTTPS 代理
- `socks5`: SOCKS5 代理

**配置示例**

```json
{
  "use_proxy": "socks5",
  "proxy": "socks5://127.0.0.1:1080"
}
```

### 不走代理网站配置

**配置项**

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `no_proxy_sites` | str | `api.tmdb.org` | 不使用代理的网站列表 |

**配置格式**

支持以下格式：

1. **单个网站**
   ```
   api.tmdb.org
   ```

2. **多个网站**（逗号分隔）
   ```
   api.tmdb.org,javdb,javbus
   ```

3. **网站值**（推荐，自动匹配域名）
   ```
   javdb
   tmdb
   libredmm
   ```

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

**使用场景**

**场景 1：TMDB API 走代理速度慢**
```json
{
  "use_proxy": "socks5",
  "proxy": "socks5://127.0.0.1:1080",
  "no_proxy_sites": "api.tmdb.org"
}
```
说明：其他网站走代理，TMDB API 直连

**场景 2：JavDB 使用代理无法访问**
```json
{
  "use_proxy": "http",
  "proxy": "http://proxy.com:8080",
  "no_proxy_sites": "javdb"
}
```
说明：JavDB 直连，其他网站走代理

**场景 3：多个 API 服务不走代理**
```json
{
  "use_proxy": "socks5",
  "proxy": "socks5://127.0.0.1:1080",
  "no_proxy_sites": "api.tmdb.org,theporndb,cnmdb"
}
```
说明：指定多个网站不走代理

**配置界面**

在 MDCx 主界面：
1. 打开"设置"
2. 进入"网络"标签
3. 在"不使用代理网站"输入框中输入配置
4. 点击"应用"保存配置

**注意事项**

⚠️ **域名匹配规则**：
- 支持完整域名匹配（如 `api.tmdb.org`）
- 支持子域名匹配（如 `api.tmdb.org` 会匹配 `sub.api.tmdb.org`）
- 网站值不区分大小写（`JavDB` 和 `javdb` 等价）

⚠️ **优先级**：
- `no_proxy_sites` 的优先级高于全局代理设置
- 如果主机在 `no_proxy_sites` 列表中，将直接连接

⚠️ **常见问题**：
- 如果配置后仍然走代理，请检查域名是否正确
- 可以使用开发者工具查看实际请求的域名
- 某些网站可能需要同时配置多个域名

**实现细节**

系统在发起请求前会检查目标主机：

```python
def _is_no_proxy_host(self, host: str) -> bool:
    """检查主机是否应该绕过代理"""
    if not host or not self.no_proxy_sites:
        return False

    for no_proxy in self.no_proxy_sites:
        no_proxy = no_proxy.strip().lower()

        # 直接匹配
        if host == no_proxy:
            return True

        # 网站值匹配域名
        for domain_key, website_enum in WEB_DIC.items():
            if website_enum.value == no_proxy:
                if host == domain_key or host.endswith("." + domain_key):
                    return True
                # 检查常见 TLD
                for tld in [".com", ".net", ".org", ".co", ".jp", ".io"]:
                    if host == domain_key + tld or host.endswith("." + domain_key + tld):
                        return True

    return False

# 使用代理前检查
use_proxy = use_proxy and not self._is_no_proxy_host(host)
```

---

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [数据模型](data-models.md) - 数据结构定义
- [爬虫系统](crawler-system.md) - 爬虫框架详解
- [命名系统](naming-system.md) - 命名规则详解