# 用户指令记忆

本文件记录了用户的指令、偏好和教导，用于在未来的交互中提供参考。

## 格式

### 用户指令条目
用户指令条目应遵循以下格式：

[用户指令摘要]
- Date: [YYYY-MM-DD]
- Context: [提及的场景或时间]
- Instructions:
  - [用户教导或指示的内容，逐行描述]

### 项目知识条目
Agent 在任务执行过程中发现的条目应遵循以下格式：

[项目知识摘要]
- Date: [YYYY-MM-DD]
- Context: Agent 在执行 [具体任务描述] 时发现
- Category: [运维部署|构建方法|测试方法|排错调试|工作流协作|环境配置]
- Instructions:
  - [具体的知识点，逐行描述]

## 去重策略
- 添加新条目前，检查是否存在相似或相同的指令
- 若发现重复，跳过新条目或与已有条目合并
- 合并时，更新上下文或日期信息
- 这有助于避免冗余条目，保持记忆文件整洁

## 条目

[面向小白的细致指导风格]
- Date: 2026-06-08
- Context: 用户希望我以编程能手、审核、修改和补全代码专家的方式长期协作
- Instructions:
  - 默认从全方位、多角度、深层次的角度审查和改进代码。
  - 面向小白解释问题，给出细致、可执行、易落地的建议。
  - 在发现风险、缺陷、遗漏时主动指出，并尽量给出修复方案和进行验证。

[优先自动执行本地检查]
- Date: 2026-06-09
- Context: 用户希望尽量自动执行，减少手动命令操作
- Instructions:
- 优先把重复性的本地检查配置为自动执行。
- 对推送前校验这类工作流，优先提供自动拦截方案，减少手动步骤。

[提交前必须运行 ruff format + ruff check + pytest]
- Date: 2026-07-17
- Context: 多次 CI 因测试失败报错，用户要求在推送前自动运行测试
- Category: 工作流协作
- Instructions:
- 每次修改 Python 代码后、提交前，必须运行 `ruff format` 和 `ruff check --fix`，确认通过后再提交推送。
- 推送前必须运行 `pytest tests/ --tb=short -m "not network" -x` 确保无回归。
- 项目有 `.pre-commit-config.yaml` 配置了 ruff 和 pytest 钩子，MonkeyCode 沙箱环境不持久化 git hooks，每次新会话开始时必须先执行 `pre-commit install` 安装钩子，然后再手动执行上述检查。
- 项目有 `.githooks/pre-push` 推送前自检脚本（运行 `uv run check`），每次新会话开始时必须先执行 `git config core.hooksPath .githooks` 启用它，否则推送不会触发自检。
- 不要依赖 CI 来发现问题，本地先拦截。

[每次新会话自动安装 pre-commit 钩子]
- Date: 2026-07-17
- Context: 用户希望每次新会话开始时自动安装 pre-commit 钩子，无需手动执行
- Instructions:
  - 每次新会话开始时，自动执行 `pre-commit install` 命令安装 git hooks。
  - 如果 pre-commit 工具未安装，先执行 `pip install pre-commit --break-system-packages` 安装。
  - 安装完成后确认 `.git/hooks/pre-commit` 文件存在且可执行。

[环境 Python 版本升级到 >= 3.13.4]
- Date: 2026-07-17
- Context: 项目要求 Python >= 3.13.4（使用 type parameter defaults 语法），但沙箱环境默认只有 Python 3.11，导致无法运行测试和导入项目。
- Category: 环境配置
- Instructions:
  - 项目只能 `uv run` 执行测试（`pytest tests/ --tb=short -m "not network"`），因为 sandbox 默认 python3 是 3.11，无法解析 3.12+ 的 `class Rename[TRaw = str, TNew = TRaw]` 语法。
  - Python 3.13.14 已安装到 `/opt/python3.13`，`uv` 已安装到 `/usr/local/bin/uv`。
  - 每次新会话开始时，检查 `/opt/python3.13` 是否存在：
    - 若存在，直接使用 `uv run pytest` 跑测试。
    - 若不存在，需要下载并安装：从 `https://github.com/astral-sh/python-build-standalone` 下载最新 `cpython-3.13.x-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz`，解压到 `/opt/python3.13`，创建 `/usr/local/bin/uv` 和 `/usr/local/bin/python3.13` 软链接，然后执行 `uv sync` 安装项目依赖。
  - 依赖安装后可以运行 `uv run pytest tests/ --tb=short -m "not network"` 验证。

[Windows exe 打包依赖约束]
- Date: 2026-06-21
- Context: 用户提醒后续修改需兼容 Windows 打包发布场景
- Category: 环境配置
- Instructions:
  - 代码变更优先使用 Python 标准库，不主动引入新三方依赖。
  - 新增文件持久化路径应使用 `resources`/`userdata` 现有目录习惯，避免新增外部库。
  - 变更涉及打包入口或运行时依赖时，先确认打包脚本与 PyInstaller 打包配置仍能在 Windows 下正常启动。
