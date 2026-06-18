# Amazon 高清封面缓存系统详解

## 概述

MDCx 的 Amazon 高清封面功能是一个多层缓存系统。它从 Amazon 获取影片的高清封面图片，避免重复搜索，提高查询效率。

## 缓存架构

Amazon 缓存由两层组成：

### 1. Excel 持久化缓存（主缓存）

- **存储位置**：`userdata/amazon_asin_database.xlsx`
- **数据格式**：Excel 表格
- **缓存内容**：番号与 ASIN 的映射关系及相关元数据
- **生命周期**：持久化存储，程序重启后仍然有效

简单说就是：用一个 Excel 文件长期保存查询结果，关掉程序再打开，数据还在。

### 2. 内存 LRU 缓存（辅助缓存）

- **实现**：`@lru_cache(maxsize=1)`
- **用途**：缓存条码数字模板
- **生命周期**：进程级别，程序重启后失效

简单说就是：只在程序运行期间临时缓存条码模板，重启后消失。

## 缓存数据模型

```python
class AsinRecord(TypedDict, total=False):
    number: str          # 影片番号（如 "ABCD-123"）
    asin: str            # 亚马逊 ASIN（10位字母数字，如 "B08X4H2K9L"）
    product_url: str     # 亚马逊商品详情页链接
    title: str           # 商品标题
    poster_url: str      # 封面图片 URL
    search_keyword: str  # 搜索关键词
```

## 缓存工作流程

### 缓存命中路径（最快）

```
查询番号 → 检查 Excel 缓存 → 找到记录且有 poster_url → 直接返回 SL1500 尺寸图片URL
```

这是最快的路径，无需网络请求，直接返回已缓存的封面 URL。

### 缓存未命中路径（三层搜索策略）

当缓存未命中或缓存记录缺少 poster_url 时，系统按顺序执行三层搜索：

#### 第一层：条码快路径

```
从封面图片中通过 OpenCV 条码检测器提取 EAN-13 条码
    ↓
用条码在 Amazon 搜索
    ↓
校验详情页确认匹配
    ↓
成功后保存 ASIN 记录到数据库
```

- 使用 OpenCV 的 `barcode_BarcodeDetector` 检测封面图片中的条码
- 如果直接检测失败，使用 OCR 数字模板匹配作为回退
- 条码匹配准确率最高，优先级最高

#### 第二层：标题搜索路径

```
构建搜索关键词队列（标题、番号、演员名组合）
    ↓
对每个关键词搜索 Amazon
    ↓
收集候选结果
    ↓
对候选进行详情页校验
    ↓
按置信度排序，选择最佳匹配
    ↓
成功后保存 ASIN 记录到数据库
```

- 使用多指标标题置信度匹配算法
- 置信度计算包括：
  - SequenceMatcher 序列比（权重 0.6）
  - 通配符包含比（权重 0.25）
  - Bigram Jaccard 相似度（权重 0.15）
- 候选评分维度：
  - 标题置信度 x 100（基础分）
  - 详情页条码匹配 +220
  - 番号匹配 +120
  - 演员匹配比例 x 20
  - 介质优先级 x 2（Blu-ray > Software Download > DVD）

简单说就是：用多种方式计算匹配程度，综合打分，选最像的那个。

#### 第三层：演员兜底搜索

```
按演员名搜索 Amazon
    ↓
匹配标题置信度
    ↓
成功后保存 ASIN 记录到数据库
```

- 当前两层都失败时的最后尝试
- 使用演员名称作为搜索关键词

### 缓存写入

当任何一层搜索成功获取到 ASIN 和封面 URL 后：

```python
async def _save_asin_record(result, asin, title, poster_url, search_keyword, detail_url):
    # 1. 校验 ASIN 非空且格式为 10 位 [A-Z0-9]
    # 2. 查询是否已有该番号的记录
    # 3. 如果已有记录且 poster_url 不为空 -> 跳过（去重）
    # 4. 如果已有记录但缺少 poster_url -> 原地更新 poster_url
    # 5. 如果无记录 -> 新增一条记录到 Excel
```

## 封面尺寸转换

系统获取到 Amazon 封面 URL 后，会自动转换为 SL1500 尺寸（1500x1500 像素）：

- **SL1500**：1500x1500（高清，默认使用）
- **SL500**：500x500
- **SL300**：300x300
- **SL75**：75x75

转换方法：修改 URL 中的尺寸参数。

## 网络层限流控制

Amazon 请求使用自适应限流器 `_AdaptiveRequestThrottle`：

- 检测 429、503、"too many requests"、"automated access" 等限流信号
- 动态调整请求间隔（退避策略）
- 失败时自动提取 Amazon cookie（session-id、ubid-acbjp）重试

简单说就是：被 Amazon 限制时就自动等一会儿再试，还会自动拿 cookie 重试。

## 使用场景

### 场景 1：首次查询新番号

1. 用户刮削一部新影片
2. 系统在 Excel 缓存中查找番号，未找到
3. 执行三层搜索策略
4. 成功获取封面后，保存到 Excel 缓存
5. 返回高清封面 URL

### 场景 2：重复查询已缓存番号

1. 用户再次刮削同一番号
2. 系统在 Excel 缓存中查找番号，找到记录
3. 直接返回缓存的 poster_url（转换为 SL1500）
4. 无需网络请求，速度极快

### 场景 3：缓存记录不完整

1. 用户查询一个已有缓存但缺少 poster_url 的番号
2. 系统检测到缓存命中但 poster_url 为空
3. 回退执行三层搜索策略
4. 获取到 poster_url 后更新缓存记录

## 配置选项

### Amazon 功能开关

在配置文件中可以控制 Amazon 功能的启用：

```json
{
  "amazon_enabled": true,
  "amazon_search_timeout": 30,
  "amazon_max_retries": 3
}
```

### 不走代理网站

Amazon 请求可以通过"不走代理网站"功能配置：

- 支持设置 `amazon` 或 `amazon.com` 作为不走代理的网站
- Amazon 请求将直接连接，不经过代理
- 提高请求速度和稳定性

## 性能优化

### 缓存命中率

- 首次查询：需要网络请求，耗时 5-30 秒
- 缓存命中：无需网络请求，耗时 <100ms
- 随着使用次数增加，缓存命中率提高，整体性能提升

### 搜索优化

- 条码快路径优先：条码匹配准确率高，速度快
- 多关键词并行搜索：提高标题搜索效率
- 置信度阈值过滤：避免低质量匹配

## 故障排查

### 常见问题

1. **缓存未命中**
   - 检查番号格式是否正确
   - 确认 Excel 文件未被损坏
   - 查看日志中的搜索过程

2. **搜索失败**
   - 检查网络连接
   - 确认 Amazon 服务可用性
   - 查看限流日志

3. **封面质量低**
   - 检查匹配置信度
   - 确认 ASIN 是否正确
   - 尝试手动更新缓存

### 日志位置

Amazon 相关日志位于：
- 主日志文件：`logs/mdcx.log`
- 调试日志：启用调试模式后查看详细搜索过程

## 相关文件

- `./mdcx/core/amazon.py` - Amazon 核心逻辑
- `./mdcx/core/amazon_database.py` - ASIN 数据库管理
- `./mdcx/base/web.py` - HTTP 请求层
- `./resources/userdata/amazon_asin_database.xlsx` - 缓存文件
