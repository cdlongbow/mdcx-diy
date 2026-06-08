# MDCx 文档中心

欢迎使用 MDCx 技术文档！这里汇集了项目的所有文档资源，帮助您快速上手和深入了解 MDCx 的各项功能。

## 文档导航

### 🔰 新手入门

如果您是第一次使用 MDCx，建议按以下顺序阅读：

1. 📖 [快速开始](#快速开始) - 5 分钟快速上手
2. 📗 [用户使用手册](USER_GUIDE.md) - 完整的使用指南
3. 🎬 [使用场景和案例](SCENARIOS.md) - 实际操作案例
4. ❓ [FAQ](FAQ.md) - 常见问题解答

### ⭐ 功能特色

详细了解 MDCx 的强大功能：

- ⭐ [功能特色](FEATURES.md) - 详细的功能介绍和技术亮点
- 📋 [完整功能列表](COMPLETE_FEATURES.md) - 所有功能的完整列表（42 个网站）
- 🔄 [刮削模式详解](SCRAPING_MODES.md) - 正常模式、更新模式、读取模式详细说明
- 🎬 [智能刮削系统](COMPLETE_FEATURES.md#智能刮削系统) - 42 个网站爬虫支持
- 🖼️ [图片处理](COMPLETE_FEATURES.md#图片处理) - 人脸裁剪、水印、高清封面
- 🌐 [多语言翻译](COMPLETE_FEATURES.md#多语言翻译) - 5 大翻译引擎
- 🎭 [演员数据库管理](USER_GUIDE.md#演员数据库管理) - Excel 数据库 + TMDB 集成
- 🖥️ [Emby/Jellyfin 集成](CODE_WIKI.md#emby-集成) - 深度集成媒体服务器

### 🔧 技术文档

面向开发者和高级用户的技术文档：

- 📗 [Code Wiki](CODE_WIKI.md) - 完整的技术文档（1,150+ 行）
- 🏗️ [架构设计](architecture.md) - 系统架构和设计模式
- 📖 [API 文档](api-documentation.md) - 核心模块 API 参考
- 🛒 [Amazon 缓存系统](amazon-cache.md) - Amazon 高清封面缓存详解
- 🎬 [TMDB 缓存系统](tmdb-cache.md) - TMDB 演员 ID 缓存详解
- 🔧 [开发指南](DEVELOPMENT.md) - 开发环境搭建和最佳实践

### 📋 配置参考

详细的配置说明和选项：

- 📋 [配置说明](configuration.md) - 详细的配置项说明
- 🎯 [字段配置](configuration.md) - 字段级优先级和翻译配置
- 📝 [命名系统](naming-system.md) - Jinja2 模板和命名规则
- 🌐 [翻译配置](configuration.md) - 翻译引擎和映射表

### 🚀 进阶使用

高级功能和自动化：

- 🎬 [使用场景和案例](SCENARIOS.md) - 8 个详细的使用场景
- 🔄 [自动化工作流](SCENARIOS.md#场景-8自动化工作流) - 定时任务和完全自动化
- 🛠️ [工具模块](tools.md) - 内置工具使用指南

### 📖 迁移和升级

版本迁移和升级指南：

- 🔄 [PyQt6 迁移](pyqt6-migration.md) - 从 PyQt5 迁移到 PyQt6
- 🔄 [爬虫迁移](crawler-migration.md) - 爬虫系统重构和迁移
- 📝 [变更日志](changelog.md) - 版本更新历史

### ✅ 代码质量

面向贡献者的代码规范：

- ✅ [代码审查清单](CODE_REVIEW_CHECKLIST.md) - 代码审查检查项
- 📖 [代码审查指南](CODE_REVIEW_GUIDE.md) - 代码审查流程和规范
- 📋 [代码审查标准](CODE_REVIEW_STANDARDS.md) - 代码质量标准
- 🧪 [测试覆盖率](TEST_COVERAGE_SUMMARY.md) - 测试覆盖率摘要

---

## 文档分类

### 架构与设计

- [项目架构](architecture.md) - 系统架构、目录结构、分层设计
- [核心模块](core-modules.md) - 刮削器、文件爬虫、NFO 生成等核心功能
- [数据模型](data-models.md) - 数据类型定义、枚举、数据流转

### 配置与开发

- [配置系统](configuration.md) - 配置模型、配置管理器、配置迁移
- [爬虫系统](crawler-system.md) - 爬虫基类、爬虫注册、爬虫实现
- [工具模块](tools.md) - 演员数据库、Emby 集成、字幕管理等工具

### 功能详解

- [命名系统](naming-system.md) - Jinja2 模板引擎、字段定义、智能截断
- [依赖关系](dependencies.md) - 主要依赖、技术栈、网络层

### 迁移指南

- [PyQt6 迁移](pyqt6-migration.md) - 从 PyQt5 迁移到 PyQt6 的指南
- [爬虫迁移](crawler-migration.md) - 爬虫系统重构和迁移指南

---

## 🔍 快速查找

### 按主题查找

**刮削相关**
- [刮削系统](crawler-system.md) - 爬虫架构和实现
- [支持的网站](COMPLETE_FEATURES.md#完整网站列表) - 40+ 网站列表
- [番号识别](COMPLETE_FEATURES.md#智能刮削系统) - 智能番号识别

**演员相关**
- [演员数据库](tools.md) - Excel 数据库管理
- [TMDB 缓存系统](tmdb-cache.md) - TMDB 演员 ID 缓存详解
- [Emby 演员](CODE_WIKI.md#emby-集成) - Emby 演员信息同步

**翻译相关**
- [翻译引擎](FEATURES.md#多语言翻译系统) - 4 大翻译引擎配置
- [映射表](configuration.md) - 演员、制作商、标签映射
- [多语言](FEATURES.md#多语言翻译系统) - 多语言环境配置

**图片相关**
- [图片下载](COMPLETE_FEATURES.md#图片处理) - 海报、缩略图、背景图
- [图片处理](COMPLETE_FEATURES.md#图片处理) - 人脸裁剪、水印
- [Amazon 缓存系统](amazon-cache.md) - 高清封面缓存详解

**配置相关**
- [配置说明](configuration.md) - 详细配置项
- [命名模板](naming-system.md) - Jinja2 模板
- [字段配置](configuration.md) - 字段级优先级

### 按用户类型查找

**新手用户**
- [用户使用手册](USER_GUIDE.md) - 从零开始
- [使用场景](SCENARIOS.md) - 实际案例
- [FAQ](FAQ.md) - 常见问题

**高级用户**
- [功能特色](FEATURES.md) - 深入了解功能
- [配置说明](configuration.md) - 高级配置
- [自动化工作流](SCENARIOS.md#场景-8自动化工作流) - 自动化

**开发者**
- [开发指南](DEVELOPMENT.md) - 开发环境
- [架构设计](architecture.md) - 系统架构
- [API 文档](api-documentation.md) - API 参考

---

## 快速开始

### 5 分钟快速上手

1. **下载和安装**
   ```bash
   # 从 Release 下载预编译版本
   # 或从源码运行
   git clone https://github.com/cdlongbow/mdcx.git
   cd mdcx
   pip install -e .
   python main.py
   ```

2. **基本配置**
   - 设置媒体路径
   - 选择刮削网站
   - 配置下载选项

3. **开始使用**
   - 扫描媒体目录
   - 选择要刮削的文件
   - 点击开始刮削

详细步骤请参阅 [用户使用手册](USER_GUIDE.md)。

---

## 核心功能速览

### 智能刮削

- 🌐 40+ 网站支持
- 🏷️ 智能番号识别
- 🔄 多网站结果整合
- ⚡ 异步并发处理

### 图片处理

- 🖼️ 多类型图片下载
- 👤 人脸检测和裁剪
- 📸 Amazon 高清封面
- ✏️ 自定义水印

### 多语言翻译

- 🌐 4 大翻译引擎
- 📝 字段级配置
- 📋 映射表机制
- 🔄 降级策略

### 演员管理

- 📊 Excel 数据库
- 🎬 TMDB ID 自动补全
- 🌐 多语言信息
- 🖥️ Emby 同步

### 媒体服务器集成

- 📄 标准 NFO 生成
- 🖥️ Emby/Jellyfin 同步
- 🎭 演员信息补全
- 🖼️ 演员图片同步

---

## 获取帮助

### 文档资源

- 📖 [完整文档列表](#文档导航)
- ❓ [FAQ](FAQ.md) - 常见问题
- 🎬 [使用场景](SCENARIOS.md) - 实际案例

### 社区支持

- 💬 [Telegram 交流群](https://t.me/mdcx_chat) - 与其他用户交流
- 🐛 [GitHub Issues](https://github.com/cdlongbow/mdcx/issues) - 提交 Bug 和功能请求
- 📧 [GitHub Discussions](https://github.com/cdlongbow/mdcx/discussions) - 讨论和交流

### 贡献文档

欢迎贡献文档！请遵循以下规范：

1. ✅ 使用 Markdown 格式
2. 📝 保持清晰的章节结构
3. 💻 提供代码示例
4. 🔄 及时更新过时内容
5. 🎯 保持与实际功能同步

---

## 文档统计

| 文档类型 | 数量 | 总行数 |
|---------|------|--------|
| 用户文档 | 6 | 4,000+ |
| 技术文档 | 20 | 4,400+ |
| 开发文档 | 4 | 1,500+ |
| 总计 | 30 | 9,900+ |

---

## 外部资源

- 🏠 [项目主页](https://github.com/cdlongbow/mdcx)
- 📦 [Release 页面](https://github.com/cdlongbow/mdcx/releases)
- 📝 [许可证](../LICENSE)
- 🤝 [贡献指南](CONTRIBUTING.md)

---

**最后更新**: 2026-06-07
**文档版本**: v1.0
