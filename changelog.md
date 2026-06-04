## 新增
- 新增 libredmm 刮削源
- 新增 Amazon ASIN 缓存功能。
  - 添加 openpyxl 依赖，默认在运行目录生成amazon_asin_database.xlsx
  - 实现缓存查询功能，避免重复搜索
  - 添加去重逻辑，保护高置信度数据

## 修改
- Amazon高清封面poster为1500尺寸。
- 精简 ASIN 数据库列，移除冗余字段（记录时间、匹配类型、置信度、媒体类型、备注）。
- 修复封面 URL 始终为空的问题，调用处传入实际 Amazon 图片 URL。
- ASIN 数据库文件迁移至 resources/userdata/，与 mapping/watermark 同目录管理。
