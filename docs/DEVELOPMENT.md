# 开发指南

本文档面向 MDCX 的开发者，介绍开发环境搭建、代码规范、开发流程和最佳实践。

## 目录

1. [开发环境搭建](#开发环境搭建)
2. [项目结构](#项目结构)
3. [开发流程](#开发流程)
4. [代码规范](#代码规范)
5. [测试](#测试)
6. [提交规范](#提交规范)
7. [发布流程](#发布流程)

## 开发环境搭建

### 系统要求

- Python 3.8+
- Git
- 文本编辑器（推荐 VSCode 或 PyCharm）

### 环境配置

1. **克隆仓库**
   ```bash
   git clone https://github.com/cdlongbow/mdcx.git
   cd mdcx
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv

   # 激活虚拟环境
   # Windows
   venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

3. **安装开发依赖**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **配置开发工具**
   - 安装 Python 扩展（VSCode）
   - 配置代码格式化工具（black、isort）
   - 配置代码检查工具（flake8、pylint）

### IDE 配置

推荐使用 VSCode，配置建议：

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

## 项目结构

```
mdcx/
├── mdcx/                    # 主程序目录
│   ├── core/               # 核心模块
│   │   ├── tmdb_actor.py   # TMDB 演员数据刮削
│   │   ├── tmdb_movie.py   # TMDB 电影数据刮削
│   │   └── ...
│   ├── gui/                # GUI 模块
│   ├── utils/              # 工具函数
│   └── __init__.py
├── resources/              # 资源文件
│   └── userdata/          # 用户数据
│       └── actor_database.xlsx
├── docs/                   # 文档目录
├── tests/                  # 测试目录
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
├── README.md              # 项目说明
├── CODE_WIKI.md           # 技术文档
└── main.py               # 程序入口
```

详细架构说明请参阅 [架构设计文档](architecture.md)。

## 开发流程

### 分支策略

- `master` - 主分支，稳定版本
- `develop` - 开发分支
- `feature/*` - 功能分支
- `fix/*` - 修复分支
- `hotfix/*` - 紧急修复分支

### 开发流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **编写代码**
   - 遵循代码规范
   - 添加必要的注释
   - 编写测试

3. **本地测试**
   ```bash
   # 运行测试
   pytest

   # 代码检查
   flake8 mdcx/
   black mdcx/
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

5. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **代码审查**
   - 等待代码审查
   - 根据反馈修改代码

7. **合并到主分支**
   - 通过审查后合并
   - 删除功能分支

## 代码规范

### Python 代码规范

遵循 PEP 8 规范：

```python
# 好的命名
def get_actor_name(actor_id: int) -> str:
    """获取演员名称"""
    pass

class ActorManager:
    """演员管理器"""
    pass

# 不好的命名
def get_name(id):
    pass

class manager:
    pass
```

### 导入规范

```python
# 标准库导入
import os
import sys
from typing import Optional

# 第三方库导入
import requests
from openpyxl import Workbook

# 本地导入
from mdcx.core.tmdb_actor import TmdbActor
```

### 注释规范

```python
def batch_update_actors(actors: list[dict], batch_size: int = 10) -> None:
    """
    批量更新演员信息

    Args:
        actors: 演员列表
        batch_size: 批次大小，默认 10

    Returns:
        None

    Raises:
        ValueError: 当 actors 为空时
    """
    if not actors:
        raise ValueError("演员列表不能为空")

    # 实现代码...
```

### 类型提示

使用类型提示提高代码可读性：

```python
from typing import List, Dict, Optional

def search_actors(query: str, limit: int = 10) -> List[Dict]:
    """搜索演员"""
    pass

def get_actor(id: int) -> Optional[Dict]:
    """获取演员信息，不存在时返回 None"""
    pass
```

### 错误处理

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"请求失败: {e}")
    raise
```

## 测试

### 测试框架

使用 pytest 作为测试框架：

```bash
# 安装 pytest
pip install pytest pytest-cov

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_tmdb_actor.py

# 生成覆盖率报告
pytest --cov=mdcx --cov-report=html
```

### 测试示例

```python
import pytest
from mdcx.core.tmdb_actor import TmdbActor

def test_search_actor():
    """测试演员搜索"""
    actor = TmdbActor("test_api_key")
    result = actor.search("松下纱荣子")
    assert result is not None
    assert "松下纱荣子" in result or "松下紗栄子" in result

def test_rate_limit():
    """测试限速"""
    actor = TmdbActor("test_api_key")
    assert actor._rate_limiter.rate == 3.5
```

详细测试说明请参阅 [测试文档](docs/TEST_COVERAGE_SUMMARY.md)。

## 提交规范

### 提交信息格式

使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式（不影响代码运行）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例：**

```
feat(tmdb): 添加令牌桶限流器

实现基于令牌桶的限流器，控制 TMDB API 请求速率，
避免触发 API 限流。

Closes #123
```

### 提交前检查

提交前请确保：

1. 代码通过所有测试
2. 代码通过代码检查（flake8）
3. 代码格式正确（black）
4. 更新了相关文档
5. 编写了测试用例

## 发布流程

### 版本号规范

使用语义化版本（Semantic Versioning）：

- `MAJOR.MINOR.PATCH`
  - MAJOR: 不兼容的 API 变更
  - MINOR: 向后兼容的功能性新增
  - PATCH: 向后兼容的问题修复

### 发布步骤

1. **更新版本号**
   ```bash
   # 更新版本号（例如 v1.2.3）
   git tag -a v1.2.3 -m "Release v1.2.3"
   ```

2. **更新 CHANGELOG**
   - 添加新版本的变更记录
   - 列出所有新增功能、修复和改进

3. **创建发布包**
   ```bash
   python setup.py sdist bdist_wheel
   ```

4. **推送到 PyPI（如果适用）**
   ```bash
   twine upload dist/*
   ```

5. **发布 GitHub Release**
   - 在 GitHub 创建 Release
   - 关联对应的 tag
   - 添加发布说明

## 文档

### 文档更新

代码变更时同步更新文档：

- API 变更 → 更新 [API 文档](api-documentation.md)
- 新功能 → 更新 [用户手册](USER_GUIDE.md)
- 架构变更 → 更新 [架构文档](architecture.md)
- 配置变更 → 更新 [配置说明](configuration.md)

### 文档位置

- 用户文档：README.md、USER_GUIDE.md、FAQ.md、INSTALL.md
- 开发文档：DEVELOPMENT.md、CODE_WIKI.md、docs/
- API 文档：docs/api-documentation.md

## 代码审查

### 审查检查清单

使用 [代码审查检查清单](docs/CODE_REVIEW_CHECKLIST.md) 确保代码质量。

### 审查要点

- 功能是否正确实现
- 代码是否遵循规范
- 是否有足够的测试
- 是否有性能问题
- 是否有安全隐患

详细说明请参阅 [代码审查指南](docs/CODE_REVIEW_GUIDE.md)。

## 性能优化

### 性能考虑

- 减少不必要的网络请求
- 使用缓存机制
- 优化数据库查询
- 控制并发数量

### 性能分析

```python
import cProfile

def profile_function():
    cProfile.run('your_function()')
```

## 安全性

### 安全最佳实践

- 不硬编码敏感信息（API Key、密码）
- 使用环境变量管理配置
- 验证用户输入
- 使用 HTTPS
- 定期更新依赖

### 敏感信息管理

```python
# 好的做法
import os
API_KEY = os.getenv('TMDB_API_KEY')

# 不好的做法
API_KEY = 'your_api_key_here'
```

## 调试技巧

### 日志记录

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 断点调试

使用 IDE 的调试功能或 pdb：

```python
import pdb; pdb.set_trace()
```

## 参与贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

详细贡献指南请参阅 [贡献指南](CONTRIBUTING.md)。

## 相关文档

- [架构设计](architecture.md)
- [核心模块](core-modules.md)
- [API 文档](api-documentation.md)
- [代码规范](docs/CODE_REVIEW_STANDARDS.md)
- [测试指南](docs/TEST_COVERAGE_SUMMARY.md)
- [迁移指南](crawler-migration.md)

## 联系方式

如有问题，请：
- 提交 GitHub Issue
- 查看 [FAQ](FAQ.md)
- 阅读其他文档

---

感谢你对 MDCX 项目的贡献！