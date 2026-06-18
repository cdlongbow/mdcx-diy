# MDCx 文档中心

## 新手入门

按此顺序阅读：

1. [快速开始](#快速开始) - 5 分钟上手
2. [用户使用手册](USER_GUIDE.md) - 完整使用说明
3. [使用场景和案例](SCENARIOS.md)
4. [FAQ](FAQ.md)

## 功能特色

- [功能特色](FEATURES.md)
- [完整功能列表](COMPLETE_FEATURES.md) - 42 个网站，全部功能
- [刮削模式详解](SCRAPING_MODES.md) - 正常模式、更新模式、读取模式
- [图片处理](COMPLETE_FEATURES.md#图片处理) - 人脸裁剪、水印、高清封面
- [多语言翻译](COMPLETE_FEATURES.md#多语言翻译) - 5 个翻译引擎
- [演员数据库管理](USER_GUIDE.md#演员数据库管理) - Excel 数据库 + TMDB
- [Emby/Jellyfin 集成](CODE_WIKI.md#emby-集成)

## 技术文档

- [Code Wiki](CODE_WIKI.md) - 完整技术文档
- [架构设计](architecture.md)
- [API 文档](api-documentation.md)
- [Amazon 缓存系统](amazon-cache.md) - 高清封面缓存
- [TMDB 缓存系统](tmdb-cache.md) - 演员 ID 缓存
- [开发指南](DEVELOPMENT.md)
- [核心模块](core-modules.md)
- [数据模型](data-models.md)
- [爬虫系统](crawler-system.md)
- [工具模块](tools.md)
- [依赖关系](dependencies.md)

## 配置参考

- [配置说明](configuration.md) - 全部配置项
- [网络配置](configuration.md#网络配置详解) - 代理和网站不走代理设置
- [命名系统](naming-system.md) - Jinja2 模板和命名规则

## 进阶使用

- [使用场景和案例](SCENARIOS.md) - 8 个详细场景
- [自动化工作流](SCENARIOS.md#场景-8自动化工作流) - 定时任务和全自动运行
- [工具模块](tools.md) - 内置工具使用说明

## 迁移和升级

- [PyQt6 迁移](pyqt6-migration.md) - 从 PyQt5 升级
- [爬虫迁移](crawler-migration.md) - 爬虫系统重构
- [变更日志](changelog.md)

## 代码质量

- [代码审查清单](CODE_REVIEW_CHECKLIST.md)
- [代码审查指南](CODE_REVIEW_GUIDE.md)
- [代码审查标准](CODE_REVIEW_STANDARDS.md)
- [测试覆盖率](TEST_COVERAGE_SUMMARY.md)

## 快速开始

### 5 分钟快速上手

1. **下载和安装**
   ```bash
   # 从 Release 下载编译好的版本
   # 或者从源码运行
   git clone https://github.com/cdlongbow/mdcx.git
   cd mdcx
   pip install -e .
   python main.py
   ```

2. **基本配置** - 设置媒体文件夹、选择抓取网站、配置下载选项
3. **开始使用** - 扫描媒体文件夹、勾选文件、点击开始抓取

详细步骤请看 [用户使用手册](USER_GUIDE.md)。

## 核心功能速览

| 模块 | 能力 |
|-----|------|
| **智能抓取** | 42 个网站、智能番号识别、多网站结果合并、异步并发 |
| **图片处理** | 多类型下载、人脸检测裁剪、Amazon 高清封面、自定义水印、图片修复 |
| **多语言翻译** | 5 个翻译引擎、字段级配置、映射表、降级策略 |
| **演员管理** | Excel 数据库、TMDB ID 补全、多语言信息、Emby 同步 |
| **媒体服务器集成** | 标准 NFO 生成、Emby/Jellyfin 同步、演员信息补全、头像同步 |

## 获取帮助

- [FAQ](FAQ.md)
- [使用场景](SCENARIOS.md)
- [Telegram 交流群](https://t.me/mdcx_chat)
- [GitHub Issues](https://github.com/cdlongbow/mdcx/issues)
- [GitHub Discussions](https://github.com/cdlongbow/mdcx/discussions)

### 贡献文档

1. 用 Markdown 格式
2. 保持清晰的章节结构
3. 提供代码示例
4. 及时更新过时内容
5. 保持与实际功能同步

## 外部资源

- [项目主页](https://github.com/cdlongbow/mdcx)
- [Release 页面](https://github.com/cdlongbow/mdcx/releases)
- [许可证](../LICENSE)
- [贡献指南](CONTRIBUTING.md)

**最后更新**: 2026-06-07
**文档版本**: v1.0