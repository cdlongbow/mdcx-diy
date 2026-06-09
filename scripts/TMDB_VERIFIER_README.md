# TMDB ID 验证工具使用说明

## 🎯 功能特性

- ✅ **图形界面**：实时显示验证进度和统计
- ✅ **断点续传**：验证中断后可继续（自动跳过已验证的记录）
- ✅ **自动保存**：每 200 条记录自动保存一次
- ✅ **状态标记**：在 Excel 中自动标记验证状态（颜色区分）
- ✅ **详细报告**：生成文本报告，便于后续处理

## 🚀 使用方法

### 方式 1：GUI 界面（推荐）

```bash
python3 scripts/verify_actor_tmdb_gui.py
```

**操作步骤**：

1. 打开工具后，点击"浏览..."选择 `resources/userdata/actor_database.xlsx`
2. 点击"加载文件"，工具会自动扫描需要验证的记录
3. 点击"▶️ 开始验证"开始验证
4. 验证过程中可以"⏸️ 暂停"或"⏹️ 停止"
5. 验证完成后点击"📊 生成报告"

**验证状态说明**：

| 状态 | 颜色 | 含义 |
|------|------|------|
| ✅ 匹配 | 绿色 | TMDB ID 对应的演员名字与 Excel 中的一致 |
| ❌ 不匹配 | 红色 | TMDB ID 对应的演员名字不一致（需要修正） |
| ⚠️ 无网络 | 黄色 | 网络错误，稍后重试 |
| 🔴 错误 | 默认色 | 其他错误（如 TMDB ID 不存在） |

### 方式 2：命令行模式

```bash
# 验证所有记录（带进度显示）
python3 scripts/verify_actor_tmdb_gui.py resources/userdata/actor_database.xlsx

# 验证前 100 条样本
python3 scripts/verify_actor_tmdb_gui.py resources/userdata/actor_database.xlsx 100
```

## 📊 Excel 自动标记

验证后，Excel 会增加以下列：

| 列 | 名称 | 说明 |
|----|------|------|
| H | 验证状态 | ✅ 匹配 / ❌ 不匹配 / ⚠️ 无网络 / 🔴 错误 |
| I | 验证结果 | TMDB 演员名字或错误信息 |
| J | 验证日期 | 验证时间（YYYY-MM-DD HH:MM） |

## 📝 验证报告

报告文件保存在 `resources/userdata/` 目录下，文件名格式：
```
tmdb_verification_report_YYYYMMDD_HHMM.txt
```

报告包含：
- 验证统计数据
- 不匹配记录列表（带行号和 TMDB ID）
- 错误记录列表

## 📋 后续处理

验证完成后，检查报告中的**不匹配记录**，告诉我以下信息：

1. **不匹配记录数**：从报告或 Excel 中查看 `❌ 不匹配` 的数量
2. **处理方式**：
   - 选项 A：清除所有不匹配记录的 tmdbid（置空）
   - 选项 B：只保留标记为待验证的记录
   - 选项 C：手动修正部分重要记录

## 🔧 注意事项

1. **网络要求**：需要能访问 `www.themoviedb.org`
2. **验证时长**：全量验证（约 5097 条）预计需要 1.5-2 小时
3. **断点续传**：如果中断，直接重新运行工具即可继续
4. **备份建议**：验证前建议备份 Excel 文件

## 🐛 故障排除

### 问题 1：无法连接 TMDB

```
错误：URLError: <urlopen error [Errno 111] Connection refused>
```

**解决**：
- 检查网络连接
- 尝试使用代理
- 稍后重试

### 问题 2：缺少 tkinter

```
ImportError: No module named 'tkinter'
```

**解决**：
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# 或使用命令行模式（不需要 tkinter）
python3 scripts/verify_actor_tmdb_gui.py resources/userdata/actor_database.xlsx
```

### 问题 3：Excel 文件被锁定

```
PermissionError: [Errno 13] Permission denied
```

**解决**：
- 关闭 Excel 文件
- 确保没有其他程序打开该文件

---

**验证完成后，将报告内容发给我，我会帮你处理不匹配的记录。**
