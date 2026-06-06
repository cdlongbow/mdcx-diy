## 新增
- 新增 libredmm 刮削源
- 新增 Amazon ASIN 缓存功能。
  - 添加 openpyxl 依赖，默认在运行目录生成 amazon_asin_database.xlsx
  - 实现缓存查询功能，避免重复搜索
  - 添加去重逻辑，保护高置信度数据
- 新增 NFO 演员 TMDB ID 功能。
  - 网络设置栏新增 TMDB API 地址（默认 api.tmdb.org）和 API Key 输入
  - NFO 设置栏新增"为演员写入 TMDB ID"选项，勾选后在 <actor> 下增加 <tmdbid> 子字段
  - 直接用日文原名搜索 TMDB API，过滤日本出生地 + 女性/未指定性别 + 精确名匹配
  - 多候选时按 popularity 排序取最优，失败不阻塞刮削
- 数据源统一迁移至 xlsx。
  - actor_mapping XML + TMDB 缓存合并为统一 actor_database.xlsx
  - mapping_info.xml 转为 info_database.xlsx
  - 删除废弃的 actor_tmdbid.xlsx，TMDB ID 数据已整合进 actor_database.xlsx
  - 内置 xlsx 数据库，支持表头冻结，提升数据管理效率

## 修改
- Amazon 高清封面 poster 为 1500 尺寸。
- 精简 ASIN 数据库列，移除冗余字段（记录时间、匹配类型、置信度、媒体类型、备注）。
- 修复封面 URL 始终为空的问题，调用处传入实际 Amazon 图片 URL。
- 修复读取模式下缺少 aiohttp 依赖导致 NameError 崩溃的问题，改为优雅降级。
- 修复 info_database.xlsx 优先级标记缺失，恢复 tag_priority 标签排序功能。
- 清理废弃 XML 文件（actor_mapping_fixed.xml 等）及死代码。
- 更新 UI 文案和路径指向 xlsx 数据库。
- 修正 .gitignore 规则，内置 xlsx 文件正确追踪。