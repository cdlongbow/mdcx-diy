# 常见问题解答 (FAQ)

这里收集了使用 MDCX 时常见的问题和解决方法。

## 安装和运行

### Q: 安装时提示 "No module named 'PyQt6'" 怎么办？

**A**: 程序界面要用 PyQt6。手动装一下就行：

```bash
pip install PyQt6
```

### Q: Linux 上界面显示不出来或者花屏？

**A**: 缺了系统图形库。装一下就好了：

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# CentOS/RHEL
sudo yum install libxcb-xinerama0 libxcb-cursor0

# 设置环境变量
export QT_QPA_PLATFORM=xcb
```

### Q: 我怎么知道自己的 Python 版本够不够？

**A**: 运行这条命令查看：

```bash
python --version
```

如果版本低于 3.13，需要先升级 Python。

### Q: macOS 上提示 "Python is not installed"？

**A**: macOS 自带的 Python 版本可能不够。用 Homebrew 装一个：

```bash
brew install python@3.13
```

## 数据库管理

### Q: 数据库文件放在哪里？

**A**: 所有系统都一样，在 `userdata/actor_database.xlsx`。

### Q: 怎么备份数据库？

**A**: 直接把 `actor_database.xlsx` 文件复制到别的地方存起来。建议顺便把 `amazon_asin_database.xlsx` 也一起备份。

### Q: 数据库坏了怎么办？

**A**: 如果有备份，用备份恢复。没有备份的话，试试用 Excel 自带的修复功能。还不行就找开发者帮忙。

### Q: 支持其他格式的数据库吗？

**A**: 目前只支持 Excel (.xlsx) 格式。以后可能会支持 CSV 和 SQLite。

### Q: 不小心删了演员数据，还能找回来吗？

**A**: 删之前有备份就能恢复。没备份就找不回来了，所以操作前记得备份。

## TMDB 数据刮削

### Q: 怎么拿到 TMDB API Key？

**A**: 去 TMDB 网站申请：
1. 打开 https://www.themoviedb.org/
2. 注册一个账号
3. 进设置页面申请 API Key
4. 把申请到的 Key 填到程序设置里

### Q: 刮削时老是出现 429 错误？

**A**: 这是 TMDB 在告诉你"请求太快了"。解决方法：
- 把并发数调低（建议改成 3）
- 开启限流（默认每秒 3.5 次）
- 等一会儿再试

### Q: 批量刮削速度太慢？

**A**: 可以试试：
- 适当提高 TMDB 的请求频率（注意别超限）
- 稍微提高并发数（别太高）
- 确保网络稳定

### Q: TMDB 找不到某个演员？

**A**: 换几种搜法试试：
- 用日文名搜
- 用别名搜
- 检查名字有没有写对
- 手动去 TMDB 网站上搜一下确认
- 也可能是这个演员本来就不在 TMDB 里

### Q: TMDB 上的数据不准？

**A**: TMDB 的数据是用户贡献的，难免有错。你可以在 TMDB 网站上提交更正，或者自己手动修改数据库。

## 配置和设置

### Q: 配置文件在哪里？

**A**: 位置看你的系统：
- Windows: `%APPDATA%/mdcx/config.json`
- Linux: `~/.config/mdcx/config.json`
- macOS: `~/Library/Application Support/mdcx/config.json`

注：旧版本（V1）用的是 `config.ini`，新版本（V2）已经换成 `config.json`。

### Q: 怎么恢复默认设置？

**A**: 关掉程序，把配置文件删掉，再重新启动程序。程序会自动用默认配置重新生成。

### Q: 改完配置需要重启吗？

**A**: 大部分配置改了之后马上生效。少数几个可能需要重启才能生效。

## 性能和优化

### Q: 程序跑起来很慢怎么办？

**A**: 试试这几招：
- 关掉没用的后台程序
- 增加电脑内存
- 清理数据库，删掉不需要的条目
- 更新到最新版本

### Q: 内存占用太高？

**A**: 试试：
- 减少并发刮削的数量
- 定期清理缓存
- 重启一下程序释放内存

### Q: 数据库文件太大？

**A**: 用格式化功能清理无效数据，删掉不需要的演员信息。

## Emby/Jellyfin 集成

### Q: 怎么配置 Emby/Jellyfin？

**A**: 在程序设置里填上 Emby/Jellyfin 的服务器地址和 API Key，然后开启自动同步。详细说明请看[Emby 集成文档](CODE_WIKI.md#emby-集成)。

### Q: 演员头像显示不出来？

**A**: 检查这几样：
- 网络连接是否正常
- 图片链接是否有效
- Emby/Jellyfin 服务器的媒体路径配置是否正确

### Q: 演员简介不更新？

**A**: 检查 TMDB API 是否正常连接，确认这个演员有没有 TMDB ID，或者手动触发一次同步试试。

## 错误和异常

### Q: 出现 "Permission denied" 错误？

**A**: 意思是权限不够。试试：
- Windows 上用管理员权限运行
- Linux/macOS 上加上 `sudo`
- 确认文件没有被其他程序占用

### Q: 出现 "Connection timeout" 错误？

**A**: 意思是连接超时。检查网络连接是否正常，防火墙有没有拦住程序，或者试试用代理。

### Q: 程序崩溃或没反应？

**A**: 先别急：
1. 看看日志文件（一般在程序目录下的 logs 文件夹）
2. 重启程序试试
3. 检查电脑内存和 CPU 够不够
4. 更新到最新版本

### Q: 怎么看详细的错误信息？

**A**: 打开命令行终端运行程序，看终端里的输出。或者直接看日志文件。

## 更新和维护

### Q: 怎么更新到最新版本？

**A**: 运行这两条命令：

```bash
git pull origin master
uv sync --all-extras --dev
```

### Q: 更新后配置会丢吗？

**A**: 一般不会丢失。但保险起见，更新前最好备份一下配置文件。

### Q: 怎么回退到旧版本？

**A**: 用这条命令回到指定的版本：

```bash
git checkout <commit-hash>
```

## 其他问题

### Q: 支持多语言吗？

**A**: 目前主要支持中文和日文。其他语言还在计划中。

### Q: 手机上能用吗？

**A**: 目前只支持电脑端。手机版还在计划中。

### Q: 我的数据安全吗？

**A**: 所有数据都存在你本地电脑上，不会上传到云端。TMDB 的查询请求遵循 TMDB 的隐私政策。

### Q: 怎么参与项目？

**A**: 欢迎贡献！请阅读[贡献指南](CONTRIBUTING.md)。

### Q: 怎么联系开发者？

**A**: 去 GitHub Issues 页面提交问题：https://github.com/cdlongbow/mdcx/issues

提交时请附上：
- 操作系统版本
- Python 版本
- 错误信息或日志
- 你是怎么操作导致出错的

## 还没解决？

如果上面的回答没能帮到你，试试：
1. 查看[用户手册](USER_GUIDE.md)
2. 阅读详细文档[Code Wiki](CODE_WIKI.md)
3. 搜索[GitHub Issues](https://github.com/cdlongbow/mdcx/issues)看看别人有没有遇到过
4. 提交新的 Issue，详细描述你的问题