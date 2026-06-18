# 项目架构

> 本文档从 CODE_WIKI.md 提取，详见完整文档

---

## 目录结构

这是项目文件的完整布局。每个文件和文件夹各司其职：

```
./
├── main.py                         # 程序入口
├── pyproject.toml                  # 项目配置和依赖管理
├── mdcx/                           # 主源码目录
│   ├── __init__.py
│   ├── consts.py                    # 常量定义（版本号、平台检测等）
│   ├── crawler.py                   # 爬虫提供器
│   ├── number.py                    # 番号解析和验证
│   ├── signals.py                   # 信号机制(Qt 信号)
│   ├── web_async.py                 # 异步网络客户端
│   ├── browser.py                   # 浏览器相关模块
│   ├── llm.py                       # LLM 翻译核心实现
│   ├── manual.py                    # 手动操作模块
│   ├── image.py                     # 顶层图片模块
│   ├── network_fingerprint.py       # 网络指纹模块
│   ├── base/                        # 基础功能模块
│   │   ├── file.py                  # 文件操作
│   │   ├── image.py                 # 图片处理
│   │   ├── number.py                # 番号解析
│   │   ├── translate.py             # 翻译功能
│   │   ├── video.py                 # 视频处理
│   │   ├── web.py                   # 网络请求
│   │   └── web_sync.py              # Web 同步操作
│   ├── config/                      # 配置管理
│   │   ├── computed.py              # 计算属性
│   │   ├── enums.py                 # 配置枚举
│   │   ├── extend.py                # 扩展配置
│   │   ├── manager.py               # 配置管理器
│   │   ├── migrations.py            # 配置迁移
│   │   ├── models.py                # 配置模型
│   │   ├── resource_policy.py       # 资源策略
│   │   ├── resources.py             # 资源管理（含演员/信息数据库 xlsx 加载）
│   │   └── v1.py                    # V1 配置兼容
│   ├── controllers/                 # 控制器(业务逻辑)
│   │   ├── cut_window.py            # 裁剪窗口控制器
│   │   └── main_window/             # 主窗口控制器
│   │       ├── init.py              # 初始化
│   │       ├── main_window.py       # 主窗口逻辑
│   │       ├── handlers.py          # 事件处理
│   │       ├── bind_utils.py        # 绑定工具
│   │       ├── load_config.py       # 加载配置
│   │       ├── save_config.py       # 保存配置
│   │       ├── site_priority_dialog.py  # 站点优先级对话框
│   │       └── style.py             # 样式设置
│   ├── core/                        # 核心功能
│   │   ├── amazon.py                # Amazon 集成
│   │   ├── amazon_database.py       # Amazon 数据库缓存
│   │   ├── face_crop.py             # 人脸裁剪
│   │   ├── file.py                  # 文件处理
│   │   ├── file_crawler.py          # 文件刮削
│   │   ├── image.py                 # 图片处理
│   │   ├── media_resource.py        # 媒体资源
│   │   ├── mosaic.py                # 马赛克处理
│   │   ├── naming/                  # 命名系统
│   │   │   ├── fields.py            # 命名字段
│   │   │   ├── renderer.py          # 渲染器
│   │   │   ├── sanitize.py          # 清理
│   │   │   └── template.py          # 模板
│   │   ├── network_check.py         # 网络检查
│   │   ├── nfo.py                   # NFO 生成
│   │   ├── scraper.py               # 刮削器
│   │   ├── tag_priority.py          # 标签优先级
│   │   ├── tmdb_actor.py            # TMDB 演员
│   │   ├── translate.py             # 翻译
│   │   ├── utils.py                 # 工具函数
│   │   └── web.py                   # Web 操作
│   ├── crawlers/                    # 爬虫实现
│   │   ├── base/                    # 爬虫基类
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # 基础爬虫类
│   │   │   ├── parser.py            # 解析器
│   │   │   └── types.py             # 类型定义
│   │   ├── airav_cc.py              # Airav.cc 爬虫
│   │   ├── avbase_new.py            # AVBase 爬虫
│   │   ├── avsex.py                 # AVSex 爬虫
│   │   ├── avsox.py                 # AVSoX 爬虫
│   │   ├── cableav.py               # CableAV 爬虫
│   │   ├── cnmdb.py                 # CNMDB 爬虫
│   │   ├── dahlia.py                # Dahlia 爬虫
│   │   ├── dmm_new/                 # DMM 爬虫
│   │   ├── faleno.py                # Faleno 爬虫
│   │   ├── fantastica.py            # Fantastica 爬虫
│   │   ├── fc2.py                   # FC2 爬虫
│   │   ├── fc2club.py               # FC2Club 爬虫
│   │   ├── fc2hub.py                # FC2Hub 爬虫
│   │   ├── fc2ppvdb.py              # FC2PPVDB 爬虫
│   │   ├── freejavbt.py             # FreeJAVBT 爬虫
│   │   ├── getchu.py                # Getchu 爬虫
│   │   ├── getchu_dl.py             # Getchu 下载站爬虫
│   │   ├── getchu_dmm.py            # Getchu DMM 爬虫
│   │   ├── giga.py                  # Giga 爬虫
│   │   ├── guochan.py               # 国产爬虫
│   │   ├── hdouban.py               # 豆瓣爬虫
│   │   ├── hscangku.py              # 红色仓库爬虫
│   │   ├── iqqtv.py                 # IQQTV 爬虫
│   │   ├── jav321.py                # Jav321 爬虫
│   │   ├── javbus.py                # JavBus 爬虫
│   │   ├── javday.py                # JavDay 爬虫
│   │   ├── javdb_new.py             # JavDB 爬虫
│   │   ├── javdbapi.py              # JavDB API 爬虫
│   │   ├── javlibrary.py            # JavLibrary 爬虫
│   │   ├── kin8.py                  # Kin8 爬虫
│   │   ├── libredmm.py              # LibreDMM 爬虫
│   │   ├── love6.py                 # Love6 爬虫
│   │   ├── lulubar.py               # 芦芦吧爬虫
│   │   ├── madouqu.py               # 马豆区爬虫
│   │   ├── mdtv.py                  # MDTV 爬虫
│   │   ├── mgstage.py               # MGStage 爬虫
│   │   ├── missav.py                # MissAV 爬虫
│   │   ├── mmtv.py                  # MMTV 爬虫
│   │   ├── mywife.py                # MyWife 爬虫
│   │   ├── official.py              # 官方站点爬虫
│   │   ├── prestige.py              # Prestige 爬虫
│   │   ├── theporndb.py             # ThePornDB 爬虫
│   │   └── xcity.py                 # X-City 爬虫
│   ├── gen/                         # 自动生成的枚举
│   ├── models/                      # 数据模型
│   │   ├── emby.py                  # Emby 模型
│   │   ├── enums.py                 # 枚举
│   │   ├── flags.py                 # 标志
│   │   ├── log_buffer.py            # 日志缓冲
│   │   └── types.py                 # 类型定义
│   ├── tools/                       # 工具模块
│   │   ├── actress_db.py            # 演员数据库
│   │   ├── emby_actor_image.py      # Emby 演员图片
│   │   ├── emby_actor_info.py       # Emby 演员信息
│   │   ├── missing.py               # 缺失文件检测
│   │   ├── subtitle.py              # 字幕管理
│   │   └── wiki.py                  # Wiki 工具
│   ├── utils/                       # 工具函数
│   │   ├── dataclass.py             # 数据类工具
│   │   ├── file.py                  # 文件工具
│   │   ├── gather_group.py          # 分组工具
│   │   ├── language.py              # 语言工具
│   │   ├── path.py                  # 路径工具
│   │   └── video.py                 # 视频工具
│   └── views/                       # UI 视图
│       ├── CustomClass.py           # 自定义类
│       ├── MDCx.py                  # 主视图
│       ├── MDCx.ui                  # 主窗口 UI 定义
│       ├── posterCutTool.py         # 海报裁剪工具
│       └── posterCutTool.ui         # 海报裁剪窗口 UI 定义
├── resources/                       # 资源文件
│   ├── config/                      # 默认配置
│   ├── c_number/                    # C 番号数据
│   ├── fonts/                       # 字体
│   ├── mapping_table/               # 映射表
│   └── userdata/                    # 用户数据
│       └── actor_database.xlsx      # 演员数据库
├── scripts/                         # 脚本工具
├── tests/                           # 测试代码
└── docs/                            # 项目文档
```

## 架构分层

MDCx 采用经典的 MVC（Model-View-Controller，模型-视图-控制器）分层架构。简单说就是：界面只管显示，控制器管业务逻辑，核心模块管具体干活，各层互不干扰。

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (PyQt6)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ MainWindow   │  │ SettingsUI   │  │ ProgressUI   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Controller Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ EventHandler │  │ ConfigMgr    │  │ SignalBus    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Business Logic                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Scraper     │  │ FileCrawler  │  │ NamingSystem │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   NFO Gen    │  │  Amazon OCR  │  │  Translator  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ TMDb Actor   │  │ Image Proc   │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Crawler Framework                         │
│  ┌──────────────────────────────────────────────────┐      │
│  │              GenericBaseCrawler[T]                │      │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐│      │
│  │  │ JAVBus │  │JavLib  │  │  DMM   │  │  FC2   ││      │
│  │  └────────┘  └────────┘  └────────┘  └────────┘│      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ HTTP Client  │  │ File System  │  │ Image Proc   │     │
│  │ (httpx)      │  │ (asyncio)    │  │ (OpenCV)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

各层的作用：

- **UI 层**（最上面）：用户看到的窗口界面，用 PyQt6 实现。负责展示数据和接收用户操作。
- **控制器层**：搭桥的中间人。用户点了按钮，控制器负责安排谁去干活，把结果送回界面。
- **核心业务层**：真正的干活模块。刮削视频信息、下载图片、生成 NFO 文件等都在这里。
- **爬虫框架**：从各网站抓取数据的统一框架。所有爬虫都遵循相同的模式，方便新增。
- **基础设施层**（最下面）：底层能力，比如发 HTTP 请求、读写文件、处理图片的工具。

## 主要模块依赖关系

程序启动后的调用链条如下：

```
main.py
  └─> controllers/main_window/
        └─> core/scraper.py
              ├─> crawler.py
              │     └─> crawlers/
              ├─> core/file_crawler.py
              ├─> core/nfo.py
              ├─> core/media_resource.py
              ├─> core/translate.py
              └─> config/manager.py
```

## 数据流程

整个刮削流程分 9 步走：

1. **文件扫描**:FileCrawler 扫描媒体目录，识别视频文件
2. **番号识别**:从文件名中提取番号，识别马赛克类型
3. **爬虫执行**:根据配置调用相应网站的爬虫
4. **数据整合**:整合多个网站的结果，应用字段优先级
5. **翻译处理**:根据配置翻译元数据
6. **命名生成**:应用命名模板生成新的文件名和目录名
7. **资源下载**:下载海报、缩略图、背景图、预告片等
8. **元数据写入**:生成 NFO 文件
9. **文件移动**:移动和重命名文件到目标位置

---


简单说就是：程序先找到视频文件，认出它的番号，然后去各个网站搜刮信息，把结果合并排序，翻译成目标语言，按照规则重命名文件，最后把封面、简介等元数据写好存盘。

## 相关文档

- [核心模块](core-modules.md) - 核心功能模块详解
- [数据模型](data-models.md) - 数据结构定义
- [配置系统](configuration.md) - 配置管理详解
- [爬虫系统](crawler-system.md) - 爬虫框架详解
- [命名系统](naming-system.md) - 命名规则详解
- [依赖关系](dependencies.md) - 项目依赖说明
