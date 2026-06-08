# 安装指南

本文档介绍 MDCX 的安装步骤和系统要求。

## 系统要求

### 操作系统
- Windows 10 或更高版本
- Linux（Ubuntu 20.04+, Debian 11+, CentOS 8+）
- macOS 11 或更高版本

### Python 环境
- Python 3.13 或更高版本
- pip 包管理器

### 依赖项
- PyQt6（GUI 框架）
- openpyxl（Excel 文件处理）
- requests（HTTP 请求）
- lxml（HTML/XML 解析）
- Pillow（图像处理）

## 安装步骤

### Windows

1. **安装 Python**
   ```powershell
   # 从 https://www.python.org/downloads/ 下载并安装 Python 3.13+
   # 安装时勾选 "Add Python to PATH"
   ```

2. **克隆仓库**
   ```powershell
   git clone https://github.com/cdlongbow/mdcx.git
   cd mdcx
   ```

3. **安装依赖**
   ```powershell
   pip install -e .
   ```

4. **运行程序**
   ```powershell
   python main.py
   ```

### Linux

1. **安装系统依赖**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv libxcb-xinerama0

   # CentOS/RHEL
   sudo yum install python3 python3-pip libxcb-xinerama0
   ```

2. **克隆仓库**
   ```bash
   git clone https://github.com/cdlongbow/mdcx.git
   cd mdcx
   ```

3. **创建虚拟环境（推荐）**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **安装依赖**
   ```bash
   pip install -e .
   ```

5. **运行程序**
   ```bash
   python main.py
   ```

### macOS

1. **安装 Python**
   ```bash
   # 使用 Homebrew
   brew install python@3.13
   ```

2. **克隆仓库**
   ```bash
   git clone https://github.com/cdlongbow/mdcx.git
   cd mdcx
   ```

3. **创建虚拟环境（推荐）**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **安装依赖**
   ```bash
   pip install -e .
   ```

5. **运行程序**
   ```bash
   python main.py
   ```

## 配置

首次运行时，程序会自动创建配置文件。详细配置说明请参阅 [配置说明文档](configuration.md)。

## 常见问题

### PyQt6 导入错误

如果遇到 PyQt6 导入错误，请先确认当前环境已安装 PyQt6：

```bash
pip install PyQt6
```

### 权限问题（Linux/macOS）

如果遇到权限问题，尝试：

```bash
chmod +x main.py
```

### 缺少系统库（Linux）

如果遇到 GUI 相关错误，安装额外的系统库：

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# CentOS/RHEL
sudo yum install libxcb-xinerama0 libxcb-cursor0
```

## 卸载

1. 删除项目目录
2. 如果使用了虚拟环境，删除虚拟环境目录
3. （可选）删除用户配置目录（通常在 `~/.mdcx`）

## 更新

```bash
git pull origin main
pip install -e . --upgrade
```

## 下一步

- 阅读 [用户使用手册](USER_GUIDE.md) 了解如何使用程序
- 查看 [配置说明](configuration.md) 了解各项配置选项
- 遇到问题时查看 [FAQ](FAQ.md)

## 获取帮助

如有问题，请：
- 查看 [FAQ](FAQ.md)
- 在 GitHub 上提交 Issue
- 访问项目 Wiki 获取更多信息
