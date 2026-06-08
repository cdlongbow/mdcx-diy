# 常见问题解答 (FAQ)

本文档收集了 MDCX 使用过程中的常见问题和解决方案。

## 安装和运行

### Q: 安装时提示 "No module named 'PyQt6'" 怎么办？

**A**: 安装 PyQt6 或改用 PyQt5：

```bash
# 方案 1: 安装 PyQt6
pip install PyQt6

# 方案 2: 安装 PyQt5
pip install PyQt5
```

### Q: Linux 上 GUI 无法显示或显示异常？

**A**: 安装缺失的系统库：

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# CentOS/RHEL
sudo yum install libxcb-xinerama0 libxcb-cursor0

# 设置环境变量
export QT_QPA_PLATFORM=xcb
```

### Q: 如何确定需要哪个版本的 Python？

**A**: MDCX 需要 Python 3.8 或更高版本：

```bash
python --version
# 或
python3 --version
```

### Q: macOS 上运行报 "Python is not installed" 错误？

**A**: macOS 可能需要通过 Homebrew 安装 Python：

```bash
brew install python@3.8
```

## 数据库管理

### Q: 数据库文件在哪里？

**A**: 默认位置：
- Windows: `userdata/actor_database.xlsx`
- Linux/macOS: `userdata/actor_database.xlsx`

### Q: 如何备份数据库？

**A**:
1. 复制 `actor_database.xlsx` 文件到安全位置
2. 建议同时备份 `amazon_asin_database.xlsx` 等用户数据文件

### Q: 数据库损坏了怎么办？

**A**:
1. 使用最近的备份文件恢复
2. 如果没有备份，尝试 Excel 的修复功能
3. 联系开发者寻求帮助

### Q: 可以使用其他格式的数据库吗？

**A**: 目前仅支持 Excel (.xlsx) 格式，未来计划支持 CSV 和 SQLite。

### Q: 如何恢复删除的演员数据？

**A**: 如果在删除前做了备份，可以从备份恢复。否则无法恢复，请谨慎操作。

## TMDB 数据刮削

### Q: TMDB API Key 如何获取？

**A**:
1. 访问 https://www.themoviedb.org/
2. 注册账号
3. 进入设置页面申请 API Key
4. 在程序设置中填入 Key

### Q: TMDB 刮削时频繁出现 429 错误？

**A**: TMDB API 有速率限制（约 4 req/s），解决方法：
- 降低并发数（建议 3）
- 启用令牌桶限流（默认 3.5 req/s）
- 等待一段时间后重试

### Q: 批量刮削速度很慢？

**A**:
- 增加 TMDB API 速率限制（注意不要超过限制）
- 适当提高并发数（但不要太高）
- 确保网络连接稳定

### Q: TMDB 匹配不到演员怎么办？

**A**:
- 尝试使用不同的搜索词（日文名、别名）
- 检查演员名称是否正确
- 手动在 TMDB 网站上搜索确认
- 该演员可能不在 TMDB 数据库中

### Q: TMDB 数据不准确？

**A**:
- TMDB 数据由用户贡献，可能存在错误
- 可以在 TMDB 网站上提交更正
- 或手动编辑数据库中的信息

## 配置和设置

### Q: 配置文件在哪里？

**A**:
- Windows: `%APPDATA%/mdcx/config.ini` 或 `~/.config/mdcx/config.ini`
- Linux: `~/.config/mdcx/config.ini`
- macOS: `~/Library/Application Support/mdcx/config.ini`

### Q: 如何重置配置？

**A**:
1. 关闭程序
2. 删除配置文件
3. 重新启动程序（会使用默认配置）

### Q: 修改配置后需要重启程序吗？

**A**: 大部分配置修改后立即生效，但某些配置可能需要重启。

## 性能和优化

### Q: 程序运行缓慢怎么办？

**A**:
- 关闭不必要的后台程序
- 增加系统内存
- 清理数据库（删除不需要的条目）
- 更新到最新版本

### Q: 内存占用过高？

**A**:
- 减少并发刮削数
- 定期清理缓存
- 重启程序释放内存

### Q: 数据库文件太大？

**A**:
- 使用格式化功能清理无效数据
- 删除不需要的演员信息
- 压缩数据库文件

## Emby/Jellyfin 集成

### Q: 如何配置 Emby/Jellyfin 集成？

**A**:
1. 在设置中输入 Emby/Jellyfin 服务器地址
2. 配置 API Key
3. 启用自动同步功能

详细配置请参阅 [Emby 集成文档](CODE_WIKI.md#emby-集成)。

### Q: 演员头像无法显示？

**A**:
- 检查网络连接
- 确认图片 URL 有效
- 检查 Emby/Jellyfin 服务器的媒体路径配置

### Q: 演员简介不更新？

**A**:
- 检查 TMDB API 连接
- 确认演员有对应的 TMDB ID
- 手动触发同步

## 错误和异常

### Q: 出现 "Permission denied" 错误？

**A**:
- 检查文件权限
- 以管理员权限运行（Windows）或使用 sudo（Linux）
- 确保文件未被其他程序占用

### Q: 出现 "Connection timeout" 错误？

**A**:
- 检查网络连接
- 确认防火墙设置
- 尝试使用代理

### Q: 程序崩溃或无响应？

**A**:
1. 查看错误日志（通常在程序目录的 logs 文件夹）
2. 尝试重启程序
3. 检查是否有足够的系统资源
4. 更新到最新版本

### Q: 如何查看详细错误信息？

**A**:
- 控制台输出包含错误详情
- 查看日志文件
- 以调试模式运行（如有）

## 更新和维护

### Q: 如何更新到最新版本？

**A**:
```bash
git pull origin master
pip install -r requirements.txt --upgrade
```

### Q: 更新后配置会丢失吗？

**A**: 配置文件不会丢失，但建议更新前备份。

### Q: 如何回退到旧版本？

**A**:
```bash
git checkout <commit-hash>
```

## 其他问题

### Q: 是否支持多语言？

**A**: 目前主要支持中文和日文，其他语言的支持计划中。

### Q: 可以在手机上使用吗？

**A**: 目前只支持桌面端，移动端版本计划中。

### Q: 数据隐私如何保护？

**A**:
- 所有数据存储在本地
- 不会上传到云端
- TMDB API 请求遵循 TMDB 的隐私政策

### Q: 如何参与项目贡献？

**A**: 欢迎！请参阅 [贡献指南](CONTRIBUTING.md)。

### Q: 如何联系开发者？

**A**:
- GitHub Issues: https://github.com/cdlongbow/mdcx/issues
- 提交问题时请提供：
  - 操作系统版本
  - Python 版本
  - 错误信息或日志
  - 重现步骤

## 仍未解决？

如果以上 FAQ 未能解决你的问题，请：

1. 查看 [用户手册](USER_GUIDE.md)
2. 阅读详细文档 [Code Wiki](CODE_WIKI.md)
3. 搜索 [GitHub Issues](https://github.com/cdlongbow/mdcx/issues)
4. 提交新的 Issue，详细描述你的问题
