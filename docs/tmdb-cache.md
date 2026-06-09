# TMDB 缓存系统详解

## 概述

MDCx 的 TMDB（The Movie Database）缓存系统是一个基于 Excel 文件的持久化 ID 映射数据库，用于缓存演员名到 TMDB ID 的对应关系。该系统避免了重复查询 TMDB API，显著提高了刮削效率。

## 缓存架构

TMDB 缓存由两层组成：

### 1. Excel 持久化缓存（主缓存）

- **存储位置**：`userdata/actor_database.xlsx`
- **缓存字段**：第 6 列（TMDB ID）、第 7 列（TMDB URL）
- **数据格式**：Excel 表格
- **生命周期**：持久化存储，程序重启后仍然有效
- **缓存内容**：演员名到 TMDB ID 的映射关系

### 2. 内存 dict 缓存（辅助缓存）

- **实现**：`resources.actor_db`（dict 类型）
- **用途**：程序运行时快速查询，避免反复读取 Excel 文件
- **生命周期**：进程级别，程序重启后失效
- **刷新机制**：每次成功写入 Excel 后自动调用 `reload_actor_db()` 刷新

## 缓存数据模型

### Excel 文件列结构

| 列号 | 字段名 | 说明 |
|------|--------|------|
| 0 | COL_JP | 演员日文原名 |
| 1 | COL_ZH_CN | 中文名 |
| 2 | COL_ZH_TW | 繁体名 |
| 3 | COL_KEYWORD | 别名 |
| 4 | COL_HREF | 信息链接 |
| 5 | COL_TMDBID | **TMDB ID（核心缓存字段）** |
| 6 | COL_TMDB_URL | TMDB 个人页面 URL |

### 内存缓存结构

```python
{
    "演员日文名": {
        "zh_cn": "中文名",
        "zh_tw": "繁体名",
        "keyword": "别名",
        "href": "链接",
        "tmdbid": 12345,  # int 或 None
        "tmdb_url": "https://www.themoviedb.org/person/12345"
    }
}
```

## 缓存工作流程

### 缓存读取流程

```
输入: 演员名列表
    │
    ▼
遍历每个演员名：
    │
    ├── 检查 resources.actor_db 中是否已有 tmdbid
    │   ├── 有 → 直接返回（缓存命中，无需网络请求）
    │   └── 没有 → 加入 need_query 列表
    │
    ▼
对 need_query 列表中的演员：
    ├── 先用 Excel 中的日文名、中文名、繁体名、别名做反向缓存搜索
    ├── 仍未命中时并发 3 路查询 TMDB
    ├── 通过令牌桶限流器（3.5 req/s，突发 10）
    ├── 使用名字归一化和候选排序完成匹配
    ├── 匹配成功后调用 update_actor_db_row() 写回 Excel
    └── update_actor_db_row() 内部自动刷新内存缓存
```

### 缓存命中路径（最快）

```
查询演员名 → 检查内存缓存 → 找到 tmdbid → 直接返回
```

这是最快的路径，无需网络请求，直接从内存 dict 中返回 TMDB ID。

### 缓存未命中路径

```
查询演员名 → 检查内存缓存 → 未找到 tmdbid
    ↓
检查 Excel 反向缓存（支持别名、中文名、繁体名）
    ↓
命中则直接返回
    ↓
仍未命中时继续
    ↓
调用 TMDB API 搜索演员
    ↓
使用名字归一化、异体字变体和候选排序匹配
    ↓
匹配成功后获取 TMDB ID
    ↓
写回 Excel 文件（第 6 列）
    ↓
刷新内存缓存
    ↓
返回 TMDB ID
```

### 缓存写入流程

```python
def update_actor_db_row(actor_name, tmdbid, tmdb_url):
    # 1. 在 Excel 中查找是否已有该演员行
    # 2. 如果已有：仅填充空白字段（不覆盖已有值）
    #    - tmdbid 填入第 6 列
    #    - tmdb_url 填入第 7 列
    # 3. 如果无：追加新行，包含所有字段
    # 4. 保存 Excel 文件
    # 5. 函数内部自动调用 resources.reload_actor_db() 刷新内存缓存
```

**写入原则**：
- 不覆盖已有值（保护手动编辑的数据）
- 仅填充空白字段
- 写入后立即刷新内存缓存

## 限流控制

TMDB API 查询使用令牌桶限流器 `_TmdbRateLimiter`：

| 参数 | 值 | 说明 |
|------|-----|------|
| 速率 | 3.5 req/s | 每秒最多 3.5 个请求 |
| 突发容量 | 10 | 允许短时间突发 10 个请求 |
| 并发数 | 3 | 最多 3 路并发查询 |

### 限流实现

```python
# 令牌桶限流器
class _TmdbRateLimiter:
    rate = 3.5        # 每秒 3.5 个令牌
    burst = 10         # 突发容量 10
```

### 并发控制

```python
# 最多 3 路并发
semaphore = asyncio.Semaphore(3)
```

## 缓存刷新机制

### 自动刷新

每次刮削更新演员数据库后自动调用：

```python
def reload_actor_db():
    # 1. 完全重新从 Excel 文件读取
    # 2. 覆盖 resources.actor_db
    # 3. 使用 read_only=True 模式加载（性能优化）
```

### 刷新时机

- 每次 `update_actor_db_row()` 成功写入后
- 用户手动编辑 Excel 文件后（下次刮削时自动重载）
- 程序启动时（初始加载）

## 数据迁移

### 旧版迁移

系统支持从旧版 `actor_tmdbid.xlsx` 迁移数据：

```python
def migrate_xml_to_xlsx():
    # 1. 读取旧版 actor_tmdbid.xlsx
    # 2. 加载到 old_tmdb_cache dict
    # 3. 合并到新版 actor_database.xlsx
    # 4. 保留旧文件（不再使用）
```

### 文件加载保护

程序启动时如果 `userdata/actor_database.xlsx` 不存在，会自动从内置副本 `resources/actor_database.xlsx` 复制一份到 `userdata/` 目录。`resources.actor_db_backup_path` 指向的就是这个内置副本。

## 使用场景

### 场景 1：首次刮削新演员

1. 用户刮削一部影片，包含新演员
2. 系统在内存缓存中查找演员名，未找到 tmdbid
3. 调用 TMDB API 搜索演员
4. 匹配成功后获取 TMDB ID
5. 写入 Excel 文件第 6 列
6. 刷新内存缓存
7. 返回 TMDB ID

### 场景 2：重复刮削已知演员

1. 用户再次刮削包含同一演员的影片
2. 系统在内存缓存中查找演员名，找到 tmdbid
3. 直接返回缓存的 TMDB ID
4. 无需网络请求，速度极快

### 场景 3：刮削时自动查询缺失 TMDB ID

1. 用户刮削一部影片
2. 系统发现某演员在 Excel 中缺少 tmdbid
3. 先用 Excel 中已有名字和别名做反向缓存匹配
4. 仍未命中时自动调用 TMDB API 查询（3 路并发，限流 3.5 req/s）
5. 查询成功后自动填充 TMDB ID 到 Excel
6. 自动刷新内存缓存

## 名字匹配策略

TMDB 查询结合以下策略提升命中率：

- 全角半角归一化
- 常见异体字归一化，如 `亜/亞 -> 亚`、`條 -> 条`、`瀬 -> 濑`、`沢/澤 -> 泽`、`桜/櫻 -> 樱`
- 假名和汉字混写变体，如 `かなこ <-> かな子`
- 使用日文名、中文名、繁体名和别名共同参与匹配
- 对 TMDB 候选使用出生地、日本特征、热度等做排序，而不是简单硬过滤

### 场景 4：手动编辑后自动同步

1. 用户手动编辑 `actor_database.xlsx`（添加新演员或修正数据）
2. 下次刮削时系统自动重载 Excel 文件
3. 内存缓存与 Excel 文件保持同步

## 配置选项

### TMDB API 配置

```json
{
  "tmdb_api_key": "your_api_key_here",
  "tmdb_api_base": "api.tmdb.org"
}
```

### 不走代理网站

TMDB 请求可以通过"不走代理网站"功能配置：

- 默认值：`api.tmdb.org`（不走代理）
- 支持设置完整域名 `api.tmdb.org`
- TMDB API 请求将直接连接，不经过代理
- 提高请求速度和稳定性

## 性能分析

### 缓存命中率

| 场景 | 网络请求 | 耗时 |
|------|----------|------|
| 首次查询 | 需要 | 300-1000ms（受限流影响） |
| 缓存命中 | 无需 | <1ms（内存查询） |

### 自动查询性能

- 10 个新演员：约 3-5 秒（受 3.5 req/s 限流）
- 100 个新演员：约 30-40 秒
- 1000 个新演员：约 5-7 分钟
- 缓存命中：无论数量多少，几乎瞬时完成

### 性能优化建议

1. **维护演员数据库**：尽量保持演员日文名、别名和 TMDB ID 准确，提升缓存命中率
2. **利用突发容量**：开始时可利用突发 10 个请求的容量
3. **缓存预热**：程序启动时预加载 Excel 到内存

## NFO 生成中的 TMDB ID 使用

TMDB ID 缓存最终用于 NFO 文件生成：

```xml
<actor>
    <name>演员名</name>
    <type>Actor</type>
    <tmdbid>12345</tmdbid>
</actor>
```

- `<tmdbid>` 字段来自缓存的 TMDB ID
- Emby/Jellyfin 通过此字段关联 TMDB 演员信息
- 实现演员信息的自动同步和补全

## 故障排查

### 常见问题

1. **TMDB ID 查询失败**
   - 检查 TMDB API Key 是否正确
   - 确认网络连接（特别是 api.tmdb.org 是否可达）
   - 查看日志中的 API 响应状态码

2. **缓存未命中**
   - 检查演员名是否与 Excel 中的名称完全匹配
   - 确认 Excel 文件未被损坏
   - 重启程序或重新开始刮削以重新加载 Excel

3. **查询速度慢**
   - 受令牌桶限流影响（3.5 req/s）
   - 刮削过程中自动查询缺失演员时属于正常现象
   - 可检查是否触发了 TMDB API 的速率限制

4. **Excel 文件损坏**
    - 程序仅在用户数据文件不存在时复制内置副本
    - 文件损坏时请使用用户自己的备份或手动修复
    - 检查 `userdata/actor_database.xlsx` 是否存在
    - 查看日志中的 `演员数据库` 相关读取失败或格式化失败提示

### 日志位置

TMDB 相关日志位于：
- 主日志文件：`logs/mdcx.log`
- 调试日志：启用调试模式后查看 API 请求详情

## 相关文件

| 文件 | 职责 |
|------|------|
| `./mdcx/core/tmdb_actor.py` | TMDB 缓存核心实现 |
| `./mdcx/config/resources.py` | 内存缓存管理与重载 |
| `./mdcx/core/nfo.py` | NFO 生成时读取 TMDB ID |
| `./mdcx/models/types.py` | 数据模型定义 |
| `./userdata/actor_database.xlsx` | 用户数据中的演员数据库（含 TMDB ID） |

## 与 Amazon 缓存的对比

| 特性 | TMDB 缓存 | Amazon 缓存 |
|------|-----------|-------------|
| 缓存内容 | 演员名 → TMDB ID | 番号 → ASIN + 封面 URL |
| 存储文件 | actor_database.xlsx | amazon_asin_database.xlsx |
| 搜索策略 | 直接 API 查询 | 三层策略（条码→标题→演员） |
| 限流速率 | 3.5 req/s | 自适应限流 |
| 并发数 | 3 | 自适应 |
| 缓存命中 | 直接返回 ID | 直接返回封面 URL |
