# 爬虫系统

> 本文档从 CODE_WIKI.md 提取,详见完整文档

---

## 爬虫基类（[mdcx/crawlers/base/base.py](../mdcx/crawlers/base/base.py)）

### `GenericBaseCrawler[T]`

泛型爬虫基类。所有具体爬虫都要继承这个类，并实现它定义的抽象方法。

**主要特性**：
- 支持自定义上下文类型
- 统一的爬虫生命周期管理
- 完善的错误处理

**主要方法**：
- `__init__(client, base_url)`：初始化爬虫
- `close()`：释放资源
- `site()`：返回此爬虫对应的网站枚举（抽象方法）
- `base_url_()`：返回默认 URL（抽象方法）
- `display_name()`：返回前端显示名称
- `new_context(input)`：创建新上下文（抽象方法）
- `run(input)`：执行爬虫任务
- `_run(ctx)`：内部执行逻辑
- `_generate_search_url(ctx)`：生成搜索 URL（抽象方法）
- `_search(ctx, search_urls)`：执行搜索
- `_parse_search_page(ctx, selector, search_url)`：解析搜索页（抽象方法）
- `_detail(ctx, detail_urls)`：获取详情页
- `_parse_detail_page(ctx, selector, detail_url)`：解析详情页（抽象方法）
- `post_process(ctx, data)`：后处理

**爬虫生命周期**：
1. 初始化爬虫实例
2. 创建上下文
3. 生成搜索 URL（或使用指定 URL）
4. 请求搜索页
5. 解析搜索页，获取详情页 URL
6. 请求详情页
7. 解析详情页，获取数据
8. 后处理
9. 返回结果

## 爬虫注册与获取

**主要机制**：
- 通过 `register_crawler()` 函数注册
- 通过 `get_crawler()` 查询注册表获取爬虫类
- 子类定义后通过 `__init_subclass__` 自动注册到 `crawler_registry`
- 站点下拉框由注册表通过 `get_registered_crawler_site_values()` 动态生成（当前共 45 个已注册爬虫）

## 爬虫实现目录（[mdcx/crawlers/](../mdcx/crawlers/)）

每个网站一个爬虫文件，共 45 个已注册站点（具体以代码注册为准，下拉框由注册表动态生成）。

**支持的网站**：
- Airav.cc
- AVBase
- AVSex
- AVSoX
- CableAV
- CNMDB
- Dahlia
- DMM
- Faleno
- Fantastica
- FC2
- FC2Club
- FC2Hub
- FC2PPVDB
- FreeJAVBT
- Getchu
- Getchu DL
- Getchu DMM
- Giga
- 国产
- 豆瓣
- 红色仓库
- IQQTV
- Jav321
- JavBus
- JavDay
- JavDB
- JavDB API
- JavLibrary
- Kin8
- LibreDMM
- Love6
- 芦芦吧
- 马豆区
- MDTV
- MGStage
- MissAV
- MMTV
- MyWife
- Prestige
- R18.dev
- ThePornDB
- X-City

**添加新爬虫的步骤**：
1. 在 `mdcx/crawlers/` 下创建新文件
2. 继承 `BaseCrawler`（或 `GenericBaseCrawler`）
3. 实现抽象方法
4. 在 `mdcx/crawlers/__init__.py` 中导入并通过 `register_crawler()` 注册
5. 在 `Website` 枚举中添加对应网站

---

## 相关文档

- [项目架构](architecture.md)
- [核心模块](core-modules.md)
- [数据模型](data-models.md)
- [配置系统](configuration.md)
- [工具模块](tools.md)
