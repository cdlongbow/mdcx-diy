# 常见问题解答 (FAQ)

## 安装和运行

### Q: 安装时提示 "No module named 'PyQt6'" 怎么办？

**A**: 手动安装：

```bash
pip install PyQt6
```

### Q: Linux 上界面显示不出来或者花屏？

**A**: 缺系统图形库：

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# CentOS/RHEL
sudo yum install libxcb-xinerama0 libxcb-cursor0

export QT_QPA_PLATFORM=xcb
```

### Q: 我怎么知道自己的 Python 版本够不够？

**A**:

```bash
python --version
```

如果版本低于 3.13，需要先升级 Python。

### Q: macOS 上提示 "Python is not installed"？

**A**: 用 Homebrew 安装：

```bash
brew install python@3.13
```

## 数据库管理

### Q: 数据库文件放在哪里？

**A**: 在 `userdata/actor_database.xlsx`（程序主目录下）。

### Q: 怎么备份数据库？

**A**: 把 `actor_database.xlsx` 复制到别处保存。建议同时备份 `amazon_asin_database.xlsx`。

### Q: 数据库坏了怎么办？

**A**: 有备份就用备份恢复。没有备份试试 Excel 自带的修复功能。

### Q: 支持其他格式的数据库吗？

**A**: 目前只支持 Excel (.xlsx) 格式。

### Q: 不小心删了演员数据，还能找回来吗？

**A**: 有备份就能恢复。操作前记得备份。

## TMDB 数据刮削

### Q: 怎么拿到 TMDB API Key？

**A**:
1. 打开 https://www.themoviedb.org/
2. 注册账号
3. 进设置页面申请 API Key
4. 把 Key 填到程序设置里

### Q: 刮削时老是出现 429 错误？

**A**: 请求太快。解决：
- 并发数调低（建议改成 3）
- 开启限流（默认每秒 3.5 次）
- 等一会儿再试

### Q: 批量刮削速度太慢？

**A**: 适当提高 TMDB 请求频率和并发数（注意别超限），确保网络稳定。

### Q: TMDB 找不到某个演员？

**A**: 换几种搜法：
- 用日文名搜
- 用别名搜
- 检查名字是否正确
- 手动去 TMDB 网站确认
- 也可能该演员不在 TMDB 中

### Q: TMDB 上的数据不准？

**A**: TMDB 数据是用户贡献的。可以在 TMDB 网站提交更正，或手动修改本地数据库。

## 翻译

### Q: Bing 翻译和 Google 翻译有什么区别？

**A**: Bing 翻译与 Google 翻译一样免费免配置，无需注册 API Key，自动爬取微软翻译接口。两者都支持中/英/日互译。Bing 适合在国内网络环境下作为 Google 的替代方案。

### Q: 如何切换翻译引擎？

**A**: 在"翻译设置"页面选择目标引擎，然后保存配置即可即时生效。各引擎特点：Google/Bing 免费免配置；百度/DeepL/LLM 需要自行申请 API Key。

## 配置和设置

### Q: 配置文件在哪里？

**A**: 默认在程序主目录下的 `config.json`。程序通过 `MDCx.config` 标记文件记录配置文件路径，运行时可切换。

### Q: 怎么恢复默认设置？

**A**: 关掉程序，删掉配置文件，重启程序会自动生成默认配置。

### Q: 改完配置需要重启吗？

**A**: 大部分配置即时生效，少数需要重启。

## 性能和优化

### Q: 程序跑起来很慢怎么办？

**A**:
- 关掉没用的后台程序
- 增加内存
- 清理数据库，删除无用条目
- 更新到最新版本

### Q: 内存占用太高？

**A**:
- 减少并发刮削数量
- 定期清理缓存
- 重启程序释放内存

### Q: 数据库文件太大？

**A**: 用格式化功能清理无效数据，删除不需要的演员信息。

## Emby/Jellyfin 集成

### Q: 怎么配置 Emby/Jellyfin？

**A**: 在程序设置中填写服务器地址和 API Key，开启自动同步。详细说明见[Emby 集成文档](CODE_WIKI.md#emby-集成)。

### Q: 演员头像显示不出来？

**A**: 检查网络连接、图片链接是否有效、Emby/Jellyfin 服务器的媒体路径配置。

### Q: 演员简介不更新？

**A**: 检查 TMDB API 连接、演员是否有 TMDB ID，或手动触发同步。

## 错误和异常

### Q: 出现 "Permission denied" 错误？

**A**: 权限不够。Windows 上用管理员权限运行，Linux/macOS 加 `sudo`，确认文件未被其他程序占用。

### Q: 出现 "Connection timeout" 错误？

**A**: 连接超时。检查网络、防火墙，或使用代理。

### Q: 程序崩溃或没反应？

**A**:
1. 查看日志文件（程序目录下的 logs 文件夹）
2. 重启程序
3. 检查内存和 CPU
4. 更新到最新版本

### Q: 怎么看详细的错误信息？

**A**: 命令行运行程序看终端输出，或直接看日志文件。

## 更新和维护

### Q: 怎么更新到最新版本？

**A**:

```bash
git pull origin main
uv sync --all-extras --dev
```

### Q: 更新后配置会丢吗？

**A**: 一般不会。但更新前最好备份配置文件。

### Q: 怎么回退到旧版本？

**A**:

```bash
git checkout <commit-hash>
```

## 其他问题

### Q: 我的数据安全吗？

**A**: 所有数据存在本地，不会上传云端。TMDB 查询遵循 TMDB 隐私政策。

### Q: 怎么参与项目？

**A**: 阅读[贡献指南](CONTRIBUTING.md)。

### Q: 怎么联系开发者？

**A**: 去 GitHub Issues 提交：https://github.com/cdlongbow/mdcx/issues

提交时附上：
- 操作系统版本
- Python 版本
- 错误信息或日志
- 复现步骤

## 还没解决？

- 查看[用户手册](USER_GUIDE.md)
- 阅读[Code Wiki](CODE_WIKI.md)
- 搜索[GitHub Issues](https://github.com/cdlongbow/mdcx/issues)
- 提交新的 Issue