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

### 已测试的模块

| 模块 | 文件 | 覆盖率 | 状态 |
|------|------|--------|------|
| 核心模块 | `tests/core/` | 待统计 | 待完成 |
| 爬虫 | `tests/crawlers/` | 待统计 | 待完成 |
| 工具 | `tests/utils/` | 待统计 | 待完成 |
| 模型 | `tests/test_*.py` | 待统计 | 待完成 |

### 测试文件列表

```
tests/
├── conftest.py              # 测试配置
├── random_generator.py      # 随机数据生成器
├── core/                    # 核心模块测试
│   ├── test_scraper.py      # 刮削器测试
│   ├── test_file_crawler.py # 文件爬虫测试
│   ├── test_nfo.py          # NFO 生成测试
│   └── test_tmdb_actor.py   # TMDB 演员测试
├── crawlers/                # 爬虫测试
│   ├── test_base_crawler.py # 基础爬虫测试
│   ├── test_javbus.py       # JavBus 爬虫测试
│   └── ...
└── utils/                   # 工具测试
    ├── test_path.py         # 路径工具测试
    └── test_language.py     # 语言工具测试
```

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
4. **快速反馈**：单元测试应该快速执行

## CI/CD 集成

测试会在以下情况下自动运行：

- 提交 Pull Request
- 合并到主分支
- 创建 Release

## 相关文档

- [架构设计](architecture.md) - 系统架构
- [核心模块](core-modules.md) - 核心模块说明
