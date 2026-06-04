## 新增
- 新增 libredmm 刮削源
- 新增 Amazon ASIN 缓存功能。
  - 添加 openpyxl 依赖，默认在运行目录生成amazon_asin_database.xlsx
  - 实现缓存查询功能，避免重复搜索
  - 添加去重逻辑，保护高置信度数据
- 新增 NFO 演员 TMDB ID 功能。
  - 网络设置栏新增 TMDB API 地址（默认 api.tmdb.org）和 API Key 输入
  - NFO 设置栏新增"为演员写入 TMDB ID"选项，勾选后在 <actor> 下增加 <tmdbid> 子字段
  - 直接用日文原名搜索 TMDB API，过滤日本出生地 + 女性/未指定性别 + 精确名匹配
  - 多候选时按 popularity 排序取最优，失败不阻塞刮削
  - 查询结果缓存至 actor_tmdbid.xlsx（演员名、tmdbid、tmdb url 超链接），可排序可复用

## 修改
- Amazon高清封面poster为1500尺寸。
- 精简 ASIN 数据库列，移除冗余字段（记录时间、匹配类型、置信度、媒体类型、备注）。
- 修复封面 URL 始终为空的问题，调用处传入实际 Amazon 图片 URL。
