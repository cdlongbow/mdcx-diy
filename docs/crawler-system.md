# 爬虫系统

> 本文档从 CODE_WIKI.md 提取,详见完整文档

---

## 爬虫基类 ([mdcx/crawlers/base/base.py](../mdcx/crawlers/base/base.py))

### `GenericBaseCrawler[T]`

泛型爬虫基类,所有具体爬虫均应继承此类并实现其抽象方法

**主要特性**:
- 支持自定义上下文类型
- 统一的爬虫生命周期管理
- 性能监控集成
- 爬虫健康监测集成
- 完善的错误处理

**主要方法**:
- `__init__(client, base_url)`:初始化爬虫
- `close()`:释放资源
- `site()`:返回此爬虫对应的网站枚举(抽象方法)
- `base_url_()`:返回默认 URL(抽象方法)
- `display_name()`:返回前端显示名称
- `new_context(input)`:创建新上下文(抽象方法)
- `run(input)`:执行爬虫任务
- `_run(ctx)`:内部执行逻辑
- `_generate_search_url(ctx)`:生成搜索 URL(抽象方法)
- `_search(ctx, search_urls)`:执行搜索
- `_parse_search_page(ctx, selector, search_url)`:解析搜索页(抽象方法)
- `_detail(ctx, detail_urls)`:获取详情页
- `_parse_detail_page(ctx, selector, detail_url)`:解析详情页(抽象方法)
- `post_process(ctx, data)`:后处理

**爬虫生命周期**:
1. 初始化爬虫实例
2. 创建上下文
3. 生成搜索 URL(或使用指定 URL)
4. 请求搜索页
5. 解析搜索页,获取详情页 URL
6. 请求详情页
7. 解析详情页,获取数据
8. 后处理
9. 返回结果

## 爬虫注册与获取

**主要机制**:
- 装饰器模式注册爬虫
- 工厂模式获取爬虫实例
- 懒加载优化性能

## 爬虫实现目录 ([mdcx/crawlers/](../mdcx/crawlers/))

每个网站一个爬虫文件,共 42+ 个站点

**支持的网站**:
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
- ThePornDB
- X-City

**添加新爬虫的步骤**:
1. 在 `mdcx/crawlers/` 下创建新文件
2. 继承 `BaseCrawler`(或 `GenericBaseCrawler`)
3. 实现抽象方法
4. 使用 `@register_crawler` 装饰器注册
5. 在 `Website` 枚举中添加对应网站

---

## 相关文档

- [项目架构](architecture.md) - 项目整体架构
- [核心模块](core-modules.md) - 核心功能模块详解
- [数据模型](data-models.md) - 数据结构定义
- [配置系统](configuration.md) - 配置管理详解
- [工具模块](tools.md) - 工具模块详解
