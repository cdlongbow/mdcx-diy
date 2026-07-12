# 开发

## 开始之前

### 需要安装的工具

* [uv](https://docs.astral.sh/uv/getting-started/installation/) 包管理器

### 克隆代码并安装依赖

```bash
git clone https://github.com/cdlongbow/mdcx.git
cd mdcx
uv sync --dev
uv run pre-commit install
uv pip install -e .
```

## 启动程序

启动 qt 版本

```bash
uv run main.py
```

## 运行测试

Python 这边用 pytest

```bash
uv run pytest
```

## 如何添加新配置项

1. 在 `mdcx/config/models.py` 的 `Config` 类里加上配置字段和默认值
2. 通过 `from mdcx.models.config.manager import manager` 导入配置，然后用 `manager.config.<key>` 读取配置项
3. 在设置界面中添加对应的控件，修改 `mdcx/controllers/main_window/` 目录下的 `load_config.py` 和 `save_config.py`，让界面和配置关联起来

## 如何修改图形界面

* `mdcx/views/MDCx.ui` 是主窗口，`mdcx/views/posterCutTool.ui` 是图片裁剪窗口，可以用 Qt Designer 或 Qt Creator 编辑
* 改完后执行 `./scripts/pyuic.sh` 生成对应的 Python 代码
* 如果要设置控件的事件处理，需要改 `mdcx.controllers.main_window.init.Init_Singal`
* 所有事件处理函数都在 `mdcx/controllers/main_window/main_window.py` 和 `mdcx/controllers/main_window/handlers.py` 里

## 代码结构说明

```bash
mdcx
├── base                 # 基础功能模块（文件、图片、视频、翻译）
├── config               # 配置管理
├── controllers          # Qt UI 控制器
│   └── main_window
├── core                 # 核心功能（刮削、翻译、NFO、Amazon、命名）
├── crawlers             # 各网站爬虫（40+ 个站点）
├── gen                  # 自动生成的枚举
├── models               # 数据模型
├── tools                # 工具模块（演员数据库、Emby、字幕）
├── utils                # 工具函数
└── views                # Qt UI 定义
scripts                  # 开发/构建脚本
├── build.py             # 构建发布包
├── bump.py              # 版本号管理
├── changelog.py         # 生成变更日志
├── check.py             # 代码检查
└── pyuic.sh             # 从 Qt UI 生成 Python 代码
tests                    # 测试
```