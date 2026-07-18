# 安装指南

## 系统要求

- **操作系统**：Windows 10+ / macOS 11+ / Linux（Ubuntu 20.04+、Debian 11+、CentOS 8+）
- **Python**：3.13.4 或更高版本（源码运行需要）
- **网络**：需要能访问数据源网站

## 方法一：用 Release 包（推荐）

去 [GitHub Releases](https://github.com/cdlongbow/mdcx/releases) 下载最新版：

| 系统 | 下载什么 |
|------|---------|
| Windows | `MDCx_win64.zip` |
| macOS (Intel) | `MDCx_macos_x64.zip` |
| macOS (Apple Silicon) | `MDCx_macos_arm64.zip` |
| Linux | `MDCx_linux_x64.zip` |

解压后双击运行即可。

## 方法二：从源码运行

```bash
# 1. 装 Python 3.13+
# 去 https://www.python.org/downloads/ 下载安装
# Windows 安装时记得勾 "Add Python to PATH"

# 2. 装 uv（Python 包管理器）
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 下载代码
git clone https://github.com/cdlongbow/mdcx.git
cd mdcx

# 4. 安装依赖
uv sync --dev

# 5. 启动
uv run python main.py
```

### Linux 额外步骤

```bash
# 装系统图形库，否则界面可能花屏
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

## 方法三：Docker

```bash
docker pull ...
docker run ...
```

## 遇到问题

- 界面太大或太小：设置 → 界面外观 → 缩放比例
- 网络不通：设置 → 网络 → 配置代理
- 其他：看 [USER_GUIDE.md](USER_GUIDE.md) 的常见问题部分