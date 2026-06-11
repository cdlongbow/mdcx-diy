# 开发

## 环境准备

### 依赖

* [uv](https://docs.astral.sh/uv/getting-started/installation/)

### clone

```bash
git clone https://github.com/sqzw-x/mdcx.git
cd mdcx
uv sync --all-extras --dev
uv run pre-commit install
uv pip install -e .
```

## Run

启动 qt 版本

```bash
uv run main.py
```

## Test

Python 侧使用 pytest

```bash
uv run pytest
```

## 如何添加新配置项

1. 在 `mdcx/config/models.py` `Config` 类中添加配置字段及默认值
2. 通过 `from mdcx.models.config.manager import manager` 导入配置, 并通过 `manager.config.<key>` 访问配置项
3. 按下一节所述在设置界面中添加对应的控件, 修改 `mdcx/controllers/main_window/` 目录下 `load_config.py` 及 `save_config.py`, 以实现 UI 绑定

## 如何修改图形界面

* `mdcx/views/MDCx.ui` 定义了主窗口, `mdcx/views/posterCutTool.ui` 是图片裁剪窗口, 可使用 Qt Designer 或 Qt Creator 编辑
* 修改后运行 `./scripts/pyuic.sh` 生成对应的 Python 代码
* 如需设置控件事件等, 需修改 `mdcx.controllers.main_window.init.Init_Singal`
* 所有事件处理函数均在 `mdcx/controllers/main_window/main_window.py` 及 `mdcx/controllers/main_window/handlers.py`

## 代码结构说明

```bash
mdcx
├── mdcx # 源代码目录
│ ├── base # 基础功能模块（文件、图片、视频、翻译）
│ ├── config # 配置管理
│ ├── controllers # Qt UI 控制器
│ │ └── main_window
│ ├── core # 核心功能（刮削、翻译、NFO、Amazon、命名）
│ ├── crawlers # 各网站爬虫（42+ 个站点）
│ ├── gen # 自动生成的枚举
│ ├── models # 数据模型
│ ├── tools # 工具模块（演员数据库、Emby、字幕）
│ ├── utils # 工具函数
│ └── views # Qt UI 定义
├── scripts # 开发/构建脚本
│   ├── build.py # 构建发布包
│   ├── bump.py # 版本号管理
│   ├── changelog.py # 生成变更日志
│   ├── check.py # 代码检查
│   └── pyuic.sh # 从 Qt UI 生成 Python 代码
└── tests # 测试
```
