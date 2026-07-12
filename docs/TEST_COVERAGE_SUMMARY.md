# 测试覆盖率摘要

## 测试框架

- **测试框架**：pytest
- **覆盖率工具**：pytest-cov
- **测试目录**：`tests/`

## 运行测试

```bash
# 运行所有测试
uv run pytest tests/

# 运行测试并生成覆盖率报告
uv run pytest tests/ --cov=mdcx --cov-report=html

# 运行测试并生成覆盖率摘要
uv run pytest tests/ --cov=mdcx --cov-report=term-missing
```

## 测试覆盖范围

### 当前测试状态

| 类型 | 数量 |
|------|------|
| 测试文件 | 72 个（`tests/` 下，含 `tests/core/`、`tests/crawlers/` 子目录） |
| 测试用例 | 474 个 |
| 执行方式 | `pytest`（预提交钩子 / CI 自动执行） |
| 检查项 | `ruff format --check` + `ruff check` + `pytest`（即 `uv run check`） |

### 测试文件分布

```
tests/
├── core/                     # 核心模块测试（6 个文件，108 个用例）
│   ├── test_face_crop.py         # OpenCV 人脸裁剪
│   ├── test_media_resource.py    # 媒体资源解析
│   ├── test_mosaic.py            # 有码/无码识别
│   ├── test_name_flags.py        # 命名标志位
│   ├── test_naming_template.py   # Jinja2 命名模板渲染
│   └── test_web_amazon.py        # Amazon 封面/ASIN 查询
├── crawlers/                 # 爬虫测试（33 个文件，111 个用例）
│   ├── test_crawler.py           # 新版框架基类/注册表
│   ├── test_compat.py            # 新旧框架兼容
│   ├── test_parsers.py           # 详情页解析 helper
│   └── test_<site>.py            # 各站点爬虫（dmm/javdb/javbus/fc2*/missav/...）
└── *.py                      # 顶层测试（33 个文件，255 个用例）
    ├── test_tmdb_actor.py        # TMDB 演员查询、xlsx 读写、LibreDMM 链接补全
    ├── test_mapping_resources.py # 映射表资源查询
    ├── test_nfo_*.py             # NFO 读写、转义、标签优先级、演员 tmdbid、外部 ID
    ├── test_config_*.py          # 配置读取与转换、网络设置
    ├── test_network_*.py         # 网络检查、指纹、生命周期、CF Bypass
    ├── test_web_*.py             # 异步网络层、限流、URL 清洗、CF Bypass
    ├── test_amazon_database.py   # Amazon ASIN 数据库读写
    ├── test_subtitle_file_index.py
    ├── test_build.py             # 构建脚本
    └── test_regression_fixes.py  # 回归修复
```

> 说明：上述为按目录的归类统计，实际文件数以仓库 `tests/` 目录为准。

### 覆盖的核心功能

| 模块 | 测试内容 |
|------|---------|
| `tmdb_actor.py` | TMDB ID 查询、Excel 读写、中文繁简归一化、候选排序、反查缓存、LibreDMM 链接补全 |
| `naming`（模板） | Jinja2 命名渲染、字段截断、文件名清理 |
| `amazon.py` / `amazon_database.py` | ASIN 查询、Excel 持久化、条码/标题/演员搜索策略 |
| `mapping_resources.py` | 演员/制作商/标签映射表的加载和查询 |
| `nfo.py` | NFO 读写、转义、标签优先级、演员 tmdbid 标签、外部 ID 标签 |
| `crawlers/*` | 各站点新版爬虫的搜索/详情解析与框架兼容 |
| `config` / `network` | 配置加载转换、网络层、限流、CF Bypass |

## 测试策略

### 单元测试

- 测试单个函数或类的功能
- 使用 Mock 隔离外部依赖
- 覆盖正常路径和异常路径

### 集成测试

- 测试多个模块协作
- 测试完整刮削流程
- 使用真实网络请求（可配置）

### 测试覆盖率目标

- **整体目标**：80%
- **核心模块**：90%
- **爬虫模块**：70%

## 测试最佳实践

1. **独立性**：每个测试独立运行
2. **可读性**：测试名称清晰表达测试意图
3. **可维护性**：使用测试辅助工具和 fixture
4. **快速反馈**：单元测试快速执行（当前 474 个测试随 CI 自动运行）

## 预提交自检

每次提交/推送前自动运行（逻辑位于 `scripts/check.py`，等价于 `uv run check`）：

```bash
ruff format --check
ruff check
uv run pytest tests/
```

全部通过后方可推送。CI 同时配置 `pre-commit` 钩子执行 `ruff check` 与 `ruff format`。

## CI/CD 集成

测试自动运行：

- 提交 Pull Request
- 合并到主分支
- 创建 Release

## 相关文档

- [架构设计](architecture.md)
- [核心模块](core-modules.md)
