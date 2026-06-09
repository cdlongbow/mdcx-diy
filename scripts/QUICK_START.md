# TMDB ID 验证工具 - 快速开始

## 📦 安装依赖

```bash
# 在你的本地机器上执行
pip install openpyxl certifi

# 如果要用 GUI 界面（推荐）：
# Ubuntu/Debian:
sudo apt-get install python3-tk

# macOS:
brew install python-tk

# Windows: tkinter 已内置在 Python 中
```

## 🚀 使用方法

### 方法 1：GUI 界面（推荐）

```bash
cd /path/to/mdcx
python3 scripts/verify_actor_tmdb_gui.py
```

**操作步骤**：
1. 选择文件：`resources/userdata/actor_database.xlsx`
2. 点击"加载文件"
3. 点击"开始验证"
4. 等待完成（可暂停/停止）
5. 生成报告

### 方法 2：命令行模式

```bash
# 验证全部（约 5097 条，预计 1.5-2 小时）
python3 scripts/verify_actor_tmdb_gui.py resources/userdata/actor_database.xlsx

# 验证前 100 条样本（约 3-5 分钟）
python3 scripts/verify_actor_tmdb_gui.py resources/userdata/actor_database.xlsx 100
```

## 📊 验证结果

### Excel 中的标记

验证后 Excel 会增加 3 列：

| 列 | 标题 | 说明 |
|----|------|------|
| H | 验证状态 | ✅ 匹配 / ❌ 不匹配 / ⚠️ 无网络 |
| I | 验证结果 | TMDB 演员名字 |
| J | 验证日期 | 验证时间 |

### 生成的报告

位置：`resources/userdata/tmdb_verification_report_YYYYMMDD_HHMM.txt`

## 📝 下一步

验证完成后，告诉我：

1. **验证了多少条**：例如 "验证了 100 条"
2. **不匹配的数量**：从报告或 Excel 中查看
3. **不匹配的记录列表**：复制报告中的"❌ 不匹配记录"部分

我会根据你的反馈：
- 清除不匹配记录的 tmdbid
- 或者标记待验证记录
- 或者提供其他处理建议

## ⚙️ 高级选项

### 修改保存间隔

编辑 `scripts/verify_actor_tmdb_gui.py` 第 22 行：

```python
self.save_interval = 200  # 改为其他数字，例如 100
```

### 跳过已验证的记录

工具会自动跳过已验证的记录（状态列为 ✅ 或 ❌ 的），直接重新运行即可继续。

## 🆘 常见问题

**Q: 网络太慢怎么办？**
A: 可以先验证少量样本（如 50 条），看看匹配率如何。

**Q: 中途停止怎么办？**
A: 直接重新运行工具，会自动跳过已验证的记录。

**Q: 发现很多不匹配怎么办？**
A: 把报告发给我，我会帮你分析原因并处理。

**Q: 验证完成后如何处理不匹配的记录？**
A: 我会提供一个脚本来清除或标记这些记录。

---

**验证完成后，把报告内容发给我！** 📊
