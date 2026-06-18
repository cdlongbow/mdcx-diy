# 测试覆盖率摘要

本文档提供 MDCx 测试覆盖率的概述。

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
| 测试文件 | 7 个 |
| 测试用例 | 43 个 |
| 执行方式 | `pytest`（CI 预提交钩子自动执行） |
| 检查项 | `ruff format --check` + `ruff check` + `pytest` |

### 测试文件列表

```
tests/
├── conftest.py                     # 测试配置与 Mock 常量
├── test_tmdb_actor.py              # TMDB 演员查询、xlsx 读写、LibreDMM 链接补全（25 个测试）
├── test_mapping_resources.py       # 映射表资源查询（4 个测试）
├── test_nfo_read.py                # NFO 读取解析（4 个测试）
├── test_nfo_write_escape.py        # NFO 写入转义（2 个测试）
├── test_nfo_tag_priority.py        # NFO 标签优先级（3 个测试）
├── test_nfo_actor_tmdbid.py        # NFO 演员 TMDB ID 标签（3 个测试）
└── test_nfo_external_id_tag.py     # NFO 外部 ID 标签（2 个测试）
```

### 覆盖的核心模块逻辑

| 模块 | 覆盖内容 |
|------|---------|
| `tmdb_actor.py` | 演员 TMDB ID 查询、xlsx 读写、中文繁简归一化、候选排序、反查缓存、LibreDMM 合并 |
| `mapping_resources.py` | 演员/制作商/标签映射表加载与查询 |
| `nfo.py` | NFO 读取、写入转义、标签优先级、演员 tmdbid 标签、外部 ID 标签 |

## 测试策略

### 单元测试

- 测试单个函数或类的功能
- 使用 Mock 隔离外部依赖
- 覆盖正常路径和异常路径

### 集成测试

- 测试多个模块协作
- 测试完整的刮削流程
- 使用真实的网络请求（可配置）

### 测试覆盖率目标

- **整体目标**：80%
- **核心模块**：90%
- **爬虫模块**：70%

## 测试最佳实践

1. **独立性**：每个测试应该独立运行
2. **可读性**：测试名称应该清晰表达测试意图
3. **可维护性**：使用测试辅助工具和 fixture
4. **快速反馈**：单元测试应该快速执行（当前 43 个测试约 1-2 秒完成）

## 预提交自检

每次 `git push` 前自动运行：

```bash
# 运行于 pre-push 钩子
ruff format --check
ruff check
python3 -m pytest tests/test_tmdb_actor.py tests/test_mapping_resources.py tests/test_nfo_*.py
```

全部通过后方可推送。自检逻辑位于 `scripts/check.py`。

## CI/CD 集成

测试会在以下情况下自动运行：

- 提交 Pull Request
- 合并到主分支
- 创建 Release

## 相关文档

- [架构设计](architecture.md) - 系统架构
- [核心模块](core-modules.md) - 核心模块说明
