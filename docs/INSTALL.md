# 安装指南

跟着下面的步骤，你就能在自己的电脑上装好 MDCX。

## 你需要准备什么

### 操作系统
- Windows 10 或更新的版本
- Linux（推荐 Ubuntu 20.04+、Debian 11+、CentOS 8+）
- macOS 11 或更新的版本

### Python 环境
- Python 3.13.4 或更新的版本
- [uv](https://docs.astral.sh/uv/getting-started/installation/) 包管理器（用来安装和管理依赖）

### 程序要用到的软件包
- PyQt6（程序界面框架）
- httpx / curl-cffi（发送网络请求）
- openpyxl（读写 Excel 文件）
- lxml / parsel / beautifulsoup4（解析网页内容）
- Pillow / OpenCV（处理图片）

---

## 安装步骤

### Windows

1. **装 Python**
```powershell
# 去 https://www.python.org/downloads/ 下载 Python 3.13 或更新的版本
# 安装时记得勾上 "Add Python to PATH"
```

2. **装 uv**
```powershell
# 打开 PowerShell，运行这一行
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. **下载项目代码**
```powershell
git clone https://github.com/sqzw-x/mdcx.git
cd mdcx
```

4. **安装依赖**
```powershell
uv sync --all-extras --dev
uv pip install -e .
```

5. **启动程序**
```powershell
uv run main.py
```

---

### Linux

1. **装系统需要的库**
```bash
# 如果你用的是 Ubuntu 或 Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv libxcb-xinerama0

# 如果你用的是 CentOS 或 RHEL
sudo yum install python3 python3-pip libxcb-xinerama0
```

2. **装 uv**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **下载项目代码**
```bash
git clone https://github.com/sqzw-x/mdcx.git
cd mdcx
```

4. **安装依赖**
```bash
uv sync --all-extras --dev
uv pip install -e .
```

5. **启动程序**
```bash
uv run main.py
```

---

### macOS

1. **装 Python**
```bash
# 推荐用 Homebrew 安装
brew install python@3.13
```

2. **装 uv**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **下载项目代码**
```bash
git clone https://github.com/sqzw-x/mdcx.git
cd mdcx
```

4. **安装依赖**
```bash
uv sync --all-extras --dev
uv pip install -e .
```

5. **启动程序**
```bash
uv run main.py
```

---

## 配置

第一次启动时，程序会自动生成配置文件。想了解详细的配置项，请看[配置说明文档](configuration.md)。

## 常见问题

### 装 PyQt6 时出错

如果提示 PyQt6 相关的错误，手动装一下：

```bash
pip install PyQt6
uv pip install PyQt6
```

### 提示权限不够（Linux/macOS）

给程序文件加个执行权限：

```bash
chmod +x main.py
```

### 缺系统库（Linux）

如果界面显示不正常，补装几个库：

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# CentOS/RHEL
sudo yum install libxcb-xinerama0 libxcb-cursor0
```

## 卸载

1. 删除项目文件夹
2. 如果你用了虚拟环境，把虚拟环境文件夹也删掉
3. （可选）删除用户配置目录（一般在 `~/.mdcx`）

## 更新到最新版

```bash
git pull origin main
uv sync --all-extras --dev
```

## 下一步

- 阅读[用户使用手册](USER_GUIDE.md)，了解程序怎么用
- 查看[配置说明](configuration.md)，了解各项设置
- 遇到问题先看看[FAQ](FAQ.md)

## 获取帮助

如果还有问题：
- 查看[FAQ](FAQ.md)
- 在 GitHub 上提交 Issue
- 访问项目 Wiki 获取更多信息